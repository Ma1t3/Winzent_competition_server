import logging
import os
import shutil
import tarfile
from io import BytesIO
from typing import Optional, Tuple

import docker
import yaml
from django.conf import settings
from docker.errors import NotFound, ImageNotFound

from pgasc.web.agentsystemmanagement import agent_logic
from pgasc.web.agentsystemmanagement.models import Agent
from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


# SDK used in this file: https://docker-py.readthedocs.io/en/stable/containers.html


class DockerManager:
    """Class to provide all docker related functionality to the scheduler"""

    IMAGE_NAME = "pg-asc_experiment"
    IMAGE_BUILDER_NAME = "experiment_image_builder"
    NETWORK_NAME = "pg-asc_default"

    def __init__(self) -> None:
        self.client = docker.from_env()

    def shutdown(self):
        """shutdown docker client"""
        self.client.close()

    def _experiment_image_exists(self):
        try:
            self.client.images.get(DockerManager.IMAGE_NAME)
            return True
        except ImageNotFound:
            logger.error("No experiment image found.")
            return False

    def experiment_image_built(self) -> bool:
        """Returns True if the experiment image builder is finished and the experiment image is built, otherwise or in case of an error False"""
        containers = self.client.containers.list(
            all=True, filters={"name": DockerManager.IMAGE_BUILDER_NAME}
        )
        if len(containers) != 0:
            container = containers[0]
            if container.status == "exited":
                return self._experiment_image_exists()
            return False
        else:
            logger.error("Container not found")
            return False

    def is_palaestrai_container_exited(self, container_id: str) -> bool:
        """Returns True if the container with the given id is exited, otherwise or in case of an error False"""
        try:
            container = self.client.containers.get(container_id)
            return container.status == "exited"
        except NotFound:
            logger.error("Container not found")
            return False

    def start_palaestrai_container(
        self, experiment: ExperimentRun, gpu_id: Optional[int] = None
    ) -> Optional[str]:
        """
        Starts the palaestrai container for the given experiment and returns the container id
        - if given, use the gpu with the gpu_id, else use the cpu
        - create a new container with the experiment image
        - copy the attacker and defender files to the container
        - copy the experiment definition file and midas yml to the container
        - if in dev mode, recopy the agents and midas directory to the container
        - attach the container to the network
        - start the container
        - return the container id
        - if an error occurs, delete created container and return None
        """
        environment = [
            f"PALAESTRAI_DB_NAME={settings.DATABASES['palaestrai']['NAME']}",
            f"PALAESTRAI_DB_USER={settings.DATABASES['palaestrai']['USER']}",
            f"PALAESTRAI_DB_PASSWORD={settings.DATABASES['palaestrai']['PASSWORD']}",
            f"PALAESTRAI_DB_HOST={settings.DATABASES['palaestrai']['HOST']}",
            f"PALAESTRAI_DB_PORT={settings.DATABASES['palaestrai']['PORT']}",
            f"MIDAS_DB_NAME={settings.DATABASES['midas']['NAME']}",
            f"MIDAS_DB_USER={settings.DATABASES['midas']['USER']}",
            f"MIDAS_DB_PASSWORD={settings.DATABASES['midas']['PASSWORD']}",
            f"MIDAS_DB_HOST={settings.DATABASES['midas']['HOST']}",
            f"MIDAS_DB_PORT={settings.DATABASES['midas']['PORT']}",
            f"EXPERIMENT_DEV_MODE={settings.EXPERIMENT_DEV_MODE}",
        ]

        if gpu_id is not None:
            environment.append(f"NVIDIA_VISIBLE_DEVICES={gpu_id}")
            container = self.client.containers.create(
                DockerManager.IMAGE_NAME,
                labels=["experiment"],
                command=["python", "docker_run.py"],
                runtime="nvidia",
                environment=environment,
            )
        else:
            container = self.client.containers.create(
                DockerManager.IMAGE_NAME,
                labels=["experiment"],
                command=["python", "docker_run.py"],
                environment=environment,
            )

        try:
            # copy agent system files and erd
            defender_id = experiment.defender.id
            attacker_id = experiment.attacker.id
            experiment_id = experiment.id

            # Documentation and hints:
            # https://stackoverflow.com/questions/53743886/create-docker-from-tar-with-python-docker-api
            # https://docs.python.org/3/library/tarfile.html
            # https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.put_archive

            # copy defender
            with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                tar.add(
                    os.path.join(settings.DIR_AGENTS, str(defender_id)),
                    arcname="defender",
                )
                container.put_archive("/app/", tar.fileobj.getvalue())

            # copy attacker
            with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                tar.add(
                    os.path.join(settings.DIR_AGENTS, str(attacker_id)),
                    arcname="attacker",
                )
                container.put_archive("/app/", tar.fileobj.getvalue())

            # copy erd
            with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                tar.add(
                    os.path.join(
                        settings.DIR_EXPERIMENTS, f"{experiment_id}.yml"
                    ),
                    arcname="erd.yml",
                )
                container.put_archive("/app/", tar.fileobj.getvalue())

            # copy midas yml
            with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                tar.add(
                    os.path.join(
                        settings.DIR_EXPERIMENTS, f"{experiment_id}_midas.yml"
                    ),
                    arcname="bhv_midas.yml",
                )
                container.put_archive("/app/", tar.fileobj.getvalue())

            if settings.SCHEDULER_DEV_MODE:
                # Copy some directories again (that are already in the Docker image)
                # for development to avoid rebuilding the image

                # copy pgasc agents
                with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                    tar.add("./pgasc/agents/", arcname="pgasc/agents")
                    container.put_archive("/app/", tar.fileobj.getvalue())

                # copy experiment_execution_docker directory
                with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                    tar.add("./pgasc/experiment_execution_docker/", arcname="")
                    container.put_archive("/app/", tar.fileobj.getvalue())

                # copy midas directory
                with tarfile.open(fileobj=BytesIO(), mode="w") as tar:
                    tar.add("./pgasc/midas/", arcname="pgasc/midas")
                    container.put_archive("/app/", tar.fileobj.getvalue())

            # connect to network
            self.client.networks.get(DockerManager.NETWORK_NAME).connect(
                container
            )

            # start container
            container.start()

            logger.info(
                f"Started Container {container.id} with experiment {experiment_id}"
            )

            # return container id
            return container.id

        except Exception as e:
            # in case of an error: delete container
            container.remove()
            logger.error(
                f"experiment {experiment.id} cannot be started.", exc_info=e
            )
            return None

    def stop_palaestrai_container(
        self, experiment: ExperimentRun, container_id: str
    ):
        """abort/stop the container with the given id"""
        container = self.client.containers.get(container_id)
        container.stop()
        logger.info(
            f"Stopped Container {container_id} with experiment {experiment.id}"
        )

    def finish_palaestrai_container(
        self, experiment: ExperimentRun, container_id: str
    ) -> bool:
        """
        Finish the container with the given id.
        - save the experiment logs to a file
        - if the experiment was successful and the trained agent should be saved, save the agent (for attacker, defender)
        - remove the container
        - return True if the experiment was successful, False otherwise
        """
        logger.info(
            f"Finishing Container {container_id} with experiment {experiment.pk}"
        )
        container = self.client.containers.get(container_id)

        # save container log in file system and db
        experiment_successful = self._save_experiment_log(
            experiment, container
        )

        # if docker run was successful and agent system should be trained, create new, trained agent system
        if experiment_successful:
            (
                attacker_yml,
                defender_yml,
            ) = self._get_attacker_and_defender_from_erd(experiment)
            if experiment.store_trained_attacker and experiment.attacker:
                self._save_trained_agent(
                    experiment,
                    container,
                    "attacker",
                    attacker_yml,
                )
            if experiment.store_trained_defender and experiment.defender:
                self._save_trained_agent(
                    experiment,
                    container,
                    "defender",
                    defender_yml,
                )

        # delete experiment docker container
        container.remove()
        return experiment_successful

    @staticmethod
    def _create_unique_name(old_name: str, agent_type: str) -> str:
        """creates a unique name for the trained agent"""
        version = 1
        old_name = old_name.replace(" (untrained)", "")
        name = f"{old_name} (trained {agent_type}) {version}"
        # check if name is unique
        while Agent.objects.filter(name=name).exists():
            version += 1
            name = f"{old_name} (trained {agent_type}) {version}"
        return name

    @staticmethod
    def _get_attacker_and_defender_from_erd(
        experiment: ExperimentRun,
    ) -> Tuple[Optional[str], Optional[str]]:
        """load the erd and return the attacker and defender yml"""
        try:
            erd_path = os.path.join(
                settings.DIR_EXPERIMENTS, f"{experiment.pk}_user.yml"
            )
            with open(erd_path, "r") as file:
                erd = file.read()
            erd_as_dict = yaml.safe_load(erd)
            # use the agent's yaml from the first phase
            phase = erd_as_dict["schedule"][0]
            agents = list(phase.values())[0]["agents"]
            attacker_yml = None
            defender_yml = None
            for agent in agents:
                if agent["name"] == "evil_attacker":
                    agent.pop("name")
                    attacker_yml = yaml.dump(agent, sort_keys=False)
                elif agent["name"] == "mighty_defender":
                    agent.pop("name")
                    defender_yml = yaml.dump(agent, sort_keys=False)
            return attacker_yml, defender_yml
        except (IOError, KeyError) as e:
            logger.error(
                f"cannot extract agent yml from experiment {experiment.pk} erd.",
                exc_info=e,
            )
            return None, None

    def _save_trained_agent(
        self,
        experiment: ExperimentRun,
        container,
        agent_type: str,
        agent_yml: Optional[str],
    ):
        """create a new agent system with the trained agent and use the yaml from the experiment"""
        logger.info("Save Trained Agent")
        # save trained agent as new agent in web db

        if agent_type == "attacker":
            old_name = experiment.attacker.name
            name = self._create_unique_name(old_name, agent_type)
            role = "A"
            description = (
                f"Original Description: {experiment.attacker.description}"
            )
            is_public = experiment.attacker.is_public
            owner = experiment.owner
            if agent_yml:
                init_yml = agent_yml
            else:
                init_yml = experiment.attacker.init_yml
        else:
            old_name = experiment.defender.name
            name = self._create_unique_name(old_name, agent_type)
            role = "D"
            description = (
                f"Original Description: {experiment.defender.description}"
            )
            is_public = experiment.defender.is_public
            owner = experiment.owner
            if agent_yml:
                init_yml = agent_yml
            else:
                init_yml = experiment.defender.init_yml

        agent = Agent(
            name=name,
            role=role,
            description=description,
            is_public=is_public,
            owner=owner,
            init_yml=init_yml,
            trained_by=experiment,
        )

        agent.save()

        # get tar archive from /attacker or /defender dir in container
        try:
            bits, stat = container.get_archive(f"/app/{agent_type}/")
        except docker.errors.APIError:
            logger.error(
                "APIError: trained agent could not be retrieved from the container."
            )
            return

        # make sure Temp directory exists
        if not os.path.exists(settings.DIR_TEMP):
            os.makedirs(settings.DIR_TEMP)
        # write bits in temporary tar file
        tar_path = os.path.join(settings.DIR_TEMP, "agent.tar")
        with open(tar_path, "wb") as fileobject:
            for chunk in bits:
                fileobject.write(chunk)

        # extract the tar file in the filesystem
        extracted_path = os.path.join(settings.DIR_TEMP, "extracted")
        with tarfile.open(name=tar_path, mode="r") as tar:
            tar.extractall(path=extracted_path)

        # remove temporary tar file
        os.remove(tar_path)
        # for the right structure: move the content and delete the temporary directory
        shutil.copytree(
            src=os.path.join(extracted_path, agent_type),
            dst=os.path.join(settings.DIR_AGENTS, str(agent.pk)),
        )
        shutil.rmtree(extracted_path)

        agent_logic.set_readonly_if_classes_exist(agent)

    def _save_experiment_log(self, experiment, container):
        """save the logs of the container of the given experiment to a file"""
        logger.debug(f"Save experiment log for experiment {experiment.pk}")
        successful = True
        try:
            stat = container.logs()
            logs = stat.decode("utf-8")
            if "CRITICAL" in logs[-10_000:]:
                successful = False
        except docker.errors.APIError:
            logger.error("APIError: log could not be saved.")
            return

        if not os.path.exists(settings.DIR_EXPERIMENT_LOGS):
            os.makedirs(settings.DIR_EXPERIMENT_LOGS)
        path = os.path.join(
            settings.DIR_EXPERIMENT_LOGS, f"{experiment.pk}.log"
        )
        with open(path, "w") as text_file:
            text_file.write(logs)
        return successful
