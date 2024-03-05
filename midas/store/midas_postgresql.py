import os
from datetime import datetime, timedelta

import mosaik_api
import pandapower as pp
import sqlalchemy as sa

from pgasc.midas.analyze.analysis import ExperimentRunAnalyse
from pgasc.midas.store.palaestrai_database_helper import (
    PalaestraiDatabaseHelper,
)
from pgasc.midas.store.model.midas_model import Model
from pgasc.midas.store.model.midas_model import (
    PPStaticGenerator,
    PPStaticGeneratorMeta,
    PPLoadMeta,
    PPLoad,
    PPBusMeta,
    PPBus,
    PPLineMeta,
    PPLine,
    PPTrafoMeta,
    PPTrafo,
    PPExtGridMeta,
    PPExtGrid,
    Constraint,
)

META = {
    "type": "time-based",
    "models": {
        "Database": {
            "public": True,
            "any_inputs": True,
            "params": ["filename", "verbose", "buffer_size", "overwrite"],
            "attrs": [],
        }
    },
}


class MidasPostgresql(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self._db_engine = None
        self._db_session_maker = None
        self._db_session = None
        self.experiment_id = None
        self.end = None
        self.eid = "Database"

    def init(self, sid, **sim_params):
        self.sid = sid
        self.store_uri = self._generate_store_uri()

        self.step_size = sim_params.get("step_size", 900)
        self.end = sim_params.get("end", 0)
        self.start_date = sim_params.get(
            "start_date", "2017-01-01 00:00:00+0100"
        )

        self.write_in_database = sim_params.get("write_in_database", True)
        if not self.write_in_database:
            return self.meta

        uid = sim_params.get("uid", "-1")

        if (
            self.store_uri == ""
            or not uid.strip("-").isnumeric()
            or int(uid) <= -1
        ):
            return self.meta

        self.experiment_id = int(uid)

        # create model
        self._db_engine = sa.create_engine(self.store_uri)
        Model.metadata.create_all(self._db_engine)

        self._delete_experiment()

        return self.meta

    def create(self, num, model, **model_params):
        return [{"eid": self.eid, "type": model}]

    def step(self, time, inputs, max_advance=0):
        """Write to Result Database after every step

        Parameters
        ----------
        time : int
            The current simulation step (by convention in seconds since
            simulation start.
        inputs : dict
            A *dict* containing inputs for entities of this simulator.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.
        """

        # abort if no database is provided by yaml
        if (
            (not self.write_in_database)
            or self.store_uri == ""
            or self.experiment_id is None
        ):
            return time + self.step_size

        grid = pp.from_json_string(
            inputs[self.eid]["grid_json"]["Powergrid-0.Grid-0"]
        )

        constraints = {}
        if "constraints" in inputs[self.eid]:
            constraints = inputs[self.eid]["constraints"][
                "Powergrid-0.Grid-0"
            ]["Grid-0"]

        # create meta tables at the beginning of the simulation
        if time == 0:
            self._save_meta_tables(grid)

        # write the pandapower simulation results to the Database
        self._save_step_results(grid, constraints, time)

        self.disable()
        return time + self.step_size

    def _delete_experiment(self):
        self._delete_experiment_table(Constraint)
        self._delete_experiment_table(PPBus)
        self._delete_experiment_table(PPBusMeta)
        self._delete_experiment_table(PPExtGrid)
        self._delete_experiment_table(PPExtGridMeta)
        self._delete_experiment_table(PPLine)
        self._delete_experiment_table(PPLineMeta)
        self._delete_experiment_table(PPLoad)
        self._delete_experiment_table(PPLoadMeta)
        self._delete_experiment_table(PPStaticGenerator)
        self._delete_experiment_table(PPStaticGeneratorMeta)
        self._delete_experiment_table(PPTrafo)
        self._delete_experiment_table(PPTrafoMeta)
        self._dbh().commit()

    def _delete_experiment_table(self, table):
        self._dbh().query(table).filter(
            table.experiment_id == self.experiment_id
        ).delete()

    def _save_step_results(self, grid, constraints, time):
        # calc step time
        date_format_str = "%Y-%m-%d %H:%M:%S%z"
        given_time = datetime.strptime(self.start_date, date_format_str)
        final_time = given_time + timedelta(seconds=time)

        # Every pandapower component gets a table. The table contains parameters which can change every in step.
        try:
            self._save_sgen(self._dbh(), grid, final_time)
            self._save_load(self._dbh(), grid, final_time)
            self._save_bus(self._dbh(), grid, final_time)
            self._save_constraints(self._dbh(), constraints, final_time)
            self._save_line(self._dbh(), grid, final_time)
            self._save_trafo(self._dbh(), grid, final_time)
            self._save_ext_grid(self._dbh(), grid, final_time)
            self._dbh().commit()

            if time == (self.end - self.step_size):  # end of simulation
                self._analyze_results()

        except Exception:
            # If one save operation fails, the whole process is rolled back
            self._dbh().rollback()
            self.disable()
            raise

    def _analyze_results(self):
        self.palaestrai_database_helper = PalaestraiDatabaseHelper(
            self.experiment_id
        )
        # get rating function of ExperimentRunDefinition
        rating_function = (
            self.palaestrai_database_helper.get_experiment_rating_function()
        )

        # calc rating grid and save in database
        experiment_run_analyse = ExperimentRunAnalyse(
            self._dbh(), self.step_size, self.end, self.experiment_id
        )
        experiment_run_analyse.analyze_grid()
        experiment_run_analyse.rating_grid(rating_function)

    def _save_sgen(self, session, grid, final_time):
        for index, res in grid.res_sgen.iterrows():
            in_service = grid.sgen.iloc[index]["in_service"]
            scaling = grid.sgen.iloc[index]["scaling"]
            session.add(
                PPStaticGenerator(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    p_mw=res["p_mw"],
                    q_mvar=res["q_mvar"],
                    scaling=scaling,
                    in_service=in_service,
                )
            )

    def _save_load(self, session, grid, final_time):
        for index, res in grid.res_load.iterrows():
            in_service = grid.load.iloc[index]["in_service"]
            scaling = grid.load.iloc[index]["scaling"]
            session.add(
                PPLoad(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    p_mw=res["p_mw"],
                    q_mvar=res["q_mvar"],
                    scaling=scaling,
                    in_service=in_service,
                )
            )

    def _save_bus(self, session, grid, final_time):
        for index, res in grid.res_bus.iterrows():
            in_service = grid.bus.iloc[index]["in_service"]
            session.add(
                PPBus(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    vm_pu=res["vm_pu"],
                    va_degree=res["va_degree"],
                    p_mw=res["p_mw"],
                    q_mvar=res["q_mvar"],
                    in_service=in_service,
                )
            )

    def _save_line(self, session, grid, final_time):
        for index, res in grid.res_line.iterrows():
            in_service = grid.line.iloc[index]["in_service"]
            session.add(
                PPLine(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    p_from_mw=res["p_from_mw"],
                    q_from_mvar=res["q_from_mvar"],
                    p_to_mw=res["p_to_mw"],
                    q_to_mvar=res["q_to_mvar"],
                    pl_mw=res["pl_mw"],
                    ql_mvar=res["ql_mvar"],
                    i_from_ka=res["i_from_ka"],
                    i_to_ka=res["i_to_ka"],
                    i_ka=res["i_ka"],
                    vm_from_pu=res["vm_from_pu"],
                    va_from_degree=res["va_from_degree"],
                    vm_to_pu=res["vm_to_pu"],
                    va_to_degree=res["va_to_degree"],
                    loading_percent=res["loading_percent"],
                    in_service=in_service,
                )
            )

    def _save_trafo(self, session, grid, final_time):
        for index, res in grid.res_trafo.iterrows():
            in_service = grid.trafo.iloc[index]["in_service"]
            session.add(
                PPTrafo(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    p_hv_mw=res["p_hv_mw"],
                    q_hv_mvar=res["q_hv_mvar"],
                    p_lv_mw=res["p_lv_mw"],
                    q_lv_mvar=res["q_lv_mvar"],
                    pl_mw=res["pl_mw"],
                    ql_mvar=res["ql_mvar"],
                    i_hv_ka=res["i_hv_ka"],
                    i_lv_ka=res["i_lv_ka"],
                    vm_hv_pu=res["vm_hv_pu"],
                    va_hv_degree=res["va_hv_degree"],
                    vm_lv_pu=res["vm_lv_pu"],
                    va_lv_degree=res["va_lv_degree"],
                    loading_percent=res["loading_percent"],
                    in_service=in_service,
                )
            )

    def _save_ext_grid(self, session, grid, final_time):
        for index, res in grid.res_ext_grid.iterrows():
            in_service = grid.bus.iloc[index]["in_service"]
            session.add(
                PPExtGrid(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    time=final_time,
                    p_mw=res["p_mw"],
                    q_mvar=res["q_mvar"],
                    in_service=in_service,
                )
            )

    def _save_meta_tables(self, grid):
        """
        Every pandapower component gets a meta table. The meta table contains parameters which stay the same the whole
        experiment. Example: The Name of a Generator. The GeneratorID is then referenced by the not meta generator
        table.
        """
        try:
            self._save_sgen_meta(self._dbh(), grid)
            self._save_load_meta(self._dbh(), grid)
            self._save_bus_meta(self._dbh(), grid)
            self._save_line_meta(self._dbh(), grid)
            self._save_trafo_meta(self._dbh(), grid)
            self._save_ext_grid_meta(self._dbh(), grid)
            self._dbh().commit()
        except Exception:
            # If one save operation fails, the whole process is rolled back
            self._dbh().rollback()
            self.disable()
            raise

    def _save_sgen_meta(self, session, grid):
        for index, sgen in grid.sgen.iterrows():
            x = grid.bus_geodata.iloc[sgen["bus"]]["x"]
            y = grid.bus_geodata.iloc[sgen["bus"]]["y"]
            session.merge(
                PPStaticGeneratorMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=sgen["name"],
                    x=x,
                    y=y,
                )
            )

    def _save_load_meta(self, session, grid):
        for index, load in grid.load.iterrows():
            x = grid.bus_geodata.iloc[load["bus"]]["x"]
            y = grid.bus_geodata.iloc[load["bus"]]["y"]
            session.merge(
                PPLoadMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=load["name"],
                    x=x,
                    y=y,
                )
            )

    def _save_bus_meta(self, session, grid):
        for index, bus in grid.bus.iterrows():
            session.merge(
                PPBusMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=bus["name"],
                    vn_kv=bus["vn_kv"],
                    type=bus["type"],
                    zone=bus["zone"],
                )
            )

    def _save_line_meta(self, session, grid):
        for index, line in grid.line.iterrows():
            session.merge(
                PPLineMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=line["name"],
                    std_type=line["std_type"],
                    from_bus=line["from_bus"],
                    to_bus=line["to_bus"],
                    length_km=line["length_km"],
                    r_ohm_per_km=line["r_ohm_per_km"],
                    x_ohm_per_km=line["x_ohm_per_km"],
                    c_nf_per_km=line["c_nf_per_km"],
                    max_i_ka=line["max_i_ka"],
                    df=line["df"],
                    parallel=line["parallel"],
                    type=line["type"],
                )
            )

    def _save_trafo_meta(self, session, grid):
        for index, trafo in grid.trafo.iterrows():
            session.merge(
                PPTrafoMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=trafo["name"],
                    std_type=trafo["std_type"],
                    hv_bus=trafo["hv_bus"],
                    lv_bus=trafo["lv_bus"],
                    sn_mva=trafo["sn_mva"],
                    vn_hv_kv=trafo["vn_hv_kv"],
                    vn_lv_kv=trafo["vn_lv_kv"],
                    vk_percent=trafo["vk_percent"],
                    vkr_percent=trafo["vkr_percent"],
                    pfe_kw=trafo["pfe_kw"],
                    i0_percent=trafo["i0_percent"],
                    shift_degree=trafo["shift_degree"],
                    tap_step_percent=trafo["tap_step_percent"],
                    tap_step_degree=trafo["tap_step_degree"],
                    tap_pos=trafo["tap_pos"],
                    tap_phase_shifter=trafo["tap_phase_shifter"],
                )
            )

    def _save_ext_grid_meta(self, session, grid):
        for index, ext_grid in grid.ext_grid.iterrows():
            session.merge(
                PPExtGridMeta(
                    experiment_id=self.experiment_id,
                    pp_index=index,
                    name=ext_grid["name"],
                    bus=ext_grid["bus"],
                )
            )

    def _save_constraints(self, session, constraints, final_time):
        for key, val in constraints.items():
            keys = key.split("-")
            etype = keys[1]
            pp_index = keys[2]

            for constraint in val:
                session.add(
                    Constraint(
                        experiment_id=self.experiment_id,
                        pp_index=pp_index,
                        type=etype,
                        key=constraint,
                        time=final_time,
                    )
                )

    def _dbh(self):
        # use a session for Database Safe
        if self._db_session is None:
            self._db_engine = sa.create_engine(self.store_uri)
            self._db_session_maker = sa.orm.sessionmaker()
            self._db_session_maker.configure(bind=self._db_engine)
            try:
                self._db_session = self._db_session_maker()
            except Exception:
                self.disable()
                raise
        return self._db_session

    def _generate_store_uri(self):
        db_name = os.environ["MIDAS_DB_NAME"]
        db_user = os.environ["MIDAS_DB_USER"]
        db_pass = os.environ["MIDAS_DB_PASSWORD"]
        db_host = os.environ["MIDAS_DB_HOST"]
        db_port = os.environ["MIDAS_DB_PORT"]
        return (
            f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )

    def disable(self):
        # close open Database session
        if self._db_session:
            self._db_session.close()
        self._db_session = None
