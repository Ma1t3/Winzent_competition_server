"""lists of all brain/muscle/objective-paths that can be used by the user directly in agent yamls"""
brains = [
    "palaestrai.agent.dummy_brain:DummyBrain",
    "pgasc.agents.harl.ddpg.brain:PGASCDDPGBrain",
    "pgasc.agents.harl.ppo.brain:PGASCPPOBrain",
    "pgasc.agents.harl.sac.brain:PGASCSACBrain",
    "pgasc.agents.harl.td3.brain:PGASCTD3Brain",
]

muscles = [
    "palaestrai.agent.dummy_muscle:DummyMuscle",
    "pgasc.agents.palaestrai_test_agents.muscles:SetNothingMuscle",
    "pgasc.agents.palaestrai_test_agents.muscles:SetpointMuscle",
    "pgasc.agents.palaestrai_test_agents.muscles:SaveValuesMuscle",
    "pgasc.agents.winzent_agent_system.muscle:WinzentMuscle",
    "pgasc.agents.harl.ddpg.muscle:PGASCDDPGMuscle",
    "pgasc.agents.harl.ppo.muscle:PGASCPPOMuscle",
    "pgasc.agents.harl.sac.muscle:PGASCSACMuscle",
    "pgasc.agents.harl.td3.muscle:PGASCTD3Muscle",
]

objectives = [
    "palaestrai.agent.dummy_objective:DummyObjective",
    "pgasc.agents.harl.base.objective:DummyObjective",
    "pgasc.agents.harl.base.objective:AttackerObjective",
    "pgasc.agents.harl.base.objective:DefenderObjective",
    "pgasc.agents.harl.base.objective:DefenderDeltaObjective",
]
