import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    @app.callback(
        Output('parameter-graph', 'figure'),
        [Input('year-dropdown', 'value'),
         Input('parameter-dropdown', 'value')]
    )
    def update_graph(selected_year, selected_parameter):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {}

        year_data = calculated_results.get(selected_year, {})
        print(f'Selected Year: {selected_year}, Data: {year_data}')
    
        attendance_numbers = list(year_data.keys())
        print(f'Attendance Numbers: {attendance_numbers}')
    
        y_values = [int(year_data.get(attendance_number, {}).get(selected_parameter, 0)) for attendance_number in attendance_numbers]
        print(f'Y Values: {y_values}')

        return {
            'data': [
                go.Bar(
                    x=attendance_numbers,
                    y=y_values
                )
            ],
            'layout': {
                'title': f'{selected_parameter} for {selected_year}',
                'xaxis': {'title': 'Attendance Number'},
                'yaxis': {'title': 'Value'}
            }
        }
