import io
from pathlib import Path

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Case, When, IntegerField, Q
from django.forms import ModelChoiceField
from django.forms import ModelForm
from palaestrai.util.syntax_validation import SyntaxValidationResult

from .models import ExperimentRun
from ..agentsystemmanagement.models import Agent


class AgentModelChoiceField(ModelChoiceField):
    def __init__(self, queryset, current_username, **kwargs):
        super().__init__(queryset, **kwargs)
        self.current_username = current_username

    def label_from_instance(self, obj):
        if obj.is_public and obj.owner.username != self.current_username:
            return f"{obj.name} by {obj.owner}"
        return obj.name


class ExperimentCreationForm(ModelForm):
    """Form for creating a new experiment."""

    class Meta:
        model = ExperimentRun
        fields = (
            "name",
            "defender",
            "store_trained_defender",
            "attacker",
            "store_trained_attacker",
            "erd",
            "is_public",
        )

    erd = forms.CharField(
        widget=forms.Textarea,
        label="Experiment Run Document",
        help_text="Drag and drop of a YAML file is possible.",
    )

    defender = AgentModelChoiceField(
        queryset=Agent.objects.none(), current_username="", initial=0
    )

    attacker = AgentModelChoiceField(
        queryset=Agent.objects.none(), current_username="", initial=0
    )

    def __init__(self, user, *args, **kwargs):
        super(ExperimentCreationForm, self).__init__(*args, **kwargs)

        self.fields["attacker"].queryset = (
            Agent.objects.filter(
                Q(owner=user) | Q(is_public=True),
                Q(role="A") | Q(role="B"),
            )
            .annotate(
                relevancy=Case(
                    When(owner=user, then=1), output_field=IntegerField()
                )
            )
            .order_by("relevancy", "-upload_timestamp")
        )
        self.fields["attacker"].current_username = user.username

        self.fields["defender"].queryset = (
            Agent.objects.filter(
                Q(owner=user) | Q(is_public=True),
                Q(role="D") | Q(role="B"),
            )
            .annotate(
                relevancy=Case(
                    When(owner=user, then=1), output_field=IntegerField()
                )
            )
            .order_by("relevancy", "-upload_timestamp")
        )
        self.fields["defender"].current_username = user.username

    def clean(self):
        """Check if the experiment name is unique and if the erd is a valid YAML file."""
        cleaned_data = super().clean()

        # for unique constraint
        if cleaned_data["name"].startswith("Competition"):
            raise ValidationError(
                "The name of the experiment must not start with 'Competition'."
            )

        # syntax validation of yaml
        try:
            result = SyntaxValidationResult.validate_syntax(
                io.StringIO(cleaned_data["erd"]),
                Path(
                    settings.BASE_DIR,
                    "yaml_validation_schemas",
                    "run_schema_experiment.yml",
                ),
            )
            if result.is_valid:
                return cleaned_data
            else:
                raise ValidationError(result.error_message)
        except Exception as e:
            raise ValidationError(f"Please enter a valid YAML ({e})")
