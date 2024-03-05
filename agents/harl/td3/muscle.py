import numpy as np
import torch
from harl.TD3.muscle import TD3Muscle
from palaestrai.types import Box


class PGASCTD3Muscle(TD3Muscle):
    """Muscle for the TD3 algorithm that can be used on the Competition Server (extending hARL-Agent).
    The Muscle is compatible with "server_store_path" of the Brain and has the parameter "load_path"."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path, **params):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.load_path = params.get("load_path")

    def output_scaling(self, actuators_available, actions):
        """Method to scale the output to the given actuator space.

        If the network output space changes, this method needs to be
        modified as well.
        """
        assert len(actions) == len(actuators_available)

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

    def propose_actions(
        self, sensors, actuators_available, is_terminal=False
    ) -> list:
        values = [val() for val in sensors]
        obs = torch.tensor(
            values,
            dtype=torch.float,
        )
        state = obs.to(torch.device("cpu"))
        actions = self.model(state).cpu().data.numpy().flatten()

        assert len(actions) == len(actuators_available)

        env_actuators = self.output_scaling(actuators_available, actions)

        return [env_actuators, actions, values, {}]

    def prepare_model(self):
        data = open(self.load_path + "/td3_actor", "rb")
        self.model = torch.load(data).to("cpu")
