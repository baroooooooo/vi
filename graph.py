from dash.dependencies import Input, Output
import plotly.express as px
from dash import html, dcc
import pandas as pd


def register_callbacks(app, data_dict):
    @app.callback(
        Output('main-graph', 'figure'),
        [Input('data-dropdown', 'value')]
    )
    def update_main_graph(selected_param):
        # 横軸を出席番号、縦軸を選択したパラメータにする
        df = pd.DataFrame()
        for key, data in data_dict.items():
            data['attendance'] = key
            df = pd.concat([df, data])

        fig = px.line(df, x='attendance', y=selected_param,
                      title=f'{selected_param} by Attendance Number')
        return fig

    @app.callback(
        Output('individual-data', 'children'),
        [Input('attendance-dropdown', 'value')]
    )
    def update_individual_data(selected_attendance):
        individual_df = data_dict.get(str(selected_attendance), pd.DataFrame())
        return html.Div([
            html.H3(f'Individual Data for Attendance {selected_attendance}'),
            dcc.Graph(
                figure=px.line(individual_df, x='timeStamp',
                               y=individual_df.columns,
                               title=f'Detailed Data for{selected_attendance}')
            )
        ])
