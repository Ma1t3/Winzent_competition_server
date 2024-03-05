import csv
import io
import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun
from .competition_logic import create_experiments_for_competition
from .competition_ranking import (
    calculate_competition_results,
    calculate_ranking,
)
from .forms import CompetitionCreationForm
from .models import CompetitionRun
from ..experimentdefinitionmanagement.views import increment_string

logger = logging.getLogger(__name__)


def get_competition_list_context(request):
    """Returns the context for the competition list page."""

    competitions = CompetitionRun.objects.filter(is_public=True)
    if request.user.is_authenticated:
        competitions |= CompetitionRun.objects.filter(owner=request.user)
        competitions = competitions.annotate(
            own_competitions=Case(
                When(owner=request.user, then=1), output_field=IntegerField()
            ),
            running=Case(
                When(status="running", then=1),
                output_field=IntegerField(),
            ),
            attacker_count=Count("attacker"),
            defender_count=Count("defender"),
        ).order_by("running", "own_competitions", "-timestamp_created")
    else:
        competitions = competitions.annotate(
            running=Case(
                When(status="running", then=1),
                output_field=IntegerField(),
            ),
        ).order_by("running", "-timestamp_created")
    context = {"competitions": competitions}
    return context


def show_competition_list(request):
    """Shows the competition list page."""
    context = get_competition_list_context(request)
    return render(request, "competition_list_page.html", context)


def ajax_competition_list(request):
    """Returns the competition list to update the competition list page via ajax."""
    context = get_competition_list_context(request)
    return render(request, "competition_list.html", context)


