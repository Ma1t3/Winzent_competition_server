from django.core.management.base import BaseCommand

from pgasc.experiment_execution_scheduling.scheduler import Scheduler


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Command to start the scheduler."""
        Scheduler().scheduler_loop()
