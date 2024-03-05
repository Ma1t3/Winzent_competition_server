import logging
import socket
from pathlib import Path
from typing import Union, List

import numpy as np
import torch as T
from harl.ddpg.brain import DDPGBrain
from palaestrai.agent import SensorInformation, ActuatorInformation, Objective

LOG = logging.getLogger(__name__)


class PGASCDDPGBrain(DDPGBrain):
    """Brain for the DDPG algorithm that can be used on the Competition Server (extending hARL-Agent).
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

    def _remember(self, state, action, reward, next_state, done):
        self.memory.store_transition(
            state=np.array(state),
            action=np.array(action),
            reward=reward,
            state_=np.array([s() for s in next_state]),
            done=done,
        )

    def load_model(self, path):
        self.critic = T.load(f"{self.load_path}/ddpg_critic")
        self.actor = T.load(f"{self.load_path}/ddpg_actor")
        self.target_critic = T.load(f"{self.load_path}/ddpg_target_critic")
        self.target_actor = T.load(f"{self.load_path}/ddpg_target_actor")

    def store_model(self, path):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            LOG.warning(
                "Brain(id=0x%x) failed to create path to save model %s",
                id(self),
                str(e),
            )
            return

        T.save(self.critic, f"{self.server_store_path}/ddpg_critic")
        T.save(self.actor, f"{self.server_store_path}/ddpg_actor")
        T.save(
            self.target_actor,
            f"{self.server_store_path}/ddpg_target_actor",
        )
        T.save(
            self.target_critic,
            f"{self.server_store_path}/ddpg_target_critic",
        )
