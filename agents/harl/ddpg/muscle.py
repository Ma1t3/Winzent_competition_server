import random

import numpy as np
import torch
from harl.ddpg.muscle import DDPGMuscle
from harl.ddpg.noise import OUActionNoise
from palaestrai.types.box import Box


class PGASCDDPGMuscle(DDPGMuscle):
    """Muscle for the DDPG algorithm that can be used on the Competition Server (extending hARL-Agent).
    The Muscle is compatible with "server_store_path" of the Brain, has the parameter "load_path" and loads the model
    to the specific device. This allows to train the model on a GPU and use it in experiments on a CPU.
    Additionally, this class extends the hARL-DDPG muscle to the probability_factor parameter "prob" (in %) that can be used
     to activate a "coin flip" for every action in each step. So each action has a probability of "prob" (in %) to be applied.
     If the action is not applied, another agent is able to apply an action for the same actuator."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path, **params):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.load_path = params.get("load_path")
        self.probability_factor = params.get("prob")

    def setup(self):
        pass

    @staticmethod
    def output_scaling(actuators_available, actions, probability_factor):
        """Method to scale the output to the given actuator space.

        If the network output space changes, this method needs to be
        modified as well.
        """
        assert len(actions) == len(actuators_available)
        input_range = [0, 1]

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

            # "coin flip" to decide whether to apply the decided action or not
            if probability_factor:
                if random.randrange(100) < probability_factor:
                    actuators_available[idx](value)
                else:
                    setattr(actuators_available[idx], "_setpoint", None)
            else:
                actuators_available[idx](value)

        return actuators_available, actions

    def propose_actions(
        self, sensors, actuators_available, is_terminal=False, noise=True
    ):
        values = [val() for val in sensors]
        obs = torch.tensor(
            values,
            dtype=torch.float,
        )

        state = obs.to(self.model.device)
        mu_prime = self.model.forward(state).to(self.model.device)
        if noise is True:
            if self.noise is not None:
                self.noise.reset()  # TODO: Reset after every episode!
            else:
                self.noise = OUActionNoise(
                    mu=np.zeros(len(actuators_available))
                )
            mu_prime += torch.tensor(self.noise(), dtype=torch.float).to(
                self.model.device
            )

        actions = self._clip_actions(mu_prime, actuators_available)[0]

        assert len(actions) == len(actuators_available)

        env_actuators, actions = self.output_scaling(
            actuators_available, actions, self.probability_factor
        )

        return [env_actuators, actions, values, {}]

    def prepare_model(self):
        """Prepare the model for training."""
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        data = open(self.load_path + "/ddpg_actor", "rb")
        # load with map location
        self.model = torch.load(data, map_location=device)
        self.model.eval()
        # reassign correct device (important if cuda trained agent should be used on cpu)
        self.model.device = device
        self.model.to(self.model.device)
