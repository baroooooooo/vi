rom dash.dependencies import Input, Output, State
import plotly.express as px

def register_callbacks(app, data_dict):
    @app.callback(
        Output('main-graph', 'figure'),
        [Input('xaxis-column', 'value'),
         Input('yaxis-column', 'value'),
         Input('attendance-dropdown', 'value')]
    )
    def update_main_graph(xaxis_column_name, yaxis_column_name, attendance_number):
        data = data_dict[attendance_number]
        fig = px.scatter(data, x=xaxis_column_name, y=yaxis_column_name,
                         hover_data=['object', 'result', 'extension'])
        return fig

    @app.callback(
        Output('individual-dropdown', 'options'),
        [Input('attendance-dropdown', 'value')]
    )
    def update_individual_options(attendance_number):
        data = data_dict[attendance_number]
        unique_values = data['object'].unique()
        return [{'label': val, 'value': val} for val in unique_values]

    @app.callback(
        Output('individual-graph', 'figure'),
        [Input('individual-dropdown', 'value'),
         Input('xaxis-column', 'value'),
         Input('yaxis-column', 'value'),
         Input('attendance-dropdown', 'value')]
    )
    def update_individual_graph(selected_object, xaxis_column_name, yaxis_column_name, attendance_number):
        data = data_dict[attendance_number]
        filtered_data = data[data['object'] == selected_object]
        fig = px.scatter(filtered_data, x=xaxis_column_name, y=yaxis_column_name,
                         hover_data=['object', 'result', 'extension'])
        return fig