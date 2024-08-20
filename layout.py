from dash import dcc, html

def create_layout(years, data_options):
    return html.Div([
        html.H1('Dashboard'),
        
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in years],
                value=years[0]  # 初期値を設定
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='parameter-dropdown',
                options=data_options,
                value=data_options[0]['value'] if data_options else None
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        dcc.Graph(
            id='parameter-graph',
            style={'height': '70vh', 'overflowX': 'auto'}
        )
    ])
