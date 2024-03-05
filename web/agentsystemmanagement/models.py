from django.conf import settings
from django.db import models


class Agent(models.Model):
    ROLE_CHOICES = (
        ("B", "Attacker/Defender"),
        ("A", "Attacker"),
        ("D", "Defender"),
    )

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default=None, blank=True, null=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default="B")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    is_public = models.BooleanField(default=False)
    upload_timestamp = models.DateTimeField(auto_now_add=True)

    init_yml = models.TextField(default=None, blank=True)

    path_brain_is_correct = models.BooleanField(default=False)
    path_muscle_is_correct = models.BooleanField(default=False)
    path_objective_is_correct = models.BooleanField(default=False)

    trained_by = models.ForeignKey(
        "experimentdefinitionmanagement.ExperimentRun",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        blank=True,
        related_name="trained_agents",
    )
