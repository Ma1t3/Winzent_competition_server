from importlib import import_module

import pandas as pd
import sqlalchemy as sa

from pgasc.midas.analyze.bus_analysis import analyze_buses
from pgasc.midas.analyze.ext_grid_analysis import analyze_ext_grid
from pgasc.midas.analyze.line_analysis import analyze_line
from pgasc.midas.analyze.load_analysis import analyze_load
from pgasc.midas.analyze.power_analysis import analyze_power
from pgasc.midas.analyze.trafo_analysis import analyze_trafo
from pgasc.midas.store.model.midas_model import (
    ExperimentResult,
    PPBus,
    PPTrafoMeta,
    Constraint,
    PPLineMeta,
    PPStaticGeneratorMeta,
    PPLoad,
    PPStaticGenerator,
    PPExtGrid,
    PPLine,
    PPTrafo,
)


class ExperimentRunAnalyse:
    def __init__(self, session, step_size, end, experiment_id):
        self.session = session
        self.step_size = step_size
        self.end = end
        self.experiment_id = experiment_id

    def analyze_grid(self):
        ef = self.step_size / 3_600

        self._analyse_loads(ef)
        self._analyse_sgens(ef)
        self._analyse_ext_grids(ef)

        self.session.commit()

    def _analyse_loads(self, ef):
        # get list of all loads
        query = self.session.query(PPLoad).filter(
            PPLoad.experiment_id == self.experiment_id
        )

        df = pd.read_sql(query.statement, self.session.bind)

        # calculations copied from midas
        load_totals = analyze_power(df, self.step_size)

        total_active_energy_demand = load_totals[0].sum() * ef
        total_reactive_energy_demand = load_totals[1].sum() * ef
        total_apparent_energy_demand = load_totals[2]

        self._save_experiment_result(
            "total active energy demand", total_active_energy_demand, "MWh"
        )
        self._save_experiment_result(
            "total reactive energy demand",
            total_reactive_energy_demand,
            "MVArh",
        )
        self._save_experiment_result(
            "total apparent energy demand",
            total_apparent_energy_demand,
            "MVAh",
        )

    def _analyse_sgens(self, ef):
        # get list of all sgens
        query = self.session.query(PPStaticGenerator).filter(
            PPStaticGenerator.experiment_id == self.experiment_id
        )

        df = pd.read_sql(query.statement, self.session.bind)

        # calculations copied from midas
        gen_totals = analyze_power(df, self.step_size)
        total_active_energy_supply = gen_totals[0].sum() * ef
        total_reactive_energy_supply = gen_totals[1].sum() * ef
        total_apparent_energy_supply = gen_totals[2]

        self._save_experiment_result(
            "total active energy supply", total_active_energy_supply, "MWh"
        )
        self._save_experiment_result(
            "total reactive energy supply",
            total_reactive_energy_supply,
            "MVArh",
        )
        self._save_experiment_result(
            "total apparent energy supply",
            total_apparent_energy_supply,
            "MVAh",
        )

    def _analyse_ext_grids(self, ef):
        # get list of all ext_grids
        query = self.session.query(PPExtGrid).filter(
            PPExtGrid.experiment_id == self.experiment_id
        )
        df = pd.read_sql(query.statement, self.session.bind)

        # calculations copied from midas
        extg_totals = analyze_power(df, self.step_size)
        extg_active_energy_supply = extg_totals[0].sum() * ef
        extg_reactive_energy_supply = extg_totals[1].sum() * ef
        extg_apparent_energy_supply = extg_totals[2]

        self._save_experiment_result(
            "extg. active energy supply", extg_active_energy_supply, "MWh"
        )
        self._save_experiment_result(
            "extg. reactive energy supply",
            extg_reactive_energy_supply,
            "MVArh",
        )
        self._save_experiment_result(
            "extg. apparent energy supply", extg_apparent_energy_supply, "MVAh"
        )

    def rating_grid(self, rating_function):
        # calculate bus health
        bus_health = analyze_buses(
            self.session.query(PPBus)
            .filter(PPBus.experiment_id == self.experiment_id)
            .all()
        )
        self._save_experiment_result("Bus health", bus_health, "%")

        # calculate ext grid health
        ext_grid_health = analyze_ext_grid(
            self.session.query(PPExtGrid)
            .filter(PPExtGrid.experiment_id == self.experiment_id)
            .all()
        )
        self._save_experiment_result("Ext grid health", ext_grid_health, "%")

        # calculate line health
        line_health = analyze_line(
            self.session.query(PPLine)
            .filter(PPLine.experiment_id == self.experiment_id)
            .all()
        )
        self._save_experiment_result("Line health", line_health, "%")

        # calculate trafo health
        trafo_health = analyze_trafo(
            self.session.query(PPTrafo)
            .filter(PPTrafo.experiment_id == self.experiment_id)
            .all()
        )
        self._save_experiment_result("Trafo health", trafo_health, "%")

        # calculate load health
        load_health = analyze_load(
            self.session.query(PPLoad)
            .filter(PPLoad.experiment_id == self.experiment_id)
            .all()
        )
        self._save_experiment_result("Load health", load_health, "%")

        # calc constrained max percent trafos rating
        const_max_percentage_trafos = self._calculate_ratio(
            "ConstraintMaxPercentTrafo",
            PPTrafoMeta,
            "Constraint Max Percent Trafo",
        )
        # calc constrained max percent line rating
        const_max_percentage_lines = self._calculate_ratio(
            "ConstraintMaxPercentLine",
            PPLineMeta,
            "Constraint Max Percent Line",
        )

        # calc constrained voltage rating
        const_voltage = self._calculate_ratio(
            "ConstraintVoltage",
            PPStaticGeneratorMeta,
            "Constraint Voltage",
            True,
        )

        # calc constrained voltage timed rating
        const_voltage_timed = self._calculate_ratio(
            "ConstraintVoltageTimed",
            PPStaticGeneratorMeta,
            "Constraint Voltage Timed",
            True,
        )

        # calc constrained voltage change rating
        const_voltage_change = self._calc_const_voltage_change_rating()

        # calc constrained reactive power rating
        const_reactive_power = self._calculate_ratio(
            "ConstraintReactivePower",
            PPStaticGeneratorMeta,
            "Constraint Reactive Power",
            True,
        )

        # calc result from rating function
        module_path, class_name = rating_function.rsplit(".", 1)

        module = import_module(module_path)

        rating = getattr(module, class_name)(
            bus_health,
            ext_grid_health,
            line_health,
            trafo_health,
            load_health,
            const_max_percentage_trafos,
            const_max_percentage_lines,
            const_voltage,
            const_voltage_timed,
            const_voltage_change,
            const_reactive_power,
        )

        rating_points = rating.compute_results()
        self._save_experiment_result(
            "Rating function", rating_points, "points"
        )

        self.session.commit()

    def _calc_const_voltage_change_rating(self):
        number_sgen = self._count_powergrid_elements(PPStaticGeneratorMeta)
        number_load = self._count_powergrid_elements(PPLoad)

        number_all = number_sgen + number_load * self.end / self.step_size

        failed_const = self._count_failed_const("ConstraintVoltageChange")

        const_percent = 100 - round(failed_const / number_all, 2)
        self._save_experiment_result(
            "Constraint Voltage Change", const_percent, "%"
        )

        return const_percent

    def _calculate_ratio(self, const_key, meta_table, name, time=False):
        number_all = self._count_powergrid_elements(meta_table)
        if time:
            number_all = number_all * self.end / self.step_size
        failed_const = self._count_failed_const(const_key)

        const_percent = (1 - round((failed_const / number_all), 2)) * 100
        self._save_experiment_result(name, const_percent, "%")

        return const_percent

    def _count_failed_const(self, const_key):
        query = (
            self.session.query(sa.func.count(Constraint.id))
            .filter(Constraint.experiment_id == self.experiment_id)
            .filter(Constraint.key == const_key)
        )
        return query[0][0]

    def _count_powergrid_elements(self, meta_table):
        query = self.session.query(
            sa.func.count(sa.distinct(meta_table.pp_index))
        ).filter(meta_table.experiment_id == self.experiment_id)
        return query[0][0]

    def _save_experiment_result(self, name, value, unit):
        self.session.add(
            ExperimentResult(
                experiment_id=self.experiment_id,
                name=name,
                value=value,
                unit=unit,
            )
        )
