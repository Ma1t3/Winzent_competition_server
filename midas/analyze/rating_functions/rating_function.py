from abc import abstractmethod


class RatingFunction:
    """Abstract class for rating functions"""

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
        self.bus_health = bus_health
        self.ext_grid_health = ext_grid_health
        self.line_health = line_health
        self.trafo_health = trafo_health
        self.load_health = load_health
        self.const_max_percentage_trafos = const_max_percentage_trafos
        self.const_max_percentage_lines = const_max_percentage_lines
        self.const_voltage = const_voltage
        self.const_voltage_timed = const_voltage_timed
        self.const_voltage_change = const_voltage_change
        self.const_reactive_power = const_reactive_power

    @abstractmethod
    def compute_results(self):
        pass
