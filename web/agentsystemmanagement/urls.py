from django.urls import path

from . import views

app_name = "pgasc.web.agentsystemmanagement"
urlpatterns = [
    path("upload", views.upload, name="agent_upload"),
    path(
        "ajax/check_agent_name_exists",
        views.check_agent_name_exists,
        name="check_agent_name_exists",
    ),
    path("agentlist", views.show_agent_list, name="agent_list"),
    path("delete/<int:agent_id>", views.delete, name="delete"),
    path(
        "download/<int:agent_id>",
        views.download,
        name="agent_download",
    ),
    path(
        "detail/<int:agent_id>", views.show_agent_details, name="agent_detail"
    ),
]
