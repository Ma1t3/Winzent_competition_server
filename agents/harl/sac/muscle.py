import numpy as np
import torch as T
from harl.sac.muscle import SACMuscle
from palaestrai.types import Box
from palaestrai.types.mode import Mode


def output_scaling(actuators_available, actions):
    """Method to scale the output to the given actuator space.

    If the network output space changes, this method needs to be
    modified as well.
    """

    input_range = [-1, 1]

    for idx, action in enumerate(actions):
        assert isinstance(
            actuators_available[idx].action_space, Box
        ), f'{actuators_available[idx].action_space} must be "Box" type'
        value = np.interp(
            action,
            input_range,
            [
                actuators_available[idx].action_space.low[0],
                actuators_available[idx].action_space.high[0],
            ],
        )
        actuators_available[idx](value)
    return actuators_available


class PGASCSACMuscle(SACMuscle):
    """Muscle for the SAC algorithm that can be used on the Competition Server (extending hARL-Agent).
    The Muscle is compatible with "server_store_path" of the Brain and has the parameter "load_path"."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path, **params):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.load_path = params.get("load_path")

    def propose_actions(
        self, sensors, actuators_available, is_terminal=False
    ) -> tuple:
        values = [val() for val in sensors]
        obs = T.tensor(
            values,
            dtype=T.float,
        )
        state = obs.to(T.device("cpu"))
        if self._mode == Mode.TRAIN:
            actions = self.model.act(state, False)
        else:
            # In test mode we use det
            actions = self.model.act(state, True)

        assert len(actions) == len(actuators_available)

        env_actuators = output_scaling(actuators_available, actions)

        return env_actuators, actions, values, {}

    def prepare_model(self):
        data = open(self.load_path + "/sac_actor", "rb")
        self.model = T.load(data).to("cpu")
