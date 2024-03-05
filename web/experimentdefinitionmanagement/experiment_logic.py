import logging
import os

import yaml
from django.conf import settings

from pgasc.web.experimentdefinitionmanagement.models import ExperimentRun

logger = logging.getLogger(__name__)


def create_experiment_run_files(experiment: ExperimentRun, erd: str):
    """
    Save the experiment run files for the given experiment.
    - Copy the user uploaded erd and replace the uid.
    - Copy the midas yml file, replace the uid, experiment parameters and add scenarios.
    """
    experiment_id = experiment.pk

    # filepath to static midas yml
    filepath_default_midas_yml = os.path.join(
        settings.BASE_DIR, "yaml_defaults", "bhv_midas.yml"
    )

    # prospective filepaths for the ymls
    filepath_experiment_yml = os.path.join(
        settings.DIR_EXPERIMENTS, f"{experiment_id}.yml"
    )

    filepath_user_yml = os.path.join(
        settings.DIR_EXPERIMENTS, f"{experiment_id}_user.yml"
    )
    filepath_midas_yml = os.path.join(
        settings.DIR_EXPERIMENTS, f"{experiment_id}_midas.yml"
    )

    # make experiment yml dir if not exists
    if not os.path.isdir(settings.DIR_EXPERIMENTS):
        os.makedirs(settings.DIR_EXPERIMENTS, exist_ok=True)

    # store user erd in file
    with open(filepath_user_yml, "w") as erd_user_file:
        erd_user_file.write(erd)

    # replace experiment id in erd and save file
    experiment_data = yaml.safe_load(erd)
    experiment_data["uid"] = str(experiment_id)
    with open(filepath_experiment_yml, "w") as experiment_yml:
        yaml.dump(experiment_data, experiment_yml, sort_keys=False)

    # load midas yml
    with open(filepath_default_midas_yml, "r") as default_midas_yml:
        midas_data = yaml.safe_load(default_midas_yml)
    # get params from erd
    phase = experiment_data["schedule"][0]
    experiment_params_path = list(phase.values())[0]["environments"][0][
        "environment"
    ]["params"]

    if "write_in_midas_db" in experiment_params_path.keys():
        midas_data["bhv_palaestrai"]["mosaikdb_params"].update(
            {"write_in_database": experiment_params_path["write_in_midas_db"]}
        )

    if "scenario" in experiment_params_path.keys():
        midas_data["bhv_palaestrai"]["powergrid_params"].update(
            {"scenario": _get_scenario(experiment_params_path["scenario"])}
        )

    # replace experiment id, step_size, end, start_date
    midas_data["bhv_palaestrai"]["mosaikdb_params"].update(
        {"uid": str(experiment_id)}
    )
    midas_data["bhv_palaestrai"].update(
        {"step_size": experiment_params_path["step_size"]}
    )
    midas_data["bhv_palaestrai"].update({"end": experiment_params_path["end"]})
    midas_data["bhv_palaestrai"].update(
        {"start_date": experiment_params_path["params"]["start_date"]}
    )

    # save file to experiment yml directory
    with open(filepath_midas_yml, "w") as midas_yaml:
        yaml.dump(midas_data, midas_yaml, sort_keys=False)


