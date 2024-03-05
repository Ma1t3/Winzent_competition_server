import io
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from palaestrai.util.syntax_validation import SyntaxValidationResult

from pgasc.web.agentsystemmanagement.models import Agent


class CompetitionRun(models.Model):
    # user defined parameters
    name = models.CharField(max_length=255, unique=True)

    erd = models.TextField(
        default=None,
        verbose_name="Competition Run Document (ERD without agents)",
        help_text="Drag and drop of a YML file is possible.",
    )

    is_public = models.BooleanField(default=False)

    # automatically inserted parameters
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )

    timestamp_created = models.DateTimeField(auto_now_add=True)

    defender = models.ManyToManyField(
        Agent, related_name="defender_competition"
    )

    attacker = models.ManyToManyField(
        Agent, related_name="attackers_competition"
    )

    status = models.CharField(max_length=20, default="created")

    aborted_by_user = models.BooleanField(default=False)

    def clean(self):
        """Check if the ERD is in the correct syntax"""
        super().clean()
        try:
            result = SyntaxValidationResult.validate_syntax(
                io.StringIO(self.erd),
                Path(
                    settings.BASE_DIR,
                    "yaml_validation_schemas",
                    "run_schema_competition.yml",
                ),
            )
            if result.is_valid:
                return True
            else:
                raise ValidationError(result.error_message)
        except Exception as e:
            raise ValidationError(f"Please enter a valid YAML ({e})")
