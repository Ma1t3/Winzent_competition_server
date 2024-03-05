import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from . import create_defaults as default_helper
from ..experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


def home(request):
    """Renders the home page."""
    logger.debug("Home page accessed")

    if settings.WEBSITE_DEV_MODE:
        last_git_commit = os.getenv("GIT_LAST_COMMIT", None)
        last_commit_hash, last_commit_date = None, None
        if last_git_commit:
            last_commit_hash, last_commit_date = last_git_commit.split(";")
    else:
        last_commit_hash, last_commit_date = None, None
    context = {
        "enqueued_count": ExperimentRun.objects.filter(
            status="enqueued"
        ).count(),
        "running_count": ExperimentRun.objects.filter(
            status="running"
        ).count(),
        "dev_mode": settings.WEBSITE_DEV_MODE,
        "last_commit_hash": last_commit_hash,
        "last_commit_date": last_commit_date,
    }
    return render(request, "home_page.html", context)


def create_test_user_and_log_in(request):
    """Creates a test user and logs in. This is only available in dev mode for testing purposes."""
    if not settings.WEBSITE_DEV_MODE:
        return redirect("home")

    username = "testuser"
    email = "testuser@pgasc.local"
    password = "pass"

    default_helper.create_default_user(
        username, password, email, is_active=True
    )

    user = authenticate(username=username, password=password)
    login(request, user)

    messages.success(
        request,
        f"You're logged in with '{username}' and password '{password}'.",
    )

    return redirect("home")


def howto(request):
    """Renders the howto page."""

    context = {}
    return render(request, "how_to_page.html", context)
