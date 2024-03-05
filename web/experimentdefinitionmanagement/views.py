import logging
import os
import re
import shutil

import docker
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import ProgrammingError
from django.db import connections
from django.db.models import Case, When, IntegerField
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect

from pgasc.grafana.handler.grafana_dashboard_handler import (
    GrafanaDashboardHandler,
)
from . import exportData
from .experiment_logic import create_experiment_run_files
from .forms import ExperimentCreationForm
from .models import ExperimentRun

LOAD_LOG_MAX_CHARS = 20_000

logger = logging.getLogger(__name__)


def increment_string(strng):
    """check if strng ends with a number. If yes, increment the number, else add ' 001'"""

    # \d+$ finds one or more digits directly at the end of the string
    # x.group() returns the found substring
    # zfill adds zeros to the beginning, here to the same length as the original
    # subn returns the new string and the number of replacements made
    new_strng, n_of_subs_made = re.subn(
        r"\d+$", lambda x: str(int(x.group()) + 1).zfill(len(x.group())), strng
    )
    if n_of_subs_made >= 1:
        return new_strng
    else:
        return new_strng + " 2"


@login_required()
def create(request, experiment_id=None):
    """Create a new experiment or duplicate an existing one."""
    if request.method == "POST":
        form = ExperimentCreationForm(request.user, request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            defender = form.cleaned_data.get("defender")
            store_trained_defender = form.cleaned_data.get(
                "store_trained_defender"
            )
            attacker = form.cleaned_data.get("attacker")
            store_trained_attacker = form.cleaned_data.get(
                "store_trained_attacker"
            )
            erd = form.cleaned_data.get("erd")
            is_public = form.cleaned_data.get("is_public")
            owner = request.user

            experiment = ExperimentRun(
                name=name,
                defender=defender,
                store_trained_defender=store_trained_defender,
                attacker=attacker,
                store_trained_attacker=store_trained_attacker,
                owner=owner,
                is_public=is_public,
            )
            experiment.save()
            create_experiment_run_files(experiment, erd)

            return redirect("experimentdefinitionmanagement:experimentlist")
    else:
        # duplicating a experiment
        if experiment_id:
            try:
                experiment = ExperimentRun.objects.get(pk=experiment_id)
            except ExperimentRun.DoesNotExist:
                return redirect(
                    "experimentdefinitionmanagement:experiment_create"
                )

            # Check if user is allowed to see experiment (used is owner/experiment is public)
            if not experiment.is_public and request.user != experiment.owner:
                # User is not allowed to see agent, redirect to experiment list
                return redirect(
                    "experimentdefinitionmanagement:experiment_create"
                )

            new_experiment_name = increment_string(experiment.name)
            experiment_copy = ExperimentRun(
                name=new_experiment_name,
                defender=experiment.defender,
                store_trained_defender=experiment.store_trained_defender,
                attacker=experiment.attacker,
                store_trained_attacker=experiment.store_trained_attacker,
                is_public=experiment.is_public,
            )
            try:
                erd_path = os.path.join(
                    settings.DIR_EXPERIMENTS, f"{experiment_id}_user.yml"
                )
                with open(erd_path, "r") as file:
                    erd = file.read()
            except IOError:
                erd = ""
            form = ExperimentCreationForm(
                user=request.user,
                instance=experiment_copy,
                initial={"erd": erd},
            )
        # creating a new experiment
        else:
            path = os.path.join(
                settings.BASE_DIR,
                "yaml_defaults",
                "experiment_erd_with_comments.yml",
            )
            with open(path, "r") as file:
                default_erd = file.read()
            form = ExperimentCreationForm(
                user=request.user, initial={"erd": default_erd}
            )

    context = {"form": form}
    return render(request, "experiment_create_page.html", context)


def get_experiment_list_context(request):
    """Get the context for the experiment list page."""

    experiments = ExperimentRun.objects.filter(
        is_public=True, competition_id=None
    )

    if request.user.is_authenticated:
        experiments |= ExperimentRun.objects.filter(
            owner=request.user, competition_id=None
        )
        experiments = experiments.annotate(
            own_experiments=Case(
                When(owner=request.user, then=1), output_field=IntegerField()
            ),
            running=Case(
                When(status="running", then=1),
                output_field=IntegerField(),
            ),
        ).order_by("running", "own_experiments", "-timestamp_created")
    else:
        experiments = experiments.annotate(
            running=Case(
                When(status="running", then=1),
                output_field=IntegerField(),
            ),
        ).order_by("running", "-timestamp_created")

    context = {"experiments": experiments}
    return context


def show_experiment_list(request):
    """Show the experiment list page."""
    context = get_experiment_list_context(request)
    return render(request, "experiment_list_page.html", context)


def ajax_experiment_list(request):
    """Return the experiment list to update the experiment list page via ajax."""
    context = get_experiment_list_context(request)
    return render(request, "experiment_list.html", context)


def show_grafana_data(request, experiment_id):
    """Redirect to the grafana dashboard for the experiment."""
    if request.method == "POST":
        try:
            experiment = ExperimentRun.objects.get(pk=experiment_id)
        except ExperimentRun.DoesNotExist:
            messages.error(request, "Experiment does not exist.")
            return redirect("experimentdefinitionmanagement:experimentlist")
        grafana_helper = GrafanaDashboardHandler()
        return redirect(grafana_helper.get_dashboard_link(experiment))


def delete(request, experiment_id):
    """Delete an experiment."""

    experiment = __check_experiment_exists(experiment_id)
    if not experiment:
        messages.error(
            request, "Experiment cannot be deleted because it does not exist."
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    if (
        request.user == experiment.owner
        and experiment.competition is None
        and experiment.status != "running"
        and experiment.status != "enqueued"
    ):
        # delete from our database
        ExperimentRun.objects.filter(id=experiment_id).delete()
        # delete from filesystem
        path = os.path.join(settings.DIR_AGENTS, str(experiment.pk))
        if os.path.exists(path):
            shutil.rmtree(path)
        # delete from grafana
        grafana_helper = GrafanaDashboardHandler()
        grafana_helper.delete_dashboard(experiment)
        # delete from midas
        _delete_experiment_from_midas(experiment_id)
        # TODO: delete from palaestrai (if necessary)
        return redirect("experimentdefinitionmanagement:experimentlist")
    return redirect("experimentdefinitionmanagement:experimentlist")


def details(request, experiment_id):
    """Show the details page for an experiment (information, erd, results, logfile)."""
    experiment = __check_experiment_exists(experiment_id)
    if not experiment:
        messages.error(
            request, "Experiment cannot be viewed because it does not exist."
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    # Check if user is allowed to see experiment (used is owner/experiment is public)
    if not experiment.is_public and request.user != experiment.owner:
        # User is not allowed to see agent, redirect to experiment list
        messages.error(
            request,
            "Experiment cannot be viewed because you do not have permissions.",
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    try:
        with connections["midas"].cursor() as cursor:
            cursor.execute(
                f"select * FROM experiment_result  WHERE experiment_id = {experiment_id}"
            )
            rating_results = cursor.fetchall()
    except Exception:
        rating_results = ""

    # load erd
    try:
        erd_path = os.path.join(
            settings.DIR_EXPERIMENTS, f"{experiment_id}_user.yml"
        )
        with open(erd_path, "r") as file:
            erd = file.read()
    except Exception:
        messages.error(
            request,
            "ERD file could not be loaded.",
        )
        erd = ""

    # grafana
    grafana_helper = GrafanaDashboardHandler()
    dashboard_link = grafana_helper.get_dashboard_link(experiment)

    # logfile
    try:
        path = os.path.join(
            settings.DIR_EXPERIMENT_LOGS, f"{experiment.pk}.log"
        )
        with open(path) as file:
            text = file.read()
            logfile_part = text[-LOAD_LOG_MAX_CHARS:]
        logfile_size = os.path.getsize(path)

        for unit in ("B", "KB", "MB", "GB"):
            if logfile_size < 1024:
                break
            logfile_size /= 1024
        logfile_size_with_unit = f"{logfile_size:.2f} {unit}"
    except FileNotFoundError:
        logfile_part, logfile_size_with_unit = None, None

    context = {
        "experiment": experiment,
        "dashboard_link": dashboard_link,
        "yaml_content": erd,
        "logfile_part": logfile_part,
        "logfile_size_with_unit": logfile_size_with_unit,
        "rating_results": rating_results,
    }

    return render(request, "experiment_detail_page.html", context)


def download_logfile(request, experiment_id):
    """Download the logfile of an experiment."""
    try:
        experiment = ExperimentRun.objects.get(pk=experiment_id)
    except ExperimentRun.DoesNotExist:
        messages.error(request, "Experimentobject not found")
        return redirect("experimentdefinitionmanagement:experimentlist")

    if not experiment.is_public and request.user != experiment.owner:
        messages.error(request, "Permission denied!")
        return redirect("experimentdefinitionmanagement:experimentlist")

    try:
        path = os.path.join(
            settings.DIR_EXPERIMENT_LOGS, f"{experiment.pk}.log"
        )
        with open(path) as file:
            logfile = file.read()
    except FileNotFoundError:
        messages.error(request, "Logfile not available")
        return redirect(
            "experimentdefinitionmanagement:experiment_details", experiment_id
        )

    response = HttpResponse(logfile, content_type="text/plain charset=utf-8")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="experiment_{experiment_id}.log"'
    return response


def download_yml(request, experiment_id):
    """Download the erd as yml file of an experiment."""
    experiment = __check_experiment_exists(experiment_id)
    if not experiment:
        messages.error(
            request,
            "Experiment cannot be downloaded because it does not exist.",
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    if not experiment.is_public and request.user != experiment.owner:
        messages.error(
            request,
            "Experiment cannot be downloaded because you do not have permissions.",
        )
        return redirect("experimentdefinitionmanagement:experimentlist")

    try:
        erd_path = os.path.join(
            settings.DIR_EXPERIMENTS, f"{experiment_id}_user.yml"
        )
        with open(erd_path, "r") as file:
            erd = file.read()
    except Exception:
        messages.info(request, "Could not load file")
        return

    response = HttpResponse(erd, content_type="text/x-yaml charset=utf-8")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="experiment_{experiment_id}_erd.yml"'
    return response


def generate_export(request, experiment_id):
    """Generate an export of the results of the given experiment."""
    try:
        experiment = ExperimentRun.objects.get(pk=experiment_id)
        if request.user == experiment.owner or experiment.is_public:
            return exportData.generate_results(experiment_id)
        else:
            return HttpResponse(content="Permission denied")

    except Exception:
        return HttpResponse(content="Error")


def export_data(request, experiment_id):
    """Export the results of the given experiment."""
    try:
        return exportData.export_results(experiment_id)

    except Exception:
        return HttpResponse(content="Error")

    finally:
        shutil.rmtree(settings.DIR_EXPERIMENT_EXPORT)


def _delete_experiment_from_midas(experiment_id):
    """Delete an experiment from the midas database."""
    tables = {
        "experiment_result",
        "constraint",
        "pp_bus",
        "pp_bus_meta",
        "pp_ext_grid",
        "pp_ext_grid_meta",
        "pp_line",
        "pp_line_meta",
        "pp_load",
        "pp_load_meta",
        "pp_static_generator",
        "pp_static_generator_meta",
        "pp_trafo",
        "pp_trafo_meta",
    }
    with connections["midas"].cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(
                    f"DELETE FROM {table} WHERE experiment_id = {experiment_id}"
                )
            except ProgrammingError:
                print(f"Table {table} not found")


def __check_experiment_exists(experiment_id):
    """Return the experiment if it exists, otherwise None."""
    try:
        experiment = ExperimentRun.objects.get(pk=experiment_id)
    except ExperimentRun.DoesNotExist:
        logger.info(f"Experiment with id {experiment_id} does not exist")
        return None
    return experiment


def ajax_stream_docker_logs(request, experiment_id):
    """Live stream the docker logs of an experiment to the client."""
    experiment = __check_experiment_exists(experiment_id)

    # Check if experiment exists and user is allowed to access it and experiment is running
    if (
        not experiment
        or (not experiment.is_public and request.user != experiment.owner)
        or experiment.status != "running"
    ):
        return

    def event_stream():
        client = docker.from_env()
        container = client.containers.get(experiment.docker_container_id)
        stream = container.logs(stream=True, tail=30)

        for a in stream:
            yield f'data: {a.decode("utf-8")} \n\n'

        while True:
            yield f'data: {next(stream).decode("utf-8")} \n\n'

    return StreamingHttpResponse(
        event_stream(), content_type="text/event-stream"
    )
