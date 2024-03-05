import io
from pathlib import Path

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from palaestrai.util.syntax_validation import SyntaxValidationResult

from pgasc.web.agentsystemmanagement.models import Agent


class AgentUploadFormMan(forms.Form):
    """Form for uploading a new agent"""

    name = forms.CharField(label="Name", max_length=255, required=True)
    role = forms.ChoiceField(
        label="Role", choices=Agent.ROLE_CHOICES, required=True
    )
    description = forms.CharField(
        label="Description", widget=forms.Textarea, required=False
    )
    is_public = forms.BooleanField(label="Is public", required=False)
    file = forms.FileField(
        label="Agent files",
        help_text="<br/>Only .zip files allowed<br/>Max. 50MB compressed filesize",
        required=False,
    )
    init_yml = forms.CharField(
        label="Agent YAML for Competitions",
        widget=forms.Textarea,
        required=True,
        help_text="Drag and drop of a YAML file is possible.",
    )

    def clean(self):
        """Check if the Agent YAML is in the correct syntax"""
        cleaned_data = super().clean()
        if Agent.objects.filter(name=cleaned_data["name"]).exists():
            raise ValidationError(
                f"Agent with name {cleaned_data['name']} already exists."
            )

        # syntax validation of yaml
        try:
            result = SyntaxValidationResult.validate_syntax(
                io.StringIO(cleaned_data["init_yml"]),
                Path(
                    settings.BASE_DIR,
                    "yaml_validation_schemas",
                    "agent_schema.yml",
                ),
            )
            if result.is_valid:
                return cleaned_data
            else:
                raise ValidationError(result.error_message)
        except Exception as e:
            raise ValidationError(f"Please enter a valid YAML ({e})")


class ClassPathForm(forms.Form):
    """Form for modifying the agent yaml"""

    yml = forms.CharField(
        label=False,
        widget=forms.Textarea,
        required=True,
        help_text="Drag and drop of a YAML file is possible.",
    )

    def clean(self):
        """Check if the Agent YAML is in the correct syntax"""
        cleaned_data = super().clean()

        # syntax validation of yaml
        try:
            result = SyntaxValidationResult.validate_syntax(
                io.StringIO(cleaned_data["yml"]),
                Path(
                    settings.BASE_DIR,
                    "yaml_validation_schemas",
                    "agent_schema.yml",
                ),
            )
            if result.is_valid:
                return cleaned_data
            else:
                raise ValidationError(result.error_message)
        except Exception as e:
            raise ValidationError(f"Please enter a valid YAML ({e})")
