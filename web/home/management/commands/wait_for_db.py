import logging
import time

from django.core.management.base import BaseCommand
from django.db import connection, OperationalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Command to wait for database to be fully initialized and available."""

        # adapted from https://github.com/pinae/MicroBotBlog/blob/main/projectBlog/microblog/management/commands/wait_for_db.py
        WAITING_SECONDS = 5
        logger.info("Checking djangodb connection...")
        db_connected = False
        while not db_connected:
            try:
                connection.ensure_connection()
                db_connected = True
            except OperationalError:
                logger.info(
                    f"Connection to database failed. Waiting for {WAITING_SECONDS} seconds."
                )
                time.sleep(WAITING_SECONDS)
        logger.info("Database available.")
