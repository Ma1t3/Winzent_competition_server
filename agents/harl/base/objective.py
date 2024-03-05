from typing import List

from palaestrai.agent import RewardInformation, dummy_objective
from palaestrai.agent.objective import Objective


class DummyObjective(dummy_objective.DummyObjective):
    """Dummy objective function that doesn't need any parameters."""

    def __init__(self, **params):
        # overwriting constructor, so that params can be empty
        super().__init__(params)


class DefenderObjective(Objective):
    """Defender Objective that adds up all environment rewards"""

    def __init__(self, **params):
        # overwriting constructor, so that params can be empty
        super().__init__(params)

    def internal_reward(self, rewards: List["RewardInformation"]) -> float:
        reward = 0
        for rwd in rewards:
            reward += rwd.reward_value
        return reward


class DefenderDeltaObjective(Objective):
    """Defender Objective that uses the difference between the current reward and the last reward as objective."""

    def __init__(self, **params):
        # overwriting constructor, so that params can be empty
        super().__init__(params)
        self.old_reward = 0

    def internal_reward(self, rewards: List["RewardInformation"]) -> float:
        # add up all rewards
        reward = 0
        for rwd in rewards:
            reward += rwd.reward_value

        # compute delta reward
        delta_reward = reward - self.old_reward

        # update old reward
        self.old_reward = reward

        return delta_reward


class AttackerObjective(Objective):
    """Attacker Objective that adds up all negated environment rewards"""

    def __init__(self, **params):
        # overwriting constructor, so that params can be empty
        super().__init__(params)

    def internal_reward(self, rewards: List["RewardInformation"]) -> float:
        reward = 0
        for rwd in rewards:
            reward += -rwd.reward_value
        return reward
