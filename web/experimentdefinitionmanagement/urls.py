from django.urls import path

from . import views

app_name = "experimentdefinitionmanagement"
urlpatterns = [
    path("create", views.create, name="experiment_create"),
    path("copy/<int:experiment_id>", views.create, name="experiment_copy"),
    path("experimentlist", views.show_experiment_list, name="experimentlist"),
    path(
        "ajax/experimentlist",
        views.ajax_experiment_list,
        name="ajax_experimentlist",
    ),
    path(
        "details/<int:experiment_id>", views.details, name="experiment_details"
    ),
    path(
        "show_grafana_data/<int:experiment_id>",
        views.show_grafana_data,
        name="show_grafana_data",
    ),
    path("delete/<int:experiment_id>", views.delete, name="delete"),
    path(
        "download/<int:experiment_id>",
        views.download_yml,
        name="experiment_download",
    ),
    path(
        "download_logfile/<int:experiment_id>",
        views.download_logfile,
        name="download_logfile",
    ),
    path(
        "generate_export/<int:experiment_id>",
        views.generate_export,
        name="generate_export",
    ),
    path(
        "export_data/<int:experiment_id>",
        views.export_data,
        name="export_data",
    ),
    path(
        "ajax/stream_logfile/<int:experiment_id>",
        views.ajax_stream_docker_logs,
        name="stream_logfile",
    ),
]
