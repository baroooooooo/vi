from dash import dcc, html


def create_layout(attendance_options, data_options):
    return html.Div(children=[
        html.H1(children='Data Visualization with Dash'),

        html.Div(children=[
            dcc.Dropdown(
                id='attendance-dropdown',
                options=attendance_options,
                value=list(attendance_options[0]['value']),
                clearable=False
            ),
            dcc.Dropdown(
                id='xaxis-column',
                options=data_options,
                value='timeStamp',
                clearable=False
            ),
            dcc.Dropdown(
                id='yaxis-column',
                options=data_options,
                value='actor',
                clearable=False
            ),
            dcc.Graph(id='main-graph'),
            html.Div(children=[
                dcc.Dropdown(
                    id='individual-dropdown',
                    options=[],
                    value=None,
                    clearable=False
                ),
                dcc.Graph(id='individual-graph')
            ])
        ])
    ])
