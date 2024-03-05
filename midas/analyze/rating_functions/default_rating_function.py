from pgasc.midas.analyze.rating_functions import rating_function


class DefaultRatingFunction(rating_function.RatingFunction):
    """Our default rating function for experiments"""

    def __init__(
        self,
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
    ):
        super().__init__(
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

    def compute_results(self):
        m_bus_health = 5
        m_ext_grid_health = 5
        m_line_health = 2
        m_trafo_health = 3
        m_load_health = 5
        m_const_max_percentage_trafos = 4
        m_const_max_percentage_lines = 3
        m_const_voltage = 2
        m_const_voltage_timed = 1
        m_const_voltage_change = 1
        m_const_reactive_power = 3

        # result of rating function
        return round(
            self.bus_health * m_bus_health
            + self.ext_grid_health * m_ext_grid_health
            + self.line_health * m_line_health
            + self.trafo_health * m_trafo_health
            + self.load_health * m_load_health
            + self.const_max_percentage_trafos * m_const_max_percentage_trafos
            + self.const_max_percentage_lines * m_const_max_percentage_lines
            + self.const_voltage * m_const_voltage
            + self.const_voltage_timed * m_const_voltage_timed
            + self.const_voltage_change * m_const_voltage_change
            + self.const_reactive_power * m_const_reactive_power,
            2,
        )
