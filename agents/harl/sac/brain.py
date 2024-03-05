import socket
from pathlib import Path
from typing import Union, List

import numpy as np
import torch as T
from harl.sac.brain import SACBrain
from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
    Objective,
    LOG,
)


class PGASCSACBrain(SACBrain):
    """Brain for the SAC algorithm that can be used on the Competition Server (extending hARL-Agent).
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

    def _remember(self, readings, actions, reward, next_state, done):
        self.replay_buffer.add(
            state=np.array(readings),
            action=np.array(actions),
            reward=reward,
            next_state=np.array([s() for s in next_state]),
            done=done,
        )

    def load_model(self, path):
        self.actor = T.load(f"{self.load_path}/sac_actor")
        self.actor_target = T.load(f"{self.load_path}/sac_actor_target")
        self.critic = T.load(f"{self.load_path}/sac_critic")
        self.critic_target = T.load(f"{self.load_path}/sac_critic_target")

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

        T.save(self.actor, f"{self.server_store_path}/sac_actor")
        T.save(self.actor_target, f"{self.server_store_path}/sac_actor_target")
        T.save(self.critic, f"{self.server_store_path}/sac_critic")
        T.save(
            self.critic_target, f"{self.server_store_path}/sac_critic_target"
        )
