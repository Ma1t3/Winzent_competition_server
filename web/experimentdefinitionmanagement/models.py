from django.conf import settings
from django.db import models

from pgasc.web.agentsystemmanagement.models import Agent
from pgasc.web.competitiondefinitionmanagement.models import CompetitionRun


class ExperimentRun(models.Model):
    # user defined parameters
    name = models.CharField(max_length=255, unique=True)

    defender = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        related_name="defenders_received",
    )
    store_trained_defender = models.BooleanField(
        verbose_name="Store copy of trained defender", default=False
    )

    attacker = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        default=1,
        related_name="attackers_received",
    )
    store_trained_attacker = models.BooleanField(
        verbose_name="Store copy of trained attacker", default=False
    )

    competition = models.ForeignKey(
        CompetitionRun,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )

    is_public = models.BooleanField(default=False)

    # automatically inserted parameters
    status = models.CharField(max_length=20, default="created")

    aborted_by_user = models.BooleanField(default=False)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )

    timestamp_created = models.DateTimeField(auto_now_add=True)

    timestamp_enqueued = models.DateTimeField(
        default=None, blank=True, null=True
    )

    timestamp_started = models.DateTimeField(
        default=None, blank=True, null=True
    )

    timestamp_finished = models.DateTimeField(
        default=None, blank=True, null=True
    )

    docker_container_id = models.CharField(
        max_length=64, default=None, blank=True, null=True
    )

    gpu_id = models.IntegerField(default=None, blank=True, null=True)
