import csv
import os

from palaestrai.agent import Muscle


class PrintMuscle(Muscle):
    """Muscle that prints all sensor and actuator information to the console."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)

    def setup(self):
        pass

    def propose_actions(self, sensors, actuators_available, is_terminal=False):
        print("SENSORS:")
        print(sensors)
        print("ACTUATORS:")
        print(actuators_available)

        return (
            actuators_available,
            actuators_available,
            [1 for _ in actuators_available],
            {},
        )

    def update(self, update):
        pass

    def __repr__(self):
        pass

    def prepare_model(self):
        pass


class SetNothingMuscle(Muscle):
    """Muscle that does not set any actuators."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)

    def setup(self):
        pass

    def propose_actions(self, sensors, actuators_available, is_terminal=False):
        return (
            actuators_available,
            actuators_available,
            [1 for _ in actuators_available],
            {},
        )

    def update(self, update):
        pass

    def __repr__(self):
        pass

    def prepare_model(self):
        pass


class SaveValuesMuscle(Muscle):
    """Muscle that saves all sensor values to a csv file."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.sensor_occurrences = {}

    def setup(self):
        pass

    def propose_actions(self, sensors, actuators_available, is_terminal=False):
        path = "defender/sensor_values/"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}/sensor_values.csv", "a+") as file:
            writer = csv.writer(file)
            for sensor in sensors:
                if "json" not in sensor.sensor_id:
                    print("sensor: " + sensor.sensor_id)
                    if sensor.sensor_id not in self.sensor_occurrences.keys():
                        self.sensor_occurrences[sensor.sensor_id] = 1
                    else:
                        self.sensor_occurrences[sensor.sensor_id] += 1
                    data = [
                        self.sensor_occurrences[sensor.sensor_id],
                        sensor.sensor_id,
                        sensor.sensor_value,
                    ]
                    writer.writerow(data)
        return (
            actuators_available,
            actuators_available,
            [1 for _ in actuators_available],
            {},
        )

    def update(self, update):
        pass

    def __repr__(self):
        pass

    def prepare_model(self):
        pass


class SetpointMuscle(Muscle):
    """Muscle that sets all actuators to a given setpoint."""

    def __init__(self, broker_uri, brain_uri, uid, brain_id, path, **params):
        super().__init__(broker_uri, brain_uri, uid, brain_id, path)
        self.setpoint = params["setpoint"]

    def setup(self):
        pass

    def propose_actions(self, sensors, actuators_available, is_terminal=False):
        for actuator in actuators_available:
            actuator(self.setpoint)
        return (
            actuators_available,
            actuators_available,
            [1 for _ in actuators_available],
            {},
        )

    def update(self, update):
        pass

    def __repr__(self):
        pass

    def prepare_model(self):
        pass
