import numpy as np
import torch
from harl.ppo.muscle import PPOMuscle
from palaestrai.types import Box


def output_scaling(actuators_available, actions):
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


class PGASCPPOMuscle(PPOMuscle):
    """Muscle for the PPO algorithm that can be used on the Competition Server (extending hARL-Agent).
    The Muscle is compatible with "server_store_path" of the Brain and has the parameter "load_path"."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path, **params):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.load_path = params.get("load_path")

    @torch.no_grad()
    def propose_actions(self, sensors, actuators_available, is_terminal=False):
        """
        Queries an action from the actor network, should be called from rollout.

        Parameters:
            obs - the observation at the current timestep

        Return:
            action - the action to take, as a numpy array
            log_prob - the log probability of the selected action in the distribution
        """

        if self.cov_mat is None:
            cov_var = torch.full(
                size=(len(actuators_available),), fill_value=0.5
            )
            self.cov_mat = torch.diag(cov_var)

        input_values = [val() for val in sensors]
        obs = torch.tensor(
            input_values,
            dtype=torch.float,
        ).to(self.actor.device)
        # Query the actor network for a mean action
        dist = self.actor(obs)
        value = self.critic(obs)
        action = dist.sample()

        probs = dist.log_prob(action).cpu().data.numpy().flatten()
        action = action.cpu().data.numpy().flatten()
        value = value.cpu().data.numpy().flatten()

        assert len(action) == len(actuators_available)

        env_actions = output_scaling(actuators_available, action)

        additional_data = {"probs": probs, "vals": value}
        return env_actions, action, input_values, additional_data

    def prepare_model(self):
        data = open(self.load_path + "/ppo_actor", "rb")
        self.actor = torch.load(data)
        data = open(self.load_path + "/ppo_critic", "rb")
        self.critic = torch.load(data)
