import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from pgasc.web.home import create_defaults

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Command to create default agents (test agents, winzent and untrained hARL agents)."""

        logger.info("Creating default user and agents.")

        default_username = "PG-ASC"

        user = create_defaults.create_default_user(
            username=default_username,
            password="no-password",
            email="testuser@pgasc.local",
            is_active=False,
        )

        create_defaults.create_default_agent(
            name="Set-Nothing-Agent",
            description="This is an agent that does nothing.",
            role="B",
            owner=user,
            init_yml="""brain:
    name: palaestrai.agent.dummy_brain:DummyBrain
    params: {}
muscle:
    name: pgasc.agents.palaestrai_test_agents.muscles:SetNothingMuscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
        )

        create_defaults.create_default_agent(
            name="Setpoint-Agent",
            description="This is an agent that sets all actuators to the given setpoint in every iteration.",
            role="B",
            owner=user,
            init_yml="""brain:
    name: palaestrai.agent.dummy_brain:DummyBrain
    params: {}
muscle:
    name: pgasc.agents.palaestrai_test_agents.muscles:SetpointMuscle
    params: { "setpoint": 0.5 }
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
        )

        create_defaults.create_default_agent(
            name="Save-Values-Agent",
            description="This is an agent that saves its inputs in a file (only usable as defender).",
            role="D",
            owner=user,
            init_yml="""brain:
    name: palaestrai.agent.dummy_brain:DummyBrain
    params: {}
muscle:
    name: pgasc.agents.palaestrai_test_agents.muscles:SaveValuesMuscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
        )

        create_defaults.create_default_agent(
            name="palaestrAI Dummy Agent (without sensors and actuators)",
            description="This is a dummy agent imported from palaestrAI with example sensors and actuators.",
            role="B",
            owner=user,
            init_yml="""brain:
    name: palaestrai.agent.dummy_brain:DummyBrain
    params: {}
muscle:
    name: palaestrai.agent.dummy_muscle:DummyMuscle
    params: {}
objective:
    name: palaestrai.agent.dummy_objective:DummyObjective
    params: {"params": 1}
sensors: []
actuators: []""",
        )

        path = os.path.join(
            settings.BASE_DIR, "yaml_defaults", "agent_yaml_winzent.yml"
        )
        with open(path, "r") as file:
            default_agent_yml = file.read()
        create_defaults.create_default_agent(
            name="Winzent",
            description="This is WINZENT.",
            role="D",
            owner=user,
            init_yml=default_agent_yml,
        )

        create_defaults.create_default_agent(
            name="DDPG-Agent (untrained)",
            description="This is a hARL agent with Deep Deterministic Policy Gradient as learning algorithm. ",
            role="B",
            owner=user,
            init_yml="""brain:
    name: pgasc.agents.harl.ddpg.brain:PGASCDDPGBrain
    params: {}
muscle:
    name: pgasc.agents.harl.ddpg.muscle:PGASCDDPGMuscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
            set_readonly_if_classes_exist=False,
        )

        create_defaults.create_default_agent(
            name="PPO-Agent (untrained)",
            description="This is a hARL agent with Proximal Policy Optimization as learning algorithm. ",
            role="B",
            owner=user,
            init_yml="""brain:
    name: pgasc.agents.harl.ppo.brain:PGASCPPOBrain
    params: {}
muscle:
    name: pgasc.agents.harl.ppo.muscle:PGASCPPOMuscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
            set_readonly_if_classes_exist=False,
        )

        create_defaults.create_default_agent(
            name="SAC-Agent (untrained)",
            description="This is a hARL agent with Soft Actor-Critic as learning algorithm. ",
            role="B",
            owner=user,
            init_yml="""brain:
    name: pgasc.agents.harl.sac.brain:PGASCSACBrain
    params: {}
muscle:
    name: pgasc.agents.harl.sac.muscle:PGASCSACMuscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
            set_readonly_if_classes_exist=False,
        )

        create_defaults.create_default_agent(
            name="TD3-Agent (untrained)",
            description="This is a hARL agent with Twin Delayed DDPG as learning algorithm. ",
            role="B",
            owner=user,
            init_yml="""brain:
    name: pgasc.agents.harl.td3.brain:PGASCTD3Brain
    params: {}
muscle:
    name: pgasc.agents.harl.td3.muscle:PGASCTD3Muscle
    params: {}
objective:
    name: pgasc.agents.harl.base.objective:DummyObjective
    params: {}
sensors: []
actuators: []""",
            set_readonly_if_classes_exist=False,
        )

        logger.info("Creating default user and agents finished.")
