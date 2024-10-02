import dash
from dash.dependencies import Output, Input
from dash import dcc, html
import plotly.graph_objs as go
from collections import deque
import websockets
import asyncio
import json
import threading
import plotly.subplots as subplots
from datetime import datetime

WS_URL = "ws://localhost:8998/ws/real_time_data"
SENSOR_NUM = 10
sensor_data = [
    (deque(maxlen=100), deque(maxlen=100), deque(maxlen=100)) for _ in range(SENSOR_NUM)
]
counter = 0


async def fetch_sensor_data():
    global counter
    async with websockets.connect(WS_URL) as websocket:
        async for message in websocket:
            data = json.loads(message)
            (sensor_data[int(data["sensor_id"])][0]).append(
                datetime.fromtimestamp(data["timestamp"]).strftime("%H:%M:%S")
            )  #
            (sensor_data[int(data["sensor_id"])][1]).append(data["value"])
            (sensor_data[int(data["sensor_id"])][2]).append(counter)
            counter += 1


def run_fetch_data():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_sensor_data())


app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id="live-graph", animate=True),
        dcc.Interval(
            id="graph-update",
            interval=1 * 1000,  # 1 second interval
            n_intervals=0,
        ),
    ]
)


@app.callback(Output("live-graph", "figure"), [Input("graph-update", "n_intervals")])
def update_graph_scatter(n):
    fig = subplots.make_subplots(rows=5, cols=2)
    for i, (labels, values, counter) in enumerate(sensor_data):
        fig.add_trace(
            go.Scatter(
                x=list(labels), y=list(values), mode="lines+markers", name=f"Sensor {i}"
            ),
            row=(i // 2) + 1,
            col=(i % 2) + 1,
        )
        if len(labels) | len(values) < 2:
            return {"data": fig.data}
        min_Y, max_Y = min(values), max(values)
        min_Z, max_Z = min(counter), max(counter)
        y_offset = (max_Y - min_Y) * 0.5
        z_offset = (max_Z - min_Z) * 0.05
        x_labels = [
            label if index % 2 == 0 else "" for index, label in enumerate(labels)
        ]
        fig.update_xaxes(
            range=[min_Z - z_offset, max_Z + z_offset],
            row=(i // 2) + 1,
            col=(i % 2) + 1,
        )
        fig.update_yaxes(
            range=[min_Y - y_offset, max_Y + y_offset],
            row=(i // 2) + 1,
            col=(i % 2) + 1,
            
        )
    return {
        "data": fig.data,
        "layout": go.Layout(
            xaxis=dict(
                range=[min_Z - z_offset, max_Z + z_offset],
                tickmode="array",
                tickvals=list(labels),
                ticktext=list(x_labels),
                title="Timestamps",
            ),
            yaxis=dict(range=[min_Y - y_offset, max_Y + y_offset], title="Values"),
        ),
    }


fetch_thread = threading.Thread(target=run_fetch_data, daemon=True)
fetch_thread.start()

app.run(debug=True)
