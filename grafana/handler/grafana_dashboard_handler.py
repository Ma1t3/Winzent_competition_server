import json
import logging
import os
import pathlib
from datetime import timedelta

import yaml
from dateutil import parser
from django.conf import settings
from grafana_api.grafana_face import GrafanaFace

logger = logging.getLogger(__name__)


class GrafanaDashboardHandler:
    """Helper functions for grafana"""

    def __init__(self):
        self.base_dir = pathlib.Path(__file__).resolve().parent
        self.grafana_api = self._connect_grafana()
        # if something was changed in the dashboard json, then this number can be increased
        self.version = "V1"

    def get_dashboard_link(self, experiment):
        """Returns the link to the grafana dashboard"""

        experiment_id = experiment.id
        experiment_name = experiment.name
        username = experiment.owner.username
        user_id = experiment.owner.id

        uid_folder = self._generate_uid_folder(user_id)
        uid_dashboard = self._generate_uid_dashboard(experiment_id)

        title_folder = f"{username}_{user_id}"
        folder = self._search_folder(title_folder, uid_folder)
        # check folder exists
        if folder is not None:
            dashboard = self._search_dashboard(
                folder, experiment_name, experiment_id, uid_dashboard
            )

            # check dashboard exists
            if dashboard is not None:
                return os.environ["GF_SERVER_ROOT_URL"] + dashboard["url"]

        # if Dashboard does not exist, then create a new one
        dashboard = self.create_dashboard(experiment)
        if dashboard is not None:
            return os.environ["GF_SERVER_ROOT_URL"] + dashboard["url"]
        return None

    def create_dashboard(self, experiment):
        """Creates a new dashboard for the given experiment"""

        experiment_id = experiment.id
        experiment_name = experiment.name
        username = experiment.owner.username
        user_id = experiment.owner.id

        # each user has a folder in grafana
        folder = self._create_grafana_folder(
            username=username, user_id=user_id
        )

        dashboard = self._create_grafana_dashboard(
            folder=folder,
            experiment_id=experiment_id,
            experiment_name=experiment_name,
        )

        return dashboard

    def delete_dashboard(self, experiment):
        """Deletes the dashboard of the given experiment"""

        experiment_id = experiment.id
        experiment_name = experiment.name
        username = experiment.owner.username
        user_id = experiment.owner.id

        uid_folder = self._generate_uid_folder(user_id)
        uid_dashboard = self._generate_uid_dashboard(experiment_id)

        title_folder = f"{username}_{user_id}"
        folder = self._search_folder(title_folder, uid_folder)
        # check folder exists
        if folder is not None:
            dashboard = self._search_dashboard(
                folder, experiment_name, experiment_id, uid_dashboard
            )

            # check dashboard exists
            if dashboard is not None:
                self.grafana_api.dashboard.delete_dashboard(
                    dashboard_uid=uid_dashboard
                )

    def _create_grafana_dashboard(
        self, folder, experiment_id, experiment_name
    ):
        uid = self._generate_uid_dashboard(experiment_id)

        # check dashbaord exists
        dashboard = self._search_dashboard(
            folder, experiment_name, experiment_id, uid
        )
        if dashboard is not None:
            return dashboard

        # create dashboard
        with open(
            os.path.join(self.base_dir, "../static/dashboard.json"), "r"
        ) as f:
            array = json.load(f)
            array["uid"] = uid
            array["title"] = (
                experiment_name
                + f"_experiment_id={str(experiment_id)}_v1={self.version}"
            )

            # set experiment id of new dashbaord
            array["templating"]["list"][0]["query"] = experiment_id

            # set experiment start_date of new dashboard
            experiment_config = self._get_experiment_config(experiment_id)
            start_date = str(parser.isoparse(experiment_config["start_date"]))
            end_date = str(
                parser.isoparse(start_date)
                + timedelta(seconds=eval(experiment_config["end"]))
            )
            array["templating"]["list"][1]["query"] = start_date
            array["templating"]["list"][2]["query"] = end_date

            return self.grafana_api.dashboard.update_dashboard(
                dashboard={"dashboard": array, "folderId": folder["id"]}
            )

    def _create_grafana_folder(self, username, user_id):
        title = f"{username}_{user_id}"
        uid = self._generate_uid_folder(user_id)

        # check folder exists
        folder = self._search_folder(title, uid)
        if folder is not None:
            return folder

        # if not create new folder
        folder = self.grafana_api.folder.create_folder(title, uid)
        return folder

    def _search_folder(self, title, uid):
        filtered = self.grafana_api.search.search_dashboards(query=title)
        folders = [
            x
            for x in filtered
            if x["type"] == "dash-folder" and x["uid"] == uid
        ]

        if len(folders) > 0:
            return folders[0]

        return None

    def _search_dashboard(self, folder, title, experiment_id, uid):
        filtered = self.grafana_api.search.search_dashboards(
            folder_ids=[folder["id"]],
            query=title
            + f"_experiment_id={str(experiment_id)}_v1={self.version}",
        )

        dashboards = [
            x for x in filtered if x["type"] == "dash-db" and x["uid"] == uid
        ]

        if len(dashboards) > 0:
            return dashboards[0]

        return None

    def _generate_uid_dashboard(self, experiment_id):
        return self._convert_uid(f"Dashboard_{experiment_id}_{self.version}")

    def _generate_uid_folder(self, user_id):
        return self._convert_uid(f"Folder_{user_id}")

    @staticmethod
    def _convert_uid(uid):
        # remove unlegal characters
        return "".join(uid.split())

    @staticmethod
    def _connect_grafana():
        return GrafanaFace(
            auth=(
                os.environ["GF_SECURITY_ADMIN_USER"],
                os.environ["GF_SECURITY_ADMIN_PASSWORD"],
            ),
            host=os.environ["GF_SERVER_BASE_NAME"],
            port=os.environ["GF_SERVER_HTTP_PORT"],
        )

    @staticmethod
    def _get_experiment_config(experiment_id):
        filepath_experiment_yml = os.path.join(
            settings.DIR_EXPERIMENTS, f"{experiment_id}.yml"
        )
        try:
            with open(filepath_experiment_yml, "r") as experiment_yml:
                phase = yaml.safe_load(experiment_yml)["schedule"][0]
                experiment_params_path = list(phase.values())[0][
                    "environments"
                ][0]["environment"]["params"]
            start_date = experiment_params_path["params"]["start_date"]
            end = experiment_params_path["params"]["end"]
        except IOError as e:
            logger.error(
                f"cannot load erd file for experiment {experiment_id}. using default values for start_date and end",
                exc_info=e,
            )
            start_date = "2017-01-01 00:00:00+0100"
            end = "24*60*60"

        result = {"start_date": start_date, "end": end}

        return result
