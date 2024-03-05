import logging

import django.contrib.auth.hashers

from pgasc.web.agentsystemmanagement import agent_files, agent_logic
from pgasc.web.agentsystemmanagement.models import Agent
from pgasc.web.usermanagement.models import CustomUser

logger = logging.getLogger(__name__)


def create_default_user(username, password, email, is_active=False):
    """Create a default user with the given username, password and email address."""
    user = CustomUser.objects.filter(username=username)
    if user.exists():
        user = user[0]
        logger.info(f"Default user '{username}' already exists.")
    else:
        user = CustomUser()
        user.username = username
        user.password = django.contrib.auth.hashers.make_password(password)
        user.email = email
        user.organization = "UOL"
        user.is_active = is_active
        user.save()
        logger.info(f"Default user '{username}' created.")
    return user


def create_default_agent(
    name,
    description,
    role,
    owner,
    init_yml,
    set_readonly_if_classes_exist=True,
):
    """Create a default agent with the given name, description, role, owner and init_yml."""
    agent = Agent.objects.filter(name=name, owner=owner)
    if agent.exists():
        agent = agent[0]
        logger.info(
            f"Default Agent '{name}' already exists. Owner is '{agent.owner.username}'."
        )
    else:
        agent = Agent()
        agent.name = name
        agent.description = description
        agent.role = role
        agent.owner = owner
        agent.is_public = True
        agent.init_yml = init_yml
        agent.save()

        agent_files.save_agent_files(agent.pk, None)
        if set_readonly_if_classes_exist:
            agent_logic.set_readonly_if_classes_exist(agent)

        logger.info(f"Default agent '{name}' added.")

    return agent
