import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    @app.callback(
        Output('parameter-graph', 'figure'),
        [Input('parameter-dropdown', 'value')]
    )
    def update_graph(parameter):
        if not calculated_results or parameter is None:
            return {}

        # 出席番号と指定されたパラメータの値を取得
        attendance_numbers = list(calculated_results.keys())
        y_values = [calculated_results[attendance_number].get(parameter, 0) for attendance_number in attendance_numbers]

        return {
            'data': [
                go.Bar(
                    x=attendance_numbers,
                    y=y_values
                )
            ],
            'layout': {
                'title': f'{parameter}',
                'xaxis': {'title': 'Attendance Number'},
                'yaxis': {'title': 'Value'}
            }
        }
