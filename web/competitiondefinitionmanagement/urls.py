from django.urls import path

from . import views

app_name = "competitiondefinitionmanagement"
urlpatterns = [
    path(
        "competitionlist", views.show_competition_list, name="competitionlist"
    ),
    path(
        "ajax/competitionlist",
        views.ajax_competition_list,
        name="ajax_competitionlist",
    ),
    path(
        "competitioncreate", views.competition_create, name="competitioncreate"
    ),
    path(
        "copy/<int:competition_id>",
        views.competition_create,
        name="competitioncopy",
    ),
    path(
        "details/<int:competition_id>",
        views.competition_details,
        name="competitiondetails",
    ),
    path(
        "download/<int:competition_id>",
        views.download_yml,
        name="download",
    ),
    path(
        "export-results/<int:competition_id>",
        views.export_results,
        name="export-results",
    ),
]
