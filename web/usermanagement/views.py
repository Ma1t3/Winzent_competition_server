import logging

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import CustomUserRegistrationForm

logger = logging.getLogger(__name__)


def register(request):
    """View for registering a new user.

    This will render a view with a registration form.
    It also handle sending the form, validating it and
    saving the user to the database. The user is automatically
    logged in.
    """
    if request.method == "POST":
        form = CustomUserRegistrationForm(request.POST)

        logger.debug(
            "Received registration request, checking form for correctness now"
        )
        # if all form conditions (Password strength etc.) are met:
        if form.is_valid():
            # save new user to database
            form.save()

            # authenticate and log in new user
            username = form.cleaned_data.get("username")
            logger.info(f"New user {username} registered")

            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            messages.success(
                request, f"Thank you for registering, {username}!"
            )
            # redirect to home page
            return redirect("home")

    else:
        form = CustomUserRegistrationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context=context)


@login_required
def set_list_autoreload(request):
    """Setting the autoreload flag for the experiment and competition lists."""
    autoreload = request.POST.get("autoreload", "false")
    if autoreload == "false":
        autoreload = False
    elif autoreload == "true":
        autoreload = True

    user = request.user
    user.list_autoreload = autoreload
    user.save()

    data = {"success": True}
    return JsonResponse(data)
