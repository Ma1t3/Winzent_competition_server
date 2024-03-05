import os
import shutil

import pandas as pd
from django.conf import settings
from django.db import connections
from django.http import HttpResponse, FileResponse


def generate_results(experiment_id):
    """Export the results of an experiment from the database to a zip file."""
    path = os.path.join(settings.DIR_EXPERIMENT_EXPORT, str(experiment_id))
    if not os.path.exists(path):
        os.makedirs(path)

    with connections["midas"].cursor():
        # export Midas-DB
        pd.read_sql(
            f'SELECT * FROM "constraint" WHERE experiment_id = {experiment_id}',
            connections["midas"],
        ).to_csv(f"{path}/constrains.csv")
        pd.read_sql(
            f"SELECT * FROM experiment_result WHERE experiment_id = {experiment_id}",
            connections["midas"],
        )
        pd.read_sql(
            f"SELECT * FROM pp_bus WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_bus.csv")
        pd.read_sql(
            f"SELECT * FROM pp_bus_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_bus_meta.csv")
        pd.read_sql(
            f"SELECT * FROM pp_ext_grid WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_ext_grid.csv")
        pd.read_sql(
            f"SELECT * FROM pp_ext_grid_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_ext_grid_meta.csv")
        pd.read_sql(
            f"SELECT * FROM pp_line WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_line.csv")
        pd.read_sql(
            f"SELECT * FROM pp_line_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_line_meta.csv")
        pd.read_sql(
            f"SELECT * FROM pp_load WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_load.csv")
        pd.read_sql(
            f"SELECT * FROM pp_load_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_load_meta.csv")
        pd.read_sql(
            f"SELECT * FROM pp_static_generator WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_static_generator.csv")
        pd.read_sql(
            f"SELECT * FROM pp_static_generator_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_static_generator.csv")
        pd.read_sql(
            f"SELECT * FROM pp_trafo WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_trafo.csv")
        pd.read_sql(
            f"SELECT * FROM pp_trafo_meta WHERE experiment_id = {experiment_id}",
            connections["midas"],
        ).to_csv(f"{path}/pp_trafo_meta.csv")

        # export ERD
        erd_path = os.path.join(
            settings.DIR_EXPERIMENTS, f"{experiment_id}_user.yml"
        )
        shutil.copyfile(
            erd_path, os.path.join(path, f"{experiment_id}_user.yml")
        )

        # export palaestrai-DB

        agents_informations = pd.read_sql(
            f"SELECT agents.id, agents.name FROM agents LEFT JOIN experiment_run_phases "
            f"ON agents.experiment_run_phase_id = experiment_run_phases.id "
            f"LEFT JOIN experiment_run_instances ON experiment_run_phases.experiment_run_instance_id = experiment_run_instances.id "
            f"LEFT JOIN experiment_runs ON experiment_run_instances.experiment_run_id = experiment_runs.id "
            f"WHERE CAST(experiment_runs.uid AS INTEGER) = {experiment_id} ",
            connections["palaestrai"],
        )

        for index, agent in agents_informations.iterrows():
            pd.read_sql(
                f"SELECT * FROM brain_states WHERE agent_id = {agent['id']}",
                connections["palaestrai"],
            ).to_csv(f"{path}/{agent['name']}_brain_states.csv")

        for index, agent in agents_informations.iterrows():
            pd.read_sql(
                f"SELECT * FROM muscle_actions WHERE agent_id = {agent['id']}",
                connections["palaestrai"],
            ).to_csv(f"{path}/{agent['name']}_muscle_actions.csv")

        zippath = os.path.join(
            settings.DIR_EXPERIMENT_EXPORT,
            "zipped",
            f"results_experiment_{experiment_id}",
        )
        shutil.make_archive(zippath, "zip", path)

    return HttpResponse(content="Generated")


def export_results(experiment_id):
    zippath = os.path.join(
        settings.DIR_EXPERIMENT_EXPORT,
        "zipped",
        f"results_experiment_{experiment_id}",
    )
    response = FileResponse(open(zippath + ".zip", "rb"))
    return response
