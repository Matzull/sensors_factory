import random


class Sensor:
    def __init__(
        self,
        sensor_type,
        min_value,
        max_value,
        unit,
        sensor_id,
        system_id,
        frequency=2,
        distribution="normal",
        std_dev=1,
    ):
        self.sensor_type = sensor_type
        self.min_value = min_value
        self.max_value = max_value
        self.unit = unit
        self.sensor_id = sensor_id
        self.system_id = system_id
        self.frequency = frequency
        self.distribution = distribution
        self.std_dev = std_dev
        self.value = self.generate_value()

    def generate_value(self):
        if self.distribution == "uniform":
            return round(random.uniform(self.min_value, self.max_value), 2)
        elif self.distribution == "normal":
            mean = (self.min_value + self.max_value) / 2
            value = random.gauss(mean, self.std_dev)
            return round(min(max(self.min_value, value), self.max_value), 2)

    def update_value(self):
        self.value = self.generate_value()

    def get_sensor_type(self):
        return self.sensor_type

    def get_unit(self):
        return self.unit

    def get_sensor_id(self):
        return self.sensor_id

    def get_system_id(self):
        return self.system_id

    def __str__(self) -> str:
        return f"Sensor - {self.sensor_id} System - {self.system_id} -> {self.value} {self.unit}"

    def to_dict(self):
        return {
            "sensor_id": self.sensor_id,
            "system_id": self.system_id,
            "sensor_type": self.sensor_type,
            "frequency": self.frequency,
            "value": self.value,
            "unit": self.unit,
        }