@login_required
def competition_create(request, competition_id=None):
    """Shows the competition creation page."""
    if request.method == "POST":
        form = CompetitionCreationForm(request.user, request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            erd = form.cleaned_data.get("erd")
            is_public = form.cleaned_data.get("is_public")
            owner = request.user
            competition = CompetitionRun(
                name=name,
                erd=erd,
                owner=owner,
                is_public=is_public,
            )
            competition.save()

            attacker = form.cleaned_data.get("attacker")
            competition.attacker.set(attacker)
            defender = form.cleaned_data.get("defender")
            competition.defender.set(defender)

            create_experiments_for_competition(competition)

            return redirect("competitiondefinitionmanagement:competitionlist")

    else:
        if competition_id:
            # duplicate
            competition = __check_competition_exists(competition_id)
            if not competition:
                messages.error(request, "Competition does not exist.")
                return redirect(
                    "competitiondefinitionmanagement:competitioncreate"
                )

            # Check if user is allowed to see experiment (used is owner/experiment is public)
            if not competition.is_public and request.user != competition.owner:
                # User is not allowed to see agent, redirect to experiment list
                messages.error(request, "Permission denied.")
                return redirect(
                    "competitiondefinitionmanagement:competitioncreate"
                )
            new_competition_name = increment_string(competition.name)
            competition_copy = CompetitionRun(
                name=new_competition_name,
                erd=competition.erd,
                owner=competition.owner,
                is_public=competition.is_public,
            )
            form = CompetitionCreationForm(
                user=request.user,
                instance=competition_copy,
                initial={
                    "attacker": competition.attacker.all(),
                    "defender": competition.defender.all(),
                },
            )

        else:
            # creating a new competition
            path = os.path.join(
                settings.BASE_DIR,
                "yaml_defaults",
                "competition_erd_with_comments.yml",
            )
            with open(path, "r") as file:
                default_competition_erd = file.read()
            form = CompetitionCreationForm(
                user=request.user, initial={"erd": default_competition_erd}
            )

    attackers_empty = True
    defenders_empty = True
    if len(form.fields["attacker"].queryset) > 0:
        attackers_empty = False
    if len(form.fields["defender"].queryset) > 0:
        defenders_empty = False

    context = {
        "form": form,
        "attackers_empty": attackers_empty,
        "defenders_empty": defenders_empty,
    }
    return render(request, "competition_create_page.html", context)


def competition_details(request, competition_id):
    """Shows the competition details page (with information, competition run document, experiments, results and leaderboard)."""
    competition = __check_competition_exists(competition_id)
    if not competition:
        messages.error(request, "Competition does not exist.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    attackers = competition.attacker.all()
    defenders = competition.defender.all()

    # Check if user is allowed to see experiment (used is owner/competition is public)
    if not competition.is_public and request.user != competition.owner:
        # User is not allowed to see agent, redirect to competition list
        messages.error(request, "Permission denied.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    try:
        # shows only the experiments which points to the specific competition
        experiments = (
            ExperimentRun.objects.filter(competition=competition)
            .annotate(
                running=Case(
                    When(status="running", then=1),
                    output_field=IntegerField(),
                ),
            )
            .order_by("running", "-timestamp_created")
        )
    except ExperimentRun.DoesNotExist:
        messages.error(request, "Competition experiments do not exist.")
        return redirect("experimentdefinitionmanagement:experimentlist")

    if (
        competition.status == "completed"
        or competition.status == "aborted"
        or competition.status == "failed"
    ):
        competition_results_defender = calculate_competition_results(
            competition, aggregate_by_defenders=True
        )
        leaderboard_list_defender = calculate_ranking(
            competition_results_defender,
            evaluation_criteria="Rating function",
            defender_ranking=True,
        )
        competition_results_attacker = calculate_competition_results(
            competition, aggregate_by_defenders=False
        )
        leaderboard_list_attacker = calculate_ranking(
            competition_results_attacker,
            evaluation_criteria="Rating function",
            defender_ranking=False,
        )
    else:
        competition_results_defender = None
        leaderboard_list_defender = None
        competition_results_attacker = None
        leaderboard_list_attacker = None

    context = {
        "attackers": attackers,
        "defenders": defenders,
        "competition": competition,
        "experiments": experiments,
        "competition_results_defender": competition_results_defender,
        "leaderboard_list_defender": leaderboard_list_defender,
        "competition_results_attacker": competition_results_attacker,
        "leaderboard_list_attacker": leaderboard_list_attacker,
    }
    return render(request, "competition_detail_page.html", context)


def download_yml(request, competition_id):
    """Downloads the competition run document as a yml file."""

    competition = __check_competition_exists(competition_id)
    if not competition:
        messages.error(request, "Competition does not exist.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    # Check if user is allowed to see experiment (used is owner/competition is public)
    if not competition.is_public and request.user != competition.owner:
        # User is not allowed to see agent, redirect to competition list
        messages.error(request, "Permission denied.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    response = HttpResponse(
        competition.erd, content_type="text/x-yaml charset=utf-8"
    )
    response[
        "Content-Disposition"
    ] = f'attachment; filename="competition_{competition_id}_crd.yml"'
    return response


def export_results(request, competition_id):
    """Exports the competition results as a csv file."""

    competition = __check_competition_exists(competition_id)
    if not competition:
        messages.error(request, "Competition does not exist.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    # Check if user is allowed to see experiment (used is owner/competition is public)
    if not competition.is_public and request.user != competition.owner:
        # User is not allowed to see agent, redirect to competition list
        messages.error(request, "Permission denied.")
        return redirect("competitiondefinitionmanagement:competitionlist")

    if competition.status == "completed":
        competition_results = calculate_competition_results(
            competition, aggregate_by_defenders=True
        )

        header = [
            "evaluation criteria",
            "agent name",
            "avg value",
            "min value",
            "max value",
            "unit",
        ]
        competition_result_list = []
        for criteria, results in competition_results.items():
            for result in results:
                competition_result_list.append(
                    [criteria, result[0].name, *result[1:]]
                )
        print(competition_result_list[0])
        file_data = io.StringIO()
        writer = csv.writer(file_data)
        writer.writerow(header)
        writer.writerows(competition_result_list)

        # some code
        response = HttpResponse(
            file_data.getvalue(), content_type="text/csv charset=utf-8"
        )
        response[
            "Content-Disposition"
        ] = f'attachment; filename="competition_{competition_id}_export.csv"'
        return response
    else:
        messages.error(
            request, "Results can be exported only for completed competitions."
        )
        return redirect(
            "competitiondefinitionmanagement:competitiondetails",
            competition_id,
        )


def __check_competition_exists(competition_id):
    try:
        competition = CompetitionRun.objects.get(pk=competition_id)
    except CompetitionRun.DoesNotExist:
        logger.info(f"Competition with id {competition_id} does not exist")
        return None
    return competition
