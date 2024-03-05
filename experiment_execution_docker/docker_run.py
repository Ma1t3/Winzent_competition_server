import logging
import os
import subprocess
import asyncio
import palaestrai
from palaestrai.core import RuntimeConfig

logger = logging.getLogger(__name__)

"""
Script to run in the experiment docker container. The script installs requirements of defender and attacker agents,
re-installs Winzent (if in dev mode), enables palaestrAI-logging and runs the experiment in palaestrAI.
"""

if __name__ == "__main__":
    print("running")

    # print(f"file structure: {os.listdir('./')}")

    # installing requirements for attacker and defender
    for agent in ["attacker", "defender"]:
        requirements_filename = f"{agent}/requirements.txt"
        if os.path.isfile(requirements_filename):
            print(f"installing {requirements_filename}")
            subprocess.run(["pip", "install", "-r", requirements_filename])

    # print installed packages
    # print("installed packages:")
    # subprocess.run(["pip", "list"])
    if os.environ.get("EXPERIMENT_DEV_MODE", "False") == "True":
        print(
            "EXPERIMENT_DEV_MODE is activated: installing Winzent again to get the latest changes"
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "mango-library@git+https://gitlab.com/mango-agents/mango-library@e562140555b7f299ab98bdf21e084608c7eb5b93",
            ]
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "mango-agents==0.4.0",
            ]
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "palaestrai-mosaik==0.5.2",
            ]
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "mosaik==3.0.2",
            ]
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "mosaik-api==3.0.2",
            ]
        )
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "mosaik-simpy-io>=0.2.4",
            ]
        )
        # old: 0.4.0
        subprocess.run(
            [
                "pip",
                "install",
                "--upgrade",
                "--no-deps",
                "--force-reinstall",
                "protobuf==3.20.0",
            ]
        )
        # old: 3.20.0
    runtime_config = RuntimeConfig()

    # important: apply logging configuration of palaetrai runtime config. palaestrai does this NOT automatically!
    logging.config.dictConfig(runtime_config.logging)

    # load store_uri from enviroment variables
    host = os.environ["PALAESTRAI_DB_HOST"]
    user = os.environ["PALAESTRAI_DB_USER"]
    name = os.environ["PALAESTRAI_DB_NAME"]
    password = os.environ["PALAESTRAI_DB_PASSWORD"]
    port = os.environ["PALAESTRAI_DB_PORT"]
    runtime_config.load(
        {"store_uri": f"postgresql://{user}:{password}@{host}:{port}/{name}"}
    )

    print("running palaestrai")

    palaestrai.execute("erd.yml")

    print("execution of palaestrai done")
