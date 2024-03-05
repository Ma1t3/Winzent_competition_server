from django.urls import path

from . import views

app_name = "experimentexecutionmanagement"
urlpatterns = [
    path("start", views.start_experiment, name="experiment_start"),
    path("abort", views.abort_experiment, name="experiment_abort"),
    path(
        "competition_start", views.competition_start, name="competition_start"
    ),
    path(
        "competition_abort", views.competition_abort, name="competition_abort"
    ),
]
