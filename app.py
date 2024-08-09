import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask, redirect
from graph import register_callbacks
from in_it import prepare_data

server = Flask(__name__)

app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

directory = 'datas'
calculated_results = prepare_data(directory)

data_options = [
    {'label': 'Video Start Count', 'value': 'video_start_count'},
    {'label': 'Audio Start Count', 'value': 'audio_start_count'},
    {'label': 'Answer Count', 'value': 'answer_count'},
    {'label': 'Answer Time', 'value': 'answer_time'}
]

app.layout = html.Div([
    dcc.Dropdown(
        id='parameter-dropdown',
        options=data_options,
        value=data_options[0]['value'] if data_options else None
    ),
    dcc.Graph(
        id='parameter-graph',
        style={'height': '70vh', 'overflowX': 'auto'}
    )
])

register_callbacks(app, calculated_results)

@server.route('/')
def index():
    return redirect('/dashboard/')

if __name__ == '__main__':
    server.run(debug=True)