META_SCENARIO = {
    "ext_grid_fallout": "ext_grid_fallout.yml",
    "gen_fallout": "gen_fallout.yml",
    "gen_fallout_light": "gen_fallout_light.yml",
    "loads_rising": "loads_rising.yml",
    "sgens_rising": "sgens_rising.yml",
    "loads_rising_now": "loads_rising_now.yml",
    "all_loads_to_zero": "all_loads_to_zero.yml",
    "all_wind_to_zero": "wind_percentages/all_wind_to_zero.yml",
    "all_wind_to_10%": "wind_percentages/all_wind_to_10%.yml",
    "all_wind_to_20%": "wind_percentages/all_wind_to_20%.yml",
    "all_wind_to_30%": "wind_percentages/all_wind_to_30%.yml",
    "all_wind_to_40%": "wind_percentages/all_wind_to_40%.yml",
    "all_wind_to_50%": "wind_percentages/all_wind_to_50%.yml",
    "all_wind_to_60%": "wind_percentages/all_wind_to_60%.yml",
    "all_wind_to_70%": "wind_percentages/all_wind_to_70%.yml",
    "all_wind_to_80%": "wind_percentages/all_wind_to_80%.yml",
    "all_wind_to_90%": "wind_percentages/all_wind_to_90%.yml",
    "all_wind_to_110%": "wind_percentages/all_wind_to_110%.yml",
    "all_wind_to_120%": "wind_percentages/all_wind_to_120%.yml",
    "all_wind_to_130%": "wind_percentages/all_wind_to_130%.yml",
    "all_wind_to_140%": "wind_percentages/all_wind_to_140%.yml",
    "all_wind_to_150%": "wind_percentages/all_wind_to_150%.yml",
    "all_wind_to_160%": "wind_percentages/all_wind_to_160%.yml",
    "all_wind_to_170%": "wind_percentages/all_wind_to_170%.yml",
    "all_wind_to_180%": "wind_percentages/all_wind_to_180%.yml",
    "all_wind_to_190%": "wind_percentages/all_wind_to_190%.yml",
    "all_wind_to_200%": "wind_percentages/all_wind_to_200%.yml",
    "wind_crashes_at_12AM": "wind_fallouts/wind_crashes_at_12AM.yml",
    "all_households_to_zero": "household_percentages/all_households_to_zero.yml",
    "all_households_to_10%": "household_percentages/all_households_to_10%.yml",
    "all_households_to_20%": "household_percentages/all_households_to_20%.yml",
    "all_households_to_30%": "household_percentages/all_households_to_30%.yml",
    "all_households_to_40%": "household_percentages/all_households_to_40%.yml",
    "all_households_to_50%": "household_percentages/all_households_to_50%.yml",
    "all_households_to_60%": "household_percentages/all_households_to_60%.yml",
    "all_households_to_70%": "household_percentages/all_households_to_70%.yml",
    "all_households_to_80%": "household_percentages/all_households_to_80%.yml",
    "all_households_to_90%": "household_percentages/all_households_to_90%.yml",
    "all_solar_to_zero": "solar_percentages/all_solar_to_zero.yml",
    "all_solar_to_25%": "solar_percentages/all_solar_to_25%.yml",
    "all_solar_to_50%": "solar_percentages/all_solar_to_50%.yml",
    "all_solar_to_75%": "solar_percentages/all_solar_to_75%.yml",
    "all_solar_to_125%": "solar_percentages/all_solar_to_125%.yml",
    "all_solar_to_150%": "solar_percentages/all_solar_to_150%.yml",
    "all_solar_to_175%": "solar_percentages/all_solar_to_175%.yml",
    "all_solar_to_200%": "solar_percentages/all_solar_to_200%.yml",
    "all_solar_on_21_july_to_200%": "solar_percentages/all_solar_on_21_july_to_200%.yml",
    "all_solar_to_300%": "solar_percentages/all_solar_to_300%.yml",
    "all_solar_to_400%": "solar_percentages/all_solar_to_400%.yml",
    "all_solar_to_500%": "solar_percentages/all_solar_to_500%.yml",
    "all_conventionals_to_50%": "conventional_percentages/all_conventionals_to_50%.yml",
    "rest_low_solar_to_zero": "solar_high_rest_low_percentages/rest_low_solar_to_zero.yml",
    "rest_low_solar_to_25%": "solar_high_rest_low_percentages/rest_low_solar_to_25%.yml",
    "rest_low_solar_to_50%": "solar_high_rest_low_percentages/rest_low_solar_to_50%.yml",
    "rest_low_solar_to_75%": "solar_high_rest_low_percentages/rest_low_solar_to_75%.yml",
    "rest_low_solar_to_125%": "solar_high_rest_low_percentages/rest_low_solar_to_125%.yml",
    "rest_low_solar_to_150%": "solar_high_rest_low_percentages/rest_low_solar_to_150%.yml",
    "rest_low_solar_to_175%": "solar_high_rest_low_percentages/rest_low_solar_to_175%.yml",
    "rest_low_solar_to_200%": "solar_high_rest_low_percentages/rest_low_solar_to_200%.yml",
    "rest_low_solar_to_225%": "solar_high_rest_low_percentages/rest_low_solar_to_225%.yml",
    "rest_low_solar_to_250%": "solar_high_rest_low_percentages/rest_low_solar_to_250%.yml",
    "rest_low_solar_to_275%": "solar_high_rest_low_percentages/rest_low_solar_to_275%.yml",
    "rest_low_solar_to_300%": "solar_high_rest_low_percentages/rest_low_solar_to_300%.yml",
    "rest_low_solar_to_400%": "solar_high_rest_low_percentages/rest_low_solar_to_400%.yml",
}


def _get_scenario(scenario):
    if type(scenario) is list:
        return scenario

    if scenario in META_SCENARIO.keys():
        # load scenario yml
        scenario_yml_path = os.path.join(
            settings.BASE_DIR, "yaml_midas_scenarios/winzent_scenarios", META_SCENARIO[scenario]
        )
        with open(scenario_yml_path, "r") as scenario_yml:
            midas_data = yaml.safe_load(scenario_yml)
            return midas_data
    else:
        logger.info(f"Scenario with key {scenario} does not exist")

    return []
