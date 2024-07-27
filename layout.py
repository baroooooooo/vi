from dash import dcc, html


def create_layout(attendance_options, data_options):
    return html.Div([
        html.H1("データ可視化ダッシュボード"),
        html.Div([
            dcc.Dropdown(
                id='attendance-dropdown',
                options=attendance_options,
                value=attendance_options[0]['value'],
                multi=False
            )
        ]),
        html.Div([
            dcc.Dropdown(
                id='data-dropdown',
                options=data_options,
                value=data_options[0]['value'],
                multi=False
            )
        ]),
        dcc.Graph(id='main-graph'),
        html.Div(id='individual-data')
    ])
