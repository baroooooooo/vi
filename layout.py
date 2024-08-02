import dash
from dash import dcc, html

def create_layout(attendance_options, data_options):
    return html.Div([
        dcc.Dropdown(
            id='attendance-dropdown',
            options=attendance_options,
            value=attendance_options[0]['value'] if attendance_options else None
        ),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=data_options,
            value=data_options[0]['value'] if data_options else None
        ),
        dcc.Graph(
            id='parameter-graph',
            style={'height': '70vh', 'overflowX': 'scroll'}  # スクロールを有効にするためのスタイル設定
        )
    ])
