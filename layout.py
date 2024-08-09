import dash
from dash import dcc, html

def create_layout(attendance_options, data_options):
    return html.Div([
        dcc.Dropdown(
            id='parameter-dropdown',
            options=data_options,
            value=data_options[0]['value'] if data_options else None
        ),
        dcc.Graph(
            id='parameter-graph',
            style={'height': '70vh', 'overflowX': 'auto'}  # スクロールを有効にするためのスタイル設定
        )
    ])
