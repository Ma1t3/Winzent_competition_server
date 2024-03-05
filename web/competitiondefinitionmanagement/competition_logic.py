import yaml

from pgasc.web.agentsystemmanagement import directly_usable_paths
from pgasc.web.competitiondefinitionmanagement.models import CompetitionRun
from pgasc.web.experimentdefinitionmanagement.experiment_logic import (
    create_experiment_run_files,
)
from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun


def get_modified_agent_yaml_dict(agent, role):
    """Returns a modified version of the agent yaml file, where the role of the agents is integrated in the path of brain/muscle/objective."""

    # add correct name
    agent_yaml_dict = {"name": agent.name}

    # load agent yaml
    agent_yaml_dict.update(yaml.safe_load(agent.init_yml))

    # check if "attacker" or "defender" has to be added to brain/muscle/objective-path
    path_brain = agent_yaml_dict["brain"]["name"]
    if path_brain not in directly_usable_paths.brains:
        agent_yaml_dict["brain"]["name"] = f"{role}.{path_brain}"

    path_muscle = agent_yaml_dict["muscle"]["name"]
    if path_muscle not in directly_usable_paths.muscles:
        agent_yaml_dict["muscle"]["name"] = f"{role}.{path_muscle}"

    path_objective = agent_yaml_dict["objective"]["name"]
    if path_objective not in directly_usable_paths.objectives:
        agent_yaml_dict["objective"]["name"] = f"{role}.{path_objective}"

    # return modified dictionary
    return agent_yaml_dict


def create_experiment(competition, attacker, defender):
    """
    Create a new experiment for the given attacker and defender in the competition.
    Use modified versions of the agent yaml files in the experiment erd (based on the competition run document).
    """
    experiment_name = (
        f"Competition {competition.name}: {attacker.name} vs. {defender.name}"
    )

    experiment = ExperimentRun(
        name=experiment_name,
        defender=defender,
        store_trained_defender=False,
        attacker=attacker,
        store_trained_attacker=False,
        competition=competition,
        owner=competition.owner,
        is_public=competition.is_public,
    )
    experiment.save()

    # add modified versions of the agent yamls to a list
    agent_list = []
    attacker_yaml_dict = get_modified_agent_yaml_dict(attacker, "attacker")
    defender_yaml_dict = get_modified_agent_yaml_dict(defender, "defender")
    agent_list.append(attacker_yaml_dict)
    agent_list.append(defender_yaml_dict)

    # load competition erd yaml
    erd_as_dict = yaml.safe_load(competition.erd)
    for phase in erd_as_dict["schedule"]:
        # for every phase: add all agents
        list(phase.values())[0]["agents"] = agent_list

    erd_as_str = yaml.dump(erd_as_dict, sort_keys=False)
    create_experiment_run_files(experiment, erd_as_str)


def create_experiments_for_competition(competition: CompetitionRun):
    """For every combination of attacker and defender in the competition, create an experiment."""
    for attacker in competition.attacker.all():
        for defender in competition.defender.all():
            create_experiment(competition, attacker, defender)
