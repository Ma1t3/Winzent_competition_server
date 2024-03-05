import ast
import os

import yaml
from django.conf import settings

from pgasc.web.agentsystemmanagement import directly_usable_paths


def set_readonly_if_classes_exist(agent):
    """Checks if the paths in the agent yaml are valid and sets the flag in the database accordingly"""
    agent_dict = yaml.safe_load(agent.init_yml)
    path_brain = agent_dict["brain"]["name"]
    path_muscle = agent_dict["muscle"]["name"]
    path_objective = agent_dict["objective"]["name"]

    brain_exists = check_class_exists(agent.id, path_brain)
    muscle_exists = check_class_exists(agent.id, path_muscle)
    objective_exists = check_class_exists(agent.id, path_objective)

    agent.path_brain_is_correct = False
    agent.path_muscle_is_correct = False
    agent.path_objective_is_correct = False

    # Check if the Paths are correct (class exists or directly usable)
    if brain_exists or path_brain in directly_usable_paths.brains:
        agent.path_brain_is_correct = True
    if muscle_exists or path_muscle in directly_usable_paths.muscles:
        agent.path_muscle_is_correct = True
    if objective_exists or path_objective in directly_usable_paths.objectives:
        agent.path_objective_is_correct = True

    agent.save()


def check_class_exists(agent_id, path):
    """check if the class exists in the file"""
    base_path = os.path.join(settings.DIR_AGENTS, str(agent_id))

    class_exists = None
    if path:
        path = path.replace(".", "/")
        fullpath = os.path.join(base_path, path)
        class_exists = __check_class(fullpath)

    return class_exists


def __check_class(path):
    path_split = path.split(":")
    if len(path_split) < 2:
        return False

    filepath = path_split[0] + ".py"
    classname = path_split[1]

    if not os.path.exists(filepath):
        return False
    with open(filepath) as file:
        node = ast.parse(file.read())

    classes = [n.name for n in node.body if isinstance(n, ast.ClassDef)]

    return classname in classes
