import logging
import signal
import time

from django.conf import settings
from django.db import connection, connections
from django.db.models import Case, When, IntegerField
from django.utils import timezone
from palaestrai.store.database_util import setup_database
from sqlalchemy.exc import DatabaseError

from pgasc.experiment_execution_scheduling.docker_management import (
    DockerManager,
)
from pgasc.web.competitiondefinitionmanagement.models import CompetitionRun
from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


class Scheduler:
    """
    Scheduler for experiments.
    Start and abort experiments, that are marked as such in the database.
    Finish experiments, if their execution in docker is done and the container is stopped.
    """

    def __init__(self):
        self.docker_manager = DockerManager()
        if settings.SCHEDULER_USABLE_GPUS:
            self.usable_gpus = settings.SCHEDULER_USABLE_GPUS.split(",")
        else:
            self.usable_gpus = None

        # https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
        self.exit = False
        signal.signal(signal.SIGINT, self.exit_scheduler)
        signal.signal(signal.SIGTERM, self.exit_scheduler)

    def _wait_for_image_build(self):
        """wait for experiment image builder to finish"""
        while not self.docker_manager.experiment_image_built():
            logger.info("Waiting for experiment docker image to be built.")
            time.sleep(settings.SCHEDULER_SLEEP_SECONDS_INITIALIZATION)
        logger.info("Experiment docker image built.")

    def _wait_for_migrations_finished(self):
        """wait for migrations to finish"""
        while (
            ExperimentRun._meta.db_table
            not in connection.introspection.table_names()
        ):
            time.sleep(settings.SCHEDULER_SLEEP_SECONDS_INITIALIZATION)
            logger.info("Waiting for ExperimentRun-table.")
        logger.info("ExperimentRun-table exists.")

    def _create_palaestrai_database_if_not_exists(self):
        """create palaestrai database if it does not exist"""
        try:
            host = settings.DATABASES["palaestrai"]["HOST"]
            port = settings.DATABASES["palaestrai"]["PORT"]
            user = settings.DATABASES["palaestrai"]["USER"]
            password = settings.DATABASES["palaestrai"]["PASSWORD"]
            name = settings.DATABASES["palaestrai"]["NAME"]
            palaestrai_database_url = (
                f"postgresql://{user}:{password}@{host}:{port}/{name}"
            )
            setup_database(palaestrai_database_url)
            logger.info("Created palaestrAI database.")
            self._create_episode_trigger()
            logger.info("Created episode trigger for palaestrAI database.")
        except DatabaseError as e:
            logger.info(
                "The palaestrAI database could not be created. Maybe it already exists."
            )
            logger.debug(f"Caught DatabaseError (can be intentional): {e}")

    @staticmethod
    def _create_episode_trigger():
        """create trigger for palaestrAI database to insert episodes for experiments into the database"""
        with connections["palaestrai"].cursor() as cursor:
            cursor.execute(
                "CREATE TABLE episodes (muscle_action_id INT PRIMARY KEY,episode INT NOT NULL);"
                "CREATE FUNCTION episode_checker() RETURNS trigger AS $BODY$ BEGIN IF NEW.simtimes::text != '{}'::TEXT AND NEW.rewards::text != '{}'::text THEN INSERT INTO episodes(muscle_action_id,episode) VALUES(NEW.id,(SELECT COUNT(simtimes)+1 FROM muscle_actions WHERE agent_id = NEW.agent_id AND simtimes::text = '{}'::TEXT)); RETURN NEW; ELSE RETURN NEW; END IF; END $BODY$ LANGUAGE 'plpgsql';"
                "CREATE TRIGGER episode_tracker AFTER INSERT ON muscle_actions FOR ROW EXECUTE PROCEDURE episode_checker();"
            )

    def scheduler_loop(self):
        """
        Activates the scheduler: Initializes the scheduler and starts the scheduler loop.
        The scheduler loop will run until the exit flag is set to True.
        If the exit flag is set to True, the scheduler will stop and properly shut down.
        """

        # initialize
        self._wait_for_image_build()
        self._wait_for_migrations_finished()
        self._create_palaestrai_database_if_not_exists()

        logger.info("Scheduler initialized.")

        # scheduler loop
        while not self.exit:
            logger.info("Check if experiments can be aborted.")
            any_exp_aborted = self._abort_experiments()

            logger.info("Check if experiments can be started.")
            # check if new experiment was added to queue
            any_exp_started = self._start_experiments()

            logger.info("Check if experiments can be finished.")
            # check if experiment execution in docker is done
            any_exp_finished = self._finish_experiments()

            if (
                not any_exp_started
                and not any_exp_aborted
                and not any_exp_finished
            ):
                logger.info(
                    f"Waiting {settings.SCHEDULER_SLEEP_SECONDS_LOOP} seconds ..."
                )
                time.sleep(settings.SCHEDULER_SLEEP_SECONDS_LOOP)

        # finish
        self.docker_manager.shutdown()
        logger.info("Finished scheduler.")

    def exit_scheduler(self, *args):
        """Method to exit the scheduler. This method is called when the scheduler receives a SIGINT or SIGTERM signal."""
        self.exit = True

    def _start_experiment(self, experiment, gpu_id):
        """
        Start the given experiment on the given gpu.
        Starts a docker container for the experiment and updates the database.
        """
        logger.info(f"starting experiment {experiment.id}")

        if not experiment.defender or not experiment.attacker:
            # cannot start experiment with deleted attacker or defender
            logger.info(
                f"experiment {experiment.id} cannot be started (attacker or defender missing)"
            )
            ExperimentRun.objects.filter(pk=experiment.pk).update(
                status="failed",
            )

            if experiment.competition is not None:
                self._update_competition_status(experiment.competition)
            return

        # start palaestrai container and get container id
        container_id = self.docker_manager.start_palaestrai_container(
            experiment, gpu_id
        )
        if container_id is None:
            # in case of an error: set experiment to failed
            ExperimentRun.objects.filter(pk=experiment.pk).update(
                status="failed",
            )

            if experiment.competition is not None:
                self._update_competition_status(experiment.competition)
            return

        # update experiment infos in db
        ExperimentRun.objects.filter(pk=experiment.pk).update(
            docker_container_id=container_id,
            gpu_id=gpu_id,
            timestamp_started=timezone.now(),
            status="running",
        )

        if (
            experiment.competition is not None
            and experiment.competition.status != "running"
        ):
            CompetitionRun.objects.filter(pk=experiment.competition.id).update(
                status="running"
            )

        logger.info(f"experiment {experiment.id} started")

    def _start_experiments(self):
        """
        Start the next experiment in the queue if existing and if enough resources are available.
        Of as available defined GPUs, choose the gpu with the least amount of experiments running on it.
        """
        # choose experiment to run next (FIFO)
        queue = (
            ExperimentRun.objects.filter(status="enqueued")
            .exclude(aborted_by_user=True)
            .order_by("timestamp_enqueued")
        )

        # start is not possible if queue is empty
        if not queue.exists():
            logger.info("No experiment to start.")
            return False

        # select GPU with the least number of running experiments
        if self.usable_gpus:
            running_containers_per_gpu = {
                gpu_id: ExperimentRun.objects.filter(
                    status="running", gpu_id=gpu_id
                ).count()
                for gpu_id in self.usable_gpus
            }
            gpu_id = min(
                running_containers_per_gpu, key=running_containers_per_gpu.get
            )
            running_containers = running_containers_per_gpu[gpu_id]
        else:
            running_containers = ExperimentRun.objects.filter(
                status="running"
            ).count()
            gpu_id = None

        if running_containers >= settings.SCHEDULER_EXPERIMENT_CAPACITY_PER_PU:
            logger.info("No experiment started. Capacity full.")
            return False

        # start next scheduled task
        self._start_experiment(queue[0], gpu_id)
        return True

    def _abort_experiments(self):
        """Check if experiments can be aborted. If so, abort them. First abort experiments that are enqueued, then running experiments."""
        experiments_to_abort = (
            ExperimentRun.objects.filter(aborted_by_user=True)
            .exclude(status="aborted")
            .annotate(
                status_order=Case(
                    When(status="enqueued", then=1),
                    When(status="running", then=2),
                    output_field=IntegerField(),
                ),
            )
            .order_by("status_order")
        )

        any_exp_aborted = False
        # check each experiment status: if enqueued, directly set status to aborted, else stop running container
        for experiment in experiments_to_abort:
            if (
                experiment.status == "enqueued"
                or experiment.status == "created"
            ):
                ExperimentRun.objects.filter(pk=experiment.pk).update(
                    status="aborted",
                )

                if experiment.competition is not None:
                    self._update_competition_status(experiment.competition)
                logger.info(f"experiment {experiment.id} aborted")
            elif experiment.status == "running":
                # exit container, finish experiment in function below
                container_id = experiment.docker_container_id
                self.docker_manager.stop_palaestrai_container(
                    experiment, container_id
                )
                logger.info(f"experiment {experiment.id} aborted")
            elif (
                experiment.status == "completed"
                or experiment.status == "failed"
            ):
                # Error handling: Completed or failed experiments cannot be aborted
                ExperimentRun.objects.filter(pk=experiment.pk).update(
                    aborted_by_user=False,
                )
                logger.info(
                    f"experiment {experiment.id} is already {experiment.status} and cannot be aborted."
                )

            any_exp_aborted = True

        return any_exp_aborted

    def _finish_experiments(self):
        """
        Check if experiments can be finished. If so, finish them.
        An experiment is finished if the docker container is exited.
        Update the experiment (and competition) status in the database.
        """
        running_experiments = ExperimentRun.objects.filter(status="running")

        any_exp_finished = False
        # check each task with running status
        for experiment in running_experiments:
            # check if container is exited
            container_id = experiment.docker_container_id
            if self.docker_manager.is_palaestrai_container_exited(
                container_id
            ):
                # finish palaestrai container and get successful state
                successful = self.docker_manager.finish_palaestrai_container(
                    experiment, container_id
                )

                # update experiment status in db
                if experiment.aborted_by_user:
                    status = "aborted"
                else:
                    if successful:
                        status = "completed"
                    else:
                        status = "failed"

                ExperimentRun.objects.filter(pk=experiment.pk).update(
                    docker_container_id=None,
                    timestamp_finished=timezone.now(),
                    status=status,
                )

                if experiment.competition is not None:
                    self._update_competition_status(experiment.competition)

                any_exp_finished = True
                logger.info(f"experiment {experiment.id} finished")

        return any_exp_finished

    @staticmethod
    def _update_competition_status(competition):
        """
        Update the competition status in the database.
        If there is still at least one experiment running or enqueued, the competition status remains running or enqueued.
        Else-If any experiment is aborted, the competition status is set to aborted.
        Else-If any experiment is failed, the competition status is set to failed.
        Else (=> all experiments of a competition are successful) the competition status is set to completed.
        """
        # check if any experiment is not yet finished
        if (
            ExperimentRun.objects.filter(
                competition=competition, timestamp_finished=None
            )
            .exclude(status="aborted")
            .exclude(status="failed")
            .exists()
        ):
            # status remains "running" or "enqueued" (no update)
            pass
        # else: check if any experiment is aborted
        elif ExperimentRun.objects.filter(
            competition=competition, status="aborted"
        ).exists():
            # competition status is "aborted"
            CompetitionRun.objects.filter(pk=competition.id).update(
                status="aborted"
            )
        # else: check if any experiment is failed
        elif ExperimentRun.objects.filter(
            competition=competition, status="failed"
        ).exists():
            # competition status is "failed"
            CompetitionRun.objects.filter(pk=competition.id).update(
                status="failed"
            )
        else:
            # else: competition status is completed
            CompetitionRun.objects.filter(pk=competition.id).update(
                status="completed"
            )
