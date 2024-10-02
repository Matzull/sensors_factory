from sensors import power, pressure, temperature, rotation, water_level


class SensorFactory:
    sensor_number = -1

    @staticmethod
    def get_id():
        SensorFactory.sensor_number += 1
        return SensorFactory.sensor_number

    @staticmethod
    def create_sensor(min_value, max_value, sensor_type, system_id, frequency=2):
        if sensor_type == "power":
            return power.Power_Sensor(
                min_value=min_value,
                max_value=max_value,
                sensor_id=SensorFactory.get_id(),
                system_id=system_id,
                frequency=frequency,
            )
        elif sensor_type == "pressure":
            return pressure.Pressure_Sensor(
                min_value=min_value,
                max_value=max_value,
                sensor_id=SensorFactory.get_id(),
                system_id=system_id,
                frequency=frequency,
            )
        elif sensor_type == "temperature":
            return temperature.Temperature_Sensor(
                min_value=min_value,
                max_value=max_value,
                sensor_id=SensorFactory.get_id(),
                system_id=system_id,
                frequency=frequency,
            )
        elif sensor_type == "rotation":
            return rotation.Rotation_Sensor(
                min_value=min_value,
                max_value=max_value,
                sensor_id=SensorFactory.get_id(),
                system_id=system_id,
                frequency=frequency,
            )
        elif sensor_type == "water_level":
            return water_level.Water_Level_Sensor(
                min_value=min_value,
                max_value=max_value,
                sensor_id=SensorFactory.get_id(),
                system_id=system_id,
                frequency=frequency,
            )
        else:
            raise ValueError("Invalid sensor type")
