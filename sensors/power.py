from sensors.sensor import Sensor


class Power_Sensor(Sensor):
    def __init__(
        self,
        min_value,
        max_value,
        sensor_id,
        system_id,
        frequency=2,
        distribution="normal",
        std_dev=1,
    ):
        super().__init__(
            "Power Sensor",
            min_value,
            max_value,
            "W",
            sensor_id,
            system_id,
            frequency,
            distribution,
            std_dev,
        )

    def __str__(self) -> str:
        return f"Power Sensor - {self.sensor_id} System - {self.system_id} -> {self.value} {self.unit}"
