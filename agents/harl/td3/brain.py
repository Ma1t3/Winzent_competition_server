import socket
from pathlib import Path
from typing import List, Union

import numpy as np
import torch as T
from harl.TD3.brain import TD3Brain
from palaestrai.agent import (
    SensorInformation,
    ActuatorInformation,
    Objective,
    LOG,
)
from palaestrai.core.protocol import MuscleUpdateResponse
from palaestrai.util.exception import NoneInputError


class PGASCTD3Brain(TD3Brain):
    """Brain for the TD3 algorithm that can be used on the Competition Server (extending hARL-Agent).
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

    def thinking(
        self,
        muscle_id,
        readings,
        actions,
        reward,
        next_state,
        done,
        additional_data,
    ) -> MuscleUpdateResponse:
        # TODO: How to deal with self.last_state when env is done?
        self.log_reward.append(reward)
        # self.avrg_reward.append(np.mean(self.log_reward[-300:]))
        # self.avrg_critic_error.append(np.mean(self.critic_error[-300:]))
        # self.avrg_actor_error.append(np.mean(self.actor_error[-300:]))

        if not self.init_muscle:
            self.init_muscle = True
            response = MuscleUpdateResponse(True, self._get_init_dict())
        else:
            if done:
                response = MuscleUpdateResponse(False, None)
            else:
                if (
                    readings is None
                    or actions is None
                    or reward is None
                    or not next_state
                    or done is None
                ):
                    LOG.error(
                        "Brain(id=0x%x) " "has received a none value",
                        id(self),
                    )
                    raise NoneInputError
                else:
                    self._remember(readings, actions, reward, next_state, done)
                    # Currently training and updating every step!
                    response = self._train()

        return response

    def _remember(self, state, action, reward, next_state, done):
        self.buffer.add(
            state=np.array(state),
            action=np.array(action),
            reward=reward,
            next_state=np.array([s() for s in next_state]),
            done=done,
        )

    def load_model(self, path, **kwargs):
        self.critic = T.load(f"{self.load_path}/td3_critic")
        self.actor = T.load(f"{self.load_path}/td3_actor")
        self.critic_target = T.load(f"{self.load_path}/td3_critic_target")
        self.actor_target = T.load(f"{self.load_path}/td3_actor_target")

    def store_model(self, path, **kwargs):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            LOG.warning(
                "Brain(id=0x%x) failed to create path to save model %s",
                id(self),
                str(e),
            )
            return

        T.save(self.critic, f"{self.server_store_path}/td3_critic")
        T.save(self.actor, f"{self.server_store_path}/td3_actor")
        T.save(
            self.critic_target, f"{self.server_store_path}/td3_critic_target"
        )
        T.save(self.actor_target, f"{self.server_store_path}/td3_actor_target")
