import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from pgasc.grafana.handler.grafana_dashboard_handler import (
    GrafanaDashboardHandler,
)
from pgasc.web.competitiondefinitionmanagement.models import CompetitionRun
from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


def _start_experiment_and_create_dashboard(experiment):
    if experiment.status == "created":
        experiment.status = "enqueued"
        experiment.timestamp_enqueued = timezone.now()
        experiment.save()

        grafana_handler = GrafanaDashboardHandler()
        grafana_handler.create_dashboard(experiment)
    else:
        logger.info("experiment could not be enqueued")


def start_experiment(request):
    """Add the given experiment to the queue of experiments to be executed and create a grafana dashboard for it."""
    experiment_id = request.GET.get("experiment", None)
    experiment = __check_experiment_exists(experiment_id)
    if not experiment:
        messages.error(
            request, "Experiment cannot be started because it does not exist."
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    if request.user == experiment.owner:
        if experiment.competition is None:
            _start_experiment_and_create_dashboard(experiment)
        else:
            messages.info(
                request,
                "Cannot start experiments that are part of a competition.",
            )
            logger.info(
                "Cannot start experiments that are part of a competition"
            )

    return redirect("experimentdefinitionmanagement:experimentlist")


def abort_experiment(request):
    """Set the given experiment to aborted_by_user."""
    experiment_id = request.GET.get("experiment", None)
    experiment = __check_experiment_exists(experiment_id)
    if not experiment:
        messages.error(
            request, "Experiment cannot be aborted because it does not exist."
        )
    elif request.user == experiment.owner:
        ExperimentRun.objects.filter(pk=experiment_id).update(
            aborted_by_user=True
        )
    else:
        messages.error(
            request,
            "Experiment cannot be aborted because you are not the owner.",
        )
    return redirect("experimentdefinitionmanagement:experimentlist")


def competition_start(request):
    """Start all experiments of the given competition."""
    competition_id = request.GET.get("competition", None)
    user = request.user
    try:
        competition = CompetitionRun.objects.get(pk=competition_id)
        experiments = ExperimentRun.objects.filter(
            competition_id=competition.id
        )
    except CompetitionRun.DoesNotExist:
        logger.info("competition does not exist")
        messages.error(
            request, "Competition cannot be started because it does not exist."
        )
        return redirect("competitiondefinitionmanagement:competitionlist")

    if request.user != competition.owner:
        messages.error(
            request,
            "Competition cannot be started because you are not the owner.",
        )
        return redirect("competitiondefinitionmanagement:competitionlist")

    try:
        if competition.status == "created":
            CompetitionRun.objects.filter(pk=competition_id).update(
                status="enqueued"
            )
            for experiment in experiments:
                if user == experiment.owner:
                    _start_experiment_and_create_dashboard(experiment)
    except Exception:
        logger.info("not all experiments could be enqueued")
        return redirect("competitiondefinitionmanagement:competitionlist")

    return redirect("competitiondefinitionmanagement:competitionlist")


def competition_abort(request):
    """Set all experiments of the given competition to aborted_by_user."""
    competition_id = request.GET.get("competition", None)
    try:
        competition = CompetitionRun.objects.get(pk=competition_id)
        experiments = ExperimentRun.objects.filter(competition=competition)
    except CompetitionRun.DoesNotExist:
        logger.info("competition does not exist")
        messages.error(
            request, "Competition cannot be aborted because it does not exist."
        )
        return redirect("competitiondefinitionmanagement:competitionlist")

    if request.user != competition.owner:
        messages.error(
            request,
            "Competition cannot be aborted because you are not the owner.",
        )
        return redirect("competitiondefinitionmanagement:competitionlist")

    CompetitionRun.objects.filter(pk=competition_id).update(
        aborted_by_user=True
    )

    for experiment in experiments:
        if request.user == experiment.owner:
            ExperimentRun.objects.filter(competition=competition).update(
                aborted_by_user=True
            )

    return redirect("competitiondefinitionmanagement:competitionlist")


def __check_experiment_exists(experiment_id):
    """Return the experiment if it exists, otherwise None."""
    try:
        experiment = ExperimentRun.objects.get(pk=experiment_id)
    except ExperimentRun.DoesNotExist:
        logger.info(f"Experiment with id {experiment_id} does not exist")
        return None
    return experiment
