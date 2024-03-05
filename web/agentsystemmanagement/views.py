import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField
from django.http import JsonResponse
from django.shortcuts import render, redirect

from . import agent_files, agent_logic
from .forms import AgentUploadFormMan
from .forms import ClassPathForm
from .models import Agent

logger = logging.getLogger(__name__)


@login_required
def upload(request):
    """Function to upload a new agent to the competition server."""

    if request.method == "POST":
        form = AgentUploadFormMan(request.POST, request.FILES)
        if form.is_valid():
            # Create agent object and save to database
            agent = Agent()
            agent.name = form.cleaned_data.get("name")
            agent.role = form.cleaned_data.get("role")
            agent.description = form.cleaned_data.get("description")
            agent.is_public = form.cleaned_data.get("is_public")
            agent.init_yml = form.cleaned_data.get("init_yml")
            agent.owner = request.user
            agent.save()

            try:
                # create agent directory and save uploaded agent files to disk, decompressing the zip file
                agent_files.save_agent_files(
                    agent.pk,
                    request.FILES.get("file", None),
                )
                # Check if brain and muscle classes exist
                agent_logic.set_readonly_if_classes_exist(agent)
                return redirect(
                    "pgasc.web.agentsystemmanagement:agent_detail",
                    agent_id=agent.pk,
                )
            except Exception as e:
                logger.error("Error", exc_info=e)
                messages.error(
                    request,
                    "Agent files were not saved to disk successfully. Your agent files may be corrupted.",
                )
                return redirect("pgasc.web.agentsystemmanagement:agent_list")
    else:
        path = os.path.join(
            settings.BASE_DIR,
            "yaml_defaults",
            "agent_init_yaml_with_comments.yml",
        )
        with open(path, "r") as file:
            default_agent_yml = file.read()
        form = AgentUploadFormMan(initial={"init_yml": default_agent_yml})

    context = {"form": form}
    return render(request, "agent_upload_page.html", context)


def download(request, agent_id):
    """Function to download an agent from the competition server."""

    agent = __check_agent_exists(agent_id)
    if not agent:
        messages.error(
            request, "Agent cannot be downloaded because it does not exist."
        )
        return redirect("pgasc.web.agentsystemmanagement:agent_list")

    if agent.owner == request.user or agent.is_public:
        return agent_files.load_agent_files(agent_id)
    else:
        messages.error(request, "No permission to download agent.")
    return redirect("pgasc.web.agentsystemmanagement:agent_list")


def check_agent_name_exists(request):
    agent_name = request.GET.get("agent_name", None)
    data = {
        "agent_name_exists": Agent.objects.filter(name=agent_name).exists()
    }
    return JsonResponse(data)


def show_agent_list(request):
    """Function to show a list of agents that are visible to the user of the request."""

    agents = Agent.objects.filter(is_public=True)
    agents = agents.order_by("-upload_timestamp")
    if request.user.is_authenticated:
        agents |= Agent.objects.filter(owner=request.user)
        agents = agents.annotate(
            relevancy=Case(
                When(owner=request.user, then=1), output_field=IntegerField()
            )
        ).order_by("relevancy", "-upload_timestamp")

    context = {"agents": agents}
    return render(request, "agent_list_page.html", context)


def show_agent_details(request, agent_id):
    """Function to show the details (information, file list) of an agent."""

    # Check if agent exists in database
    agent = __check_agent_exists(agent_id)
    if not agent:
        messages.error(request, "Requested agent does not exist.")
        return redirect("pgasc.web.agentsystemmanagement:agent_list")

    # Check if user is allowed to see agent (used is owner/agent is public)
    if not agent.is_public and agent.owner != request.user:
        # User is not allowed to see agent, redirect to agent list
        messages.error(request, "No permission to see agent.")
        return redirect("pgasc.web.agentsystemmanagement:agent_list")

    # load agent file list
    agent_path = os.path.join(settings.DIR_AGENTS, str(agent_id))
    agent_file_list = agent_files.get_file_list(agent_path)
    if agent.owner == request.user:
        if request.method == "POST":
            form = ClassPathForm(request.POST)
            if form.is_valid():
                agent.init_yml = form.cleaned_data.get("yml")
                agent.save()
                agent_logic.set_readonly_if_classes_exist(agent)
                return redirect(
                    "pgasc.web.agentsystemmanagement:agent_detail",
                    agent_id=agent.pk,
                )
        else:
            # show form if yml not correct
            if (
                (not agent.path_brain_is_correct)
                or (not agent.path_muscle_is_correct)
                or (not agent.path_objective_is_correct)
            ):
                form = ClassPathForm(
                    initial={"yml": agent.init_yml},
                )
            else:
                form = None
    else:
        form = None

    context = {
        "agent": agent,
        "agent_files": agent_file_list,
        "init_yml_form": form,
    }
    return render(request, "agent_detail_page.html", context)


def delete(request, agent_id):
    """Function to delete an agent from the competition server."""

    agent = __check_agent_exists(agent_id)
    if not agent:
        messages.error(
            request, "Agent cannot be deleted because it does not exist."
        )
        return redirect("pgasc.web.agentsystemmanagement:agent_list")

    if request.user == agent.owner:
        # delete from our database
        Agent.objects.filter(id=agent_id).delete()
        # delete from filesystem
        agent_files.delete_agent_files(agent.pk)
        # delete from Grafana is not necessary since no agent data is saved there
        # TODO: delete from palaestrai (if necessary)
        messages.success(request, "Agent deleted.")
        return redirect("pgasc.web.agentsystemmanagement:agent_list")
    messages.error(
        request, "Agent cannot be deleted because you are not the owner."
    )
    return redirect("pgasc.web.agentsystemmanagement:agent_list")


def __check_agent_exists(agent_id):
    try:
        agent = Agent.objects.get(pk=agent_id)
    except Agent.DoesNotExist:
        return None
    return agent
