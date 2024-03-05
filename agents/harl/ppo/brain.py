import socket
from pathlib import Path
from typing import List, Union

import torch as T
from harl.ppo.brain import PPOBrain
from palaestrai.agent import (
    Objective,
    SensorInformation,
    ActuatorInformation,
    LOG,
)


class PGASCPPOBrain(PPOBrain):
    """Brain for the PPO algorithm that can be used on the Competition Server (extending hARL-Agent).
    The Brain is compatible with "server_store_path" and "load_path"."""

    def __init__(
        self,
        muscle_updates_listen_uri_or_socket: Union[str, socket.socket],
        sensors: List[SensorInformation],
        actuators: List[ActuatorInformation],
        objective: Objective,
        store_path: str,
        seed: int,
        **params,
    ):
        super().__init__(
            muscle_updates_listen_uri_or_socket,
            sensors,
            actuators,
            objective,
            store_path,
            seed,
            **params,
        )

        self.load_path = params.get("load_path")
        self.server_store_path = params.get("server_store_path")

    def load_model(self, path):
        self.critic = T.load(f"{self.load_path}/ppo_critic")
        self.actor = T.load(f"{self.load_path}/ppo_actor")

    def store_model(self, path):
        try:
            Path(self.server_store_path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            LOG.warning(
                "Brain(id=0x%x) failed to create path to save model %s",
                id(self),
                str(e),
            )
            return

        T.save(self.critic, f"{self.server_store_path}/ppo_critic")
        T.save(self.actor, f"{self.server_store_path}/ppo_actor")
