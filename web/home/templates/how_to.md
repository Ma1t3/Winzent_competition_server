# How to use the competition server

This page contains all information on how to upload agents or configure experiments and competitions. This is explicitly not a tutorial 
on how to design or implement agent systems, but rather a guide on how to use the competition server. Some functions
of the competition server can be used without registration, such as displaying public experiments or competitions. 
However, to upload your own agent systems or to create experiments or competitions, you need to create an account. 

## Concept of agents, experiments and competitions

Before you can start using the competition server, you need to understand the concept of agents, experiments and competitions.
In our context, an agent (system) is, in simple terms, a program that uses the inputs of the power system simulation to 
make decisions about the control of the power grid's actuators
There are several possible ways to implement an agent, two examples are Training using
[Adversarial Resilience Learning](https://www.offis.de/en/research/applied-artificial-intelligence/adversarial-resilience-learning-e.html)
or [Winzent](https://tu-freiberg.de/sites/default/files/media/institut-fuer-informatik-9034/professur-st/publikation/ijait_2014_v7_n12_ldsa_ad_scsg.pdf).
There are some default agent systems available in the competition server, among them several Reinforcement Learning algorithms
for an implementation of Adversarial Resilience Learning and a Winzent agent. You can also implement your own agent system
and upload it to the competition server.

The competition server distinguishes between experiments and competitions. An experiment is a one-time
execution of a simulation of the power grid in which the actions of the agent systems are applied. Meanwhile, agent
systems can be trained using reinforcement learning in the ARL context. The competition server can then automatically
save the trained agent as a new agent system. Nevertheless, the competition server can also handle agent systems that are not
based on machine learning, such as Winzent.
An experiment can be configured using an Experiment Run Document (ERD).
On the competition server, an experiment is always a counterplay of an attacking (attacker) agent system with the goal 
of destabilizing the power grid and a defending (defender) agent system with the goal of stabilizing the power grid.

To compare agent systems with each other, you can use competitions. The basic idea of a competition is to select *n*
attackers and *m* defenders to compete against each other. When creating the competition, *m &middot; n* experiments are created, 
in each experiment an attacker competes against a defender. So, each attacker is paired once with each defender and
vice versa. The configuration is the same for all experiments. 

Now, if you want to compare RL different agents, you can first upload the untrained agents to the competition
server – or use the built-in hARL agents (e.g. *DDPG-Agent (untrained)*). Then the agents can be trained using experiments, 
and the agents trained as defenders and attackers can be automatically saved as new agents by the competition server. 
Finally, you can use the trained agents (also together with baselines and other agents developed by other users)
in a competition to compare them. Research results can be derived from the results and leaderboard on the competition
details page and from the details of each experiment in the competition.

## Uploading an agent
You can use the built-in agents or upload your own agent. To upload your own agent, you need to create an account on the
competition server. Then you can upload your agent as a zip file. The zip file must contain all files necessary to run
your agent. The agent implementation has to be written in Python and must be compatible with the Brain/Muscle API of the 
palaestrAI framework. Please read the [palaestrAI documentation (Brain/Muscle API)](http://docs.palaestr.ai/brain-muscle-api.html) carefully. 
Your zip file may also contain a `requirements.txt` file in the root directory, which will be installed automatically 
before the agent is started. This is useful if your agent requires additional Python packages. Some packages like 
*NumPy* or *PyTorch* are already installed on the competition server, so you don't need to include them in your 
`requirements.txt` file.

You must name your agent, specify a role (attacker, defender, or both if your algorithm can be used as both), 
and you may provide a description (optional). If you set your agent as public, every user of the competition server can
use it in an experiment or competition or download the files of the agent. If you set your agent as private, only you can use it.
If you want to use your agent in a competition, the `Agent YAML for Competitions` must be set. For now,
you can leave the `Agent YAML for Competitions` field with the default value. If you want to train your agent in an
experiment, the agent YAML will be automatically extracted from the Experiment Run Document. As long as the agent YAML
is not set correctly, the agent cannot be used in a competition. You can change the agent YAML on the agent details page.
On that page, you can see all relevant details of your agent, such as role, description and a list of files.

## Running an experiment

If you are logged in, you can create a new experiment on the `Experiments` page. You have to specify a name for your
experiment, and you have to select a defender and an attacker. If you want to train your agent in the experiment, you
should tick the `Store copy of trained ...` checkbox. This will save the agent as a new agent system on the competition 
server after the experiment is finished. You can then use the trained agent in a competition. 
You need to specify the *Experiment Run Document (ERD)* for the experiment. The ERD is a YAML file that contains all
configuration options for the experiment. You can use the online code editor, or drag and drop an existing YAML file.
The syntax and all options of the ERD are described below. Syntax is checked automatically, when you save the experiment.
You can also use the default ERD or one of the example ERDs below as a starting point. The default ERD has also a lot of
comments that explain the options. It is also possible to duplicate an existing experiment. 
This will open a new experiment creation page with the same settings as the original experiment.

After creating the experiment, you can start it by clicking on the `Start` button. The experiment will be executed when
there is capacity on the competition server. You can see the status of the experiment on the `Experiments` page. If 
`Autoreload` is enabled, the page will automatically update the experiment list. Currently running experiments are 
always at the top of the list. You can see the details of the 
experiment on the experiment details page. You can view and download the ERD and also the results of the experiment,
once the experiment is finished. While the experiment is running, the progress of the experiment can be viewed in 
real-time in the Grafana board, a live log is available on the `Logfile` tab. You can also abort experiments if you 
want to stop them or if you see errors in the log. The results or `Datapoints` consist of evaluation criteria calculated 
by the MIDAS framework and evaluation functions composed of them.
These have the goal of describing the health of the power grid over the entire experiment using a scalar. You can define
your own evaluation functions and upload them together with an agent to use them in an experiment. 
However, the default evaluation function we developed can also be used (recommended). The function is described in the 
popup window on the experiment details page.

## Running a competition
You can create a competition on the `Competitions` page. You have to specify a name for your competition, and you have to
choose all attackers and defenders that should compete against each other. The configuration of the competition has to 
be specified in the *Competition Run Document (CRD)*, which follows the same syntax and has the same structure as an ERD
– only without the agents section. The ERD for each experiment is then dynamically generated by the competition server.
The agent YAML has to be set for all agents, you want to use in the competition. If your agent is not in the list, 
check the agent details page if the agent YAML is set correctly. After creating the competition, all experiments are
automatically created. 

Thus, starting a competition ensures the execution of all generated experiments. After all experiments have been
completed, the results of the competition can be calculated.
For the evaluation of a competition, the calculated values of the evaluation criteria and functions can be displayed on
the web interface. For each criterion/function, the following values are calculated for each agent: the minimum value,
the maximum value and an average over all experiments in which this agent participated.
So the implemented evaluation function can be used to compare the defenders directly: The competition server
additionally displays a leaderboard on which the average of the rating function is used to rank the defenders. The more
points the rating function calculates or the higher the stability of the power grid was during the experiments a defender
participated in, the better his place on the leaderboard. For attacker, there is also a leaderboard with the reverse
sorting: Since the attacker's goal is to destabilize the power grid, a lower score means a better performance of the attacker.
You can also see the results and graphs of each individual experiment.

## Experiment Run Documents in Detail

The Experiment Run Document (ERD) is defined in YAML format. The semantics of the ERD are described in the 
[palaestrAI Quickstart Guide](http://docs.palaestr.ai/quickstart.html#palaestrai-experiment) in a general way. 
The most important parts of the ERD to use the competition server are the `environment` and `agents` sections.
In the following, you can find code examples and the most important points to pay attention to when creating an ERD.
At first, the `uid` of the ERD is replaced internally and can be set arbitrarily.

### Environment

The default ERD uses a model of the Bremerhaven (BHV) grid as environment. The following Figure shows a graphical 
representation of the Bremerhaven grid. Buses are shown in blue, external grids in yellow. Generators (circles), 
loads (triangles) and transformers (double-circles) are also shown:
  <img src="/static/images/bhv_grid.png" alt="BHV Grid" width="600"/>

To use the bhv grid, the environment needs to be configured in ERD as follows. You can change the explained parameters,
but you should not change the other parameters except you know what you are doing.

Example for the `environments` section of the ERD:
```yaml
environments:
  - environment:
      name: palaestrai_mosaik:MosaikEnvironment
      uid: env
      params:
        module: midas.adapter.palaestrai:Descriptor
        description_func: describe
        instance_func: get_world
        # HERE you can change the step size of the simulation (in seconds, 900 = 15 minutes):
        step_size: &step_size 900
        # HERE you can change the duration of the simulation (in seconds, 24*60*60 = 24 hours):
        end: &end 24*60*60
        # HERE you can change the rating function used for the leaderboard:
        rating_function: pgasc.midas.analyze.rating_functions.default_rating_function.DefaultRatingFunction
        # HERE you can change if the grid parameters (like vm/pu) are stored in the database (True) or not (False)
        # If True, the simulation is much slower, but you can see the parameters in the grafana dashboard, interesting for testing
        # If False, the simulation is much faster, but you can't see the parameters in the grafana dashboard, interesting for training with many episodes
        write_in_midas_db: True
        # HERE you can add scenarios to the experiment or competition or use predefined scenarios
        scenario: [ ]
        # HERE you can configure and change the (global, environment) reward function used for the training and display in the grafana dashboard
        reward:
          name: pgasc.midas.rewards.reward_pgasc_v5_1:GridHealthReward
          params:
            # HERE you can change the reward function parameters (in this case: the weights of the sub-rewards)
            weight_vm_pu: 1
            weight_all_in_service: 1
            weight_line_loading: 1
            weight_trafo_loading: 1
            weight_external_grid_usage: 1
            norm_weights: False
        params:
          name: bhv_palaestrai
          config: bhv_midas.yml # please don't change this, as the bhv_midas.yml will dynamically be generated
          end: *end
          step_size: *step_size
          # HERE you can change the start date of the simulation (in ISO format)
          start_date: 2017-01-01 00:00:00+0100
          with_db: True
          mosaik_params: { addr: [ 127.0.0.1, 5674 ] }
```

#### Scenarios

You can use scenarios in experiments and competitions. A scenario is a list of actions that are executed in the 
environment at a specific time. There are a few predefined scenarios which can be used directly with the `scenario` 
section in the ERD, e.g. `scenario: ext_grid_fallout`.

Here's a list of all predefined scenarios:
- `ext_grid_fallout`: Some external grids are broken.
- `gen_fallout`: All generators are broken.
- `gen_fallout_light`: Some generators are broken.
- `loads_rising`: All loads needs more power.
- `sgens_rising`: All generators needs more power.

You can also define your own scenarios for your experiments and competitions. To do so, you need to specify a list in 
the `scenario` section. Each item of the list consists of a tuple 
`[start, end, dictionary of parameters]`. 
Start and end time are specified in seconds. The scenario will be active from `start` to `end`. After the end, the actuator will 
be set to the last value it had before the scenario started. The dictionary of parameters is a dictionary with any 
MIDAS actuators as keys and the action as value. All MIDAS actuators and their range of values are listed in the file 
[scenario_parameters.txt](/static/howto_files/scenario_parameters.txt). A value set by a scenario always overrides 
possible agent actions and MIDAS default profiles.

Example for the scenario section with two different scenarios:
```yaml
scenario:
  # set all actuators not in service at 11:00, back at 16:00
  - [ 12*60*60, 16*60*60-1, {
    0-sgen-0-16.in_service: False,
    0-sgen-1-17.in_service: False,
    0-sgen-2-20.in_service: False,
    0-sgen-3-22.in_service: False,
    0-sgen-4-23.in_service: False,
    0-sgen-5-25.in_service: False,
    0-sgen-6-28.in_service: False,
    0-sgen-7-30.in_service: False,
    0-sgen-8-32.in_service: False,
    0-sgen-9-33.in_service: False,
    0-sgen-10-35.in_service: False,
    0-sgen-11-37.in_service: False,
    0-sgen-12-39.in_service: False,
    0-sgen-13-40.in_service: False,
    0-sgen-14-43.in_service: False,
    0-sgen-15-45.in_service: False,
    0-sgen-16-50.in_service: False,
    0-sgen-17-53.in_service: False,
    0-sgen-18-55.in_service: False,
    0-sgen-19-57.in_service: False,
    0-sgen-20-63.in_service: False,
    0-sgen-21-65.in_service: False,
    0-sgen-22-67.in_service: False,
    0-sgen-23-71.in_service: False,
    0-sgen-24-80.in_service: False,
  } ]
  # set all (except one) external grids not in service at 3:00, back at 6:00
  - [ 3*60*60, 6*60*60-1, {
    0-ext_grid-14.in_service: False,
    0-ext_grid-8.in_service: False,
    0-ext_grid-1.in_service: False,
    0-ext_grid-13.in_service: True,
  } ]
```

#### Reward Function

To train an agent using Reinforcement Learning, you need to define a reward function. You can define your own reward
and upload it together with your agent, or you can use one of the predefined reward functions. There are 5 versions of 
the reward function `pgasc.midas.rewards.reward_pgasc_v*:GridHealthReward` with `*` in (`v1_1`, `v2`, `v3`, `v4`, `v5_1`).
The reward functions are described in our documentation.

#### Agents

In the `agents` section of an ERD, you can define the agents that are used in the experiment. In Competitions, the 
agent YAMLs are used. The agent YAML follows the same syntax, but without the `name` tag.
The Agent YML is used in competitions only, so that you have full flexibility over the agent configuration in experiments.
For example, you can train agents with different parameters or different sensors and actuators in experiments.
Make always sure that the agent definition in the ERD matches the agents selected in the dropdown menu.
For competitions, make sure all paths in the Agent YAML are correct. If not, you can change them on the agent details page.

##### Uploaded Agents

To use an uploaded agent, first choose the agent in the dropdown menu. Then, add the correct path in the `name` field of 
the agents section, 
e.g. `name: defender.dummy_brain:DummyBrain` for the defender if there is an `dummy_brain.py` with the class `DummyBrain` 
in the root directory of the selected defender agent. For the attacker, the path would be in this example 
`name: attacker.dummy_brain:DummyBrain`. 
For the agent YAML in competitions, use the file structure of your uploaded agent directly without `defender.` 
or `attacker.` prefix. You can see the file structure of the uploaded agents in the `Files` tab on the agent details page. 
You can also specify parameters of your agent implementation in `params` section for brain, muscle and objective.
To learn more about the difference between the reward and an agent's objective, have a closer look at the
[palaestrAI documentation (Reward and objective)](http://docs.palaestr.ai/reward.html).

Example for an uploaded defender agent (without sensors or actuators):
```yaml
- name: mighty_defender
  brain:
    # HERE you can change the brain path and params of your uploaded agent
    name: dummy_brain:DummyBrain
    params: { "key": "value" }
  muscle:
    # HERE you can change the muscle path and params of your uploaded agent
    name: dummy_muscle:DummyMuscle
    params: { }
  objective:
    # HERE you can change the objective and params path of your uploaded agent
    name: dummy_objective:DummyObjective
    params: { }
  sensors: [ ]
  actuators: [ ]
```

##### Predefined Agents

You can also use predefined agents. Use the dropdown menu to select the agent. Then, you can use the path of the agent 
in the `name` field of the agents section directly, 
e.g. `name: palaestrai.agent.dummy_brain:DummyBrain`.

The full list of directly usable paths (without need to upload an agent):
```python
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
```

##### Sensors and Actuators

There are many sensors and actuators the agents can use. Sensors e.g. to get information about the topology (`grid_json`;
used by Winzent) or about the components of the power grid (e.g. to get `p_mw` and `q_mvar` of loads and generators).
Actuators e.g. to set the `p_mw` and `q_mvar` of loads and sgens. All power grid components and their attributes are described in the 
[pandapower documentation](https://pandapower.readthedocs.io/en/v2.9.0/elements.html). A full list of all sensors and 
actuators in the bhv grid is provided in the file [all_sensors_and_actuators.yml](/static/howto_files/all_sensors_and_actuators.yml).

Example with 2 sensors and 2 actuators (p_mw of 2 specific load as sensors, scaling of 2 specific generators as actuators):
```yaml
sensors:
  - env.Powergrid-0.0-load-0-15.p_mw
  - env.Powergrid-0.0-load-1-17.p_mw
actuators:
  - env.Powergrid-0.0-sgen-0-16.scaling
  - env.Powergrid-0.0-sgen-1-17.scaling
```

You shouldn't give the exact same actuator to multiple agents (in this case, it is non-deterministic, which agent controls the actuator).
However, it is possible to use the actuators with suffix `_prio-*` (where `*` is an integer), 
e.g. `env.Powergrid-0.0-sgen-0-16.scaling_prio-1`. The agent with the highest priority (smallest `*`-value) will control 
the actuator if it sets a value. If the agent with the highest priority does not set a value (`None`), the agent with 
the next highest priority will control the actuator, ... This is useful in combination with the `probability_factor` of 
the PGASC-DDPG-Muscle. With this implementation, multiple agents can have the same actuators with different priorities. 
Pay attention to priorities in competitions, where all attackers are paired with all defenders.

##### Save and load agents

To first train an agent and test it, use two different experiments with the same agent configuration (including
sensors and actuators) in the ERD. In the first experiment (training), choose `train`-mode in the ERD.
Click on `Store copy of trained attacker/defender` to save the trained agent and use the trained agent in a second experiment.
You can duplicate the experiment and change the mode to `test`. To save the agent YAML automatically make sure the 
attacker is named `evil_attacker` and the defender is named `mighty_defender` in the training experiment. Saving and 
loading agents is only possible if the agent stores its data in the `./defender` directory (for a defender) or the `./attacker` 
(for an attacker) directory. Otherwise, the trained agent will not be saved. The usage of PGASC-hARL-Agents is 
recommended as they can store their data suitable for saving and loading on the competition server.

##### PGASC-hARL-Agents

The PGASC-hARL-Agents extend the hARL agents of the [hARL repository](https://gitlab.com/arl2/harl) in the version of the dc73d804 commit (of June 15, 2022).
An example brain path of a DDPG agent is `pgasc.agents.harl.ddpg.brain:PGASCDDPGBrain`.
As parameters, you always need to set the `server_store_path` and the `load_path` parameters in the `params` section 
of the brain and the `load_path` parameter in the `params` section of the muscle. Also, use always `./defender` as store 
and load path for the defender and `./attacker` as store and load path for the attacker. The `load_path` parameter can 
and should already be set in train_mode. This is useful if you want to use the trained agent directly in the competition
without modifying the agent YAML.

Example for a DDPG defender agent (without sensors or actuators):
```yaml
- name: mighty_defender
  brain:
    name: pgasc.agents.harl.ddpg.brain:PGASCDDPGBrain
    # HERE you can change the parameters of the learning algorithm (except the "server_store_path" and "load_path" parameters)
    params: { "server_store_path": "./defender", "load_path": "./defender", gamma: 0.99, tau: 0.001, batch_size: 8, alpha: 0.00005, beta: 0.001, fc_dims: [ 200,150,100 ], replay_size: 1000000 }
  muscle:
    name: pgasc.agents.harl.ddpg.muscle:PGASCDDPGMuscle
    params: { "load_path": "./defender" }
  objective:
    name: pgasc.agents.harl.base.objective:DefenderObjective
    params: { }
  sensors: []
  actuators: []
```

##### Winzent

The Winzent agent system is updated to the latest version available in [GitLab](https://gitlab.com/mango-agents/mango-library/-/tree/PGASC-Winzent-Changes). 
Winzent does not need brain and objective, but as they are mandatory sections in the ERD, you can use the dummy brain and objective.
Winzent always requires the `grid_json` sensor and uses the `p_mw` sensors of all loads and the `p_mw_flex` sensors 
of all generators. As actuators, it uses the `scaling` values of all generators. 

Example for Winzent (sensors and actuators are shortened):
```yaml
- name: Winzent
  brain:
    name: palaestrai.agent.dummy_brain:DummyBrain
    params: { }
  muscle:
    name: pgasc.agents.winzent_agent_system.muscle:WinzentMuscle
    params:
      step_size: 900 # Needs to be the same as the step size of the environment
      ttl: 80 # Time to live of winzent messages
      time_to_sleep: 10
      factor_mw: 1000000 # factor to mupltiply the p_mw values with
      number_of_restartable_negotiations: 40 # times winzent will try to restart a negotiation if it fails
      send_message_paths: True # if True, Winzent will use the paths of the messages to determine the next hop
  objective:
    name: palaestrai.agent.dummy_objective:DummyObjective
    params: { "params": 1 }
  sensors:
    # grid json (needed for topology)
    - env.Powergrid-0.Grid-0.grid_json
    # loads (indices 0-39): p_mw
    - env.Powergrid-0.0-load-0-15.p_mw
    - env.Powergrid-0.0-load-1-17.p_mw
    # [...]
    - env.Powergrid-0.0-load-39-80.p_mw
    # sgens (indices 0-24): p_mw_flex
    - env.Powergrid-0.0-sgen-0-16.p_mw_flex
    - env.Powergrid-0.0-sgen-1-17.p_mw_flex
    # [...]
    - env.Powergrid-0.0-sgen-24-80.p_mw_flex
  actuators:
    # sgens (indices 0-24): scaling
    - env.Powergrid-0.0-sgen-0-16.scaling
    - env.Powergrid-0.0-sgen-1-17.scaling
    # [...]
    - env.Powergrid-0.0-sgen-24-80.scaling
```


##### Helper Agents

There are some simple helper agents available, that can be used to explore the environment or as a baseline in competitions.  
The palaestrAI-Dummy-Agent samples a random action for each actuator from its action space. Agent-Configuration (without sensors and actuators):
```yaml
brain:
  name: palaestrai.agent.dummy_brain:DummyBrain
  params: {}
muscle:
  name: palaestrai.agent.dummy_muscle:DummyMuscle
  params: {}
objective:
  name: palaestrai.agent.dummy_objective:DummyObjective
  params: {"params": 1}
```

The Set-Nothing-Agent does nothing. Muscle-Configuration (`brain` and `objective` can be Dummy- as above):
```yaml
muscle:
  name: pgasc.agents.palaestrai_test_agents.muscles:SetNothingMuscle
  params: {}
```

The Setpoint-Agent sets all actuators to the given `setpoint`-parameter:
```yaml
muscle:
  name: pgasc.agents.palaestrai_test_agents.muscles:SetpointMuscle
  params: { "setpoint": 0.5 }
```

The Save-Values-Agent saves its inputs in a file (only usable as defender): 
```yaml
muscle:
  name: pgasc.agents.palaestrai_test_agents.muscles:SaveValuesMuscle
  params: {}
```

### Example-ERDs

Finally, there are some example Experiment Run Documents which can be downloaded:
- [erd_uploaded_agent.yml](/static/howto_files/erd_uploaded_agent.yml) ERD to use with a custom uploaded agent
- [erd_winzent_only.yml](/static/howto_files/erd_winzent_only.yml) ERD with a Winzent agent
- [erd_harl_ddpg.yml](/static/howto_files/erd_harl_ddpg.yml) ERD with a PGASC-hARL-DDPG-Agent (without sensors and actuators)
- [erd_harl_ddpg_any_sensor_actuator_once.yml](/static/howto_files/erd_harl_ddpg_any_sensor_actuator_once.yml) ERD with 
  a PGASC-hARL-DDPG-Agent with examples of all sensors and actuators
- [erd_harl_ddpg_different_actuators_training.yml](/static/howto_files/erd_harl_ddpg_different_actuators_training.yml)
  ERD with a PGASC-hARL-DDPG-Agent where attacker and defender use different actuators with mode `training`
- [erd_harl_ddpg_different_actuators_test.yml](/static/howto_files/erd_harl_ddpg_different_actuators_test.yml)
  ERD with a PGASC-hARL-DDPG-Agent where attacker and defender use different actuators with mode `test`
- [erd_harl_ddpg_same_actuators_attacker_priority.yml](/static/howto_files/erd_harl_ddpg_same_actuators_attacker_priority.yml)
  ERD with a PGASC-hARL-DDPG-Agent where attacker and defender use the same actuators and attacker has priority
- [erd_harl_ppo.yml](/static/howto_files/erd_harl_ppo.yml) ERD with a PGASC-hARL-PPO-Agent (without sensors and actuators)
- [erd_harl_sac.yml](/static/howto_files/erd_harl_sac.yml) ERD with a PGASC-hARL-SAC-Agent (without sensors and actuators)
- [erd_harl_td3.yml](/static/howto_files/erd_harl_td3.yml) ERD with a PGASC-hARL-TD3-Agent (without sensors and actuators)
- [erd_save_sensor_values.yml](/static/howto_files/erd_save_sensor_values.yml) ERD with a Save-Values-Agent, which saves its sensor values in a file
- [erd_with_scenario.yml](/static/howto_files/erd_with_scenario.yml) ERD containing an example scenario
