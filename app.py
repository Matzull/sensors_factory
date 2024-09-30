from contextlib import asynccontextmanager
import json
import asyncio
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.websockets import WebSocketDisconnect
from sensors.sensor_factory import SensorFactory


class WebSocketManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_text("Connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_update(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except RuntimeError as e:
                print(f"Error sending data to websocket: {e}")
                self.disconnect(connection)


def load_sensors_from_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


async def update_sensor_values(sensor):
    while True:
        await asyncio.sleep(sensor.frequency)
        sensor.update_value()
        updated_sensors.append(sensor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sensors
    sensor_configs = load_sensors_from_json("sensors_config.json")
    for config in sensor_configs:
        sensor = SensorFactory.create_sensor(
            min_value=config["min_value"],
            max_value=config["max_value"],
            sensor_type=config["sensor_type"],
            system_id=config["system_id"],
            frequency=config["frequency"],
        )
        sensors.append(sensor)
        asyncio.create_task(update_sensor_values(sensor))
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/create_sensor/")
async def create_sensor(
    min_value: float, max_value: float, sensor_type: str, system_id: str
):
    try:
        sensor = SensorFactory.create_sensor(
            min_value, max_value, sensor_type, system_id
        )
        sensors.append(sensor)
        return {
            "message": f"{sensor_type} sensor created",
            "sensor_id": sensor.sensor_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/list_sensors/")
async def list_sensors():
    return [
        {
            "sensor_id": sensor.sensor_id,
            "system_id": sensor.system_id,
            "type": sensor.sensor_type,
            "unit": sensor.unit,
        }
        for sensor in sensors
    ]


@app.get("/sensor/{sensor_id}")
async def get_sensor(sensor_id: int):
    sensor = next((sensor for sensor in sensors if sensor.sensor_id == sensor_id), None)
    if sensor:
        return {
            "sensor_id": sensor.sensor_id,
            "type": sensor.system_id,
            "value": sensor.value,
            "unit": sensor.unit,
        }
    else:
        raise HTTPException(status_code=404, detail="Sensor not found")


@app.websocket("/ws/real_time_data")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            sensor_data = [
                {
                    "sensor_id": sensor.sensor_id,
                    "type": sensor.system_id,
                    "value": sensor.value,
                    "unit": sensor.unit,
                }
                for sensor in updated_sensors
            ]
            updated_sensors.clear()
            await manager.send_update(json.dumps(sensor_data))
            await asyncio.sleep(0.25)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/all_sensors/")
async def websocket_endpoint_all(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            sensor_data = [
                {
                    "sensor_id": sensor.sensor_id,
                    "type": sensor.system_id,
                    "value": sensor.value,
                    "unit": sensor.unit,
                }
                for sensor in sensors
            ]
            await manager.send_update(json.dumps(sensor_data))
            await asyncio.sleep(0.25)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


manager = WebSocketManager()

sensors = []
updated_sensors = []
