import os
import shutil

import docker
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        This command is used to clean up the competition server.
        THIS WILL DELETE ALL USER DATA AND EXPERIMENT RESULTS ON THE SERVER!
        It will also remove migration files.
        """

        path = settings.BASE_DIR

        if not os.path.isdir(path):
            print(f"Dir {path} does not exist. Exiting...")
            raise SystemExit(1)

        # Delete migration files
        for appname in os.listdir(path):
            apppath = os.path.join(path, appname)
            appmigrations = os.path.join(apppath, "migrations")

            if os.path.isdir(appmigrations):
                print(f"Deleting migrations for {apppath}")
                for file in os.listdir(appmigrations):
                    filepath = os.path.join(appmigrations, file)
                    if (
                        os.path.isfile(filepath)
                        and file != "__init__.py"
                        and file[-3:] == ".py"
                    ):
                        print(f"File {file} deleted")
                        os.unlink(filepath)

        # Delete all user data
        if os.path.isdir(settings.DIR_USER_DATA):
            print(f"Delete {settings.DIR_USER_DATA}")
            shutil.rmtree(settings.DIR_USER_DATA)

        # Delete Temp directory
        if os.path.isdir(settings.DIR_TEMP):
            print(f"Delete {settings.DIR_TEMP}")
            shutil.rmtree(settings.DIR_TEMP)

        # Delete pgasc timescale volume
        docker_client = docker.from_env()
        ts_volume_list = docker_client.volumes.list(
            filters={"name": "pg-asc_timescale"}
        )
        if ts_volume_list:
            ts_volume = ts_volume_list[0]
            ts_volume.remove()
        else:
            print("Error: Timescale volume not found!")

        # Delete pgasc grafana volume
        ts_volume_list = docker_client.volumes.list(
            filters={"name": "pg-asc_grafana"}
        )
        if ts_volume_list:
            ts_volume = ts_volume_list[0]
            ts_volume.remove()
        else:
            print("Error: Grafana volume not found!")

        docker_client.close()

        print("cleanup finished.")
        print(
            "please execute docker-compose up now and recreate the containers"
        )
