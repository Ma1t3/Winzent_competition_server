from django import forms
from django.db.models import Case, When, IntegerField, Q
from django.forms import ModelForm

from pgasc.web.agentsystemmanagement.models import Agent
from .models import CompetitionRun


class AgentNameMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, agent: Agent):
        return agent.name


class CompetitionCreationForm(ModelForm):
    """Form for creating a new competition"""

    class Meta:
        model = CompetitionRun
        fields = ("name", "erd", "is_public", "defender", "attacker")

    def __init__(self, user, *args, **kwargs):
        super(CompetitionCreationForm, self).__init__(*args, **kwargs)

        # filter the defender and attacker and only show agents with correct paths
        self.fields["attacker"].queryset = (
            Agent.objects.filter(
                Q(owner=user) | Q(is_public=True),
                Q(role="A") | Q(role="B"),
                path_brain_is_correct=True,
                path_muscle_is_correct=True,
                path_objective_is_correct=True,
            )
            .annotate(
                relevancy=Case(
                    When(owner=user, then=1), output_field=IntegerField()
                )
            )
            .order_by("relevancy", "-upload_timestamp")
        )

        self.fields["defender"].queryset = (
            Agent.objects.filter(
                Q(owner=user) | Q(is_public=True),
                Q(role="D") | Q(role="B"),
                path_brain_is_correct=True,
                path_muscle_is_correct=True,
                path_objective_is_correct=True,
            )
            .annotate(
                relevancy=Case(
                    When(owner=user, then=1), output_field=IntegerField()
                )
            )
            .order_by("relevancy", "-upload_timestamp")
        )

    defender = AgentNameMMCF(
        queryset=Agent.objects.none(), widget=forms.CheckboxSelectMultiple
    )

    attacker = AgentNameMMCF(
        queryset=Agent.objects.none(), widget=forms.CheckboxSelectMultiple
    )
