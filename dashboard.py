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

# Initialize the data structure
X = deque(maxlen=20)
Y = deque(maxlen=20)

# WebSocket connection URL to your FastAPI
WS_URL = "ws://localhost:8998/ws/real_time_data"

# Global variable to store the latest sensor data
last_index = 0

# Function to get data from WebSocket


async def fetch_sensor_data():
    global X, Y, last_index
    async with websockets.connect(WS_URL) as websocket:
        async for message in websocket:
            data = json.loads(message)
            X.append(last_index)
            Y.append(data["value"])
            last_index += 1


# Function to run the async event loop in a separate thread
def run_fetch_data():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_sensor_data())


# Start the WebSocket data fetch in a separate thread
fetch_thread = threading.Thread(target=run_fetch_data, daemon=True)
fetch_thread.start()

# Initialize the Dash app
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
    fig = subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig.add_trace(
        go.Scatter(x=list(X), y=list(Y), mode="lines+markers", name="Sensor Data")
    )
    y_offset = (max(Y) - min(Y)) * 0.05
    x_offset = (max(X) - min(X)) * 0.05
    return {
        "data": fig.data,
        "layout": go.Layout(
            xaxis=dict(range=[min(X) - x_offset, max(X) + x_offset]),
            yaxis=dict(range=[min(Y) - y_offset, max(Y) + y_offset]),
        ),
    }


if __name__ == "__main__":
    app.run(debug=True)
