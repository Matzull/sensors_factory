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
sensor_counter = [0 for _ in range(SENSOR_NUM)]


async def fetch_sensor_data():
    global counter
    async with websockets.connect(WS_URL) as websocket:
        async for message in websocket:
            data = json.loads(message)
            (sensor_data[int(data["sensor_id"])][0]).append(
                datetime.fromtimestamp(data["timestamp"]).strftime("%H:%M:%S")
            )  #
            (sensor_data[int(data["sensor_id"])][1]).append(data["value"])
            (sensor_data[int(data["sensor_id"])][2]).append(
                sensor_counter[int(data["sensor_id"])]
            )
            sensor_counter[int(data["sensor_id"])] += 1


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
    fig = subplots.make_subplots(
        rows=5,
        cols=2,
        subplot_titles=[f"Sensor {i}" for i in range(SENSOR_NUM)],
    )
    for i, (labels, values, counter) in enumerate(sensor_data):
        fig.add_trace(
            go.Scatter(
                x=list(labels),
                y=list(values),
                mode="lines+markers",
                name=f"Sensor {i}",
                marker=dict(size=6, color="rgb(31, 119, 180)"),
                line=dict(width=2),
            ),
            row=(i // 2) + 1,
            col=(i % 2) + 1,
        )
        if len(labels) | len(values) < 2:
            continue
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
            tickmode="array",
            tickvals=list(labels),
            ticktext=list(x_labels),
            title="Timestamps",
            title_font=dict(size=14),
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor="lightgray",
        )

        fig.update_yaxes(
            range=[min_Y - y_offset, max_Y + y_offset],
            row=(i // 2) + 1,
            col=(i % 2) + 1,
            title="Values",
            title_font=dict(size=14),
            tickfont=dict(size=10),
            showgrid=True,
            gridcolor="lightgray",
        )

    fig.update_layout(
        title="Sensor Data Monitoring",
        title_font=dict(size=20, color="darkblue"),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(240, 240, 240, 1)",
        plot_bgcolor="rgba(245, 245, 245, 1)",
        font=dict(family="Arial", size=12, color="black"),
        showlegend=True,
        height=200 + (len(sensor_data) // 2) * 150,
    )

    return fig


fetch_thread = threading.Thread(target=run_fetch_data, daemon=True)
fetch_thread.start()

app.run(debug=True)
