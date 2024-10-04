import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    @app.callback(
        Output('parameter-graph', 'figure'),
        Output('graph-data', 'data'),
        Input('year-dropdown', 'value'),
        Input('parameter-dropdown', 'value'),
        Input('order-number', 'n_clicks'),
        Input('order-asc', 'n_clicks'),
        Input('order-desc', 'n_clicks'),
        Input('add-graph-button', 'n_clicks'),
        Input('remove-graph-button', 'n_clicks'),
        [State('graph-data', 'data')]
    )
    def update_graph(selected_year, selected_parameter, order_number, order_asc, order_desc, add_graph_n_clicks, remove_graph_n_clicks, existing_graphs):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}, existing_graphs

        # Debugging output to check the structure of calculated_results and year_data
        print(f"calculated_results: {calculated_results}")
        year_data = calculated_results.get(selected_year, {})
        print(f"year_data: {year_data}")

        # Check if 'test_result' exists in year_data
        for attendance_number in year_data:
            test_result = year_data[attendance_number].get('test_result')
            print(f"{attendance_number}のtest_result: {test_result}")
            if test_result is None:
                # Here you might want to add code to handle missing test_result
                print(f"{attendance_number}のtest_resultが存在しません。データを追加する必要があります。")

        # Handle special case when selected_parameter is 'test_result'
        if selected_parameter == 'test_result':
            print("test_resultが選択されています")

        # Extract attendance numbers with the selected parameter
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if year_data[attendance_number].get(selected_parameter) is not None
        ]

        if not attendance_numbers:
            return {'data': [], 'layout': {}}, existing_graphs

        # Sorting logic based on the selected order
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            order = 'asc'
        elif triggered_id == 'order-desc':
            order = 'desc'
        elif triggered_id == 'order-number':
            order = 'number'
        else:
            order = 'number'

        # Sorting attendance numbers
        if order == 'asc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter])
        elif order == 'desc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter], reverse=True)
        elif order == 'number':
            attendance_numbers.sort(key=int)

        # Bar chart data
        x_positions = list(range(len(attendance_numbers)))
        y_values_original = [year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers]

        # Original bar chart for selected parameter
        original_data = go.Bar(
            x=x_positions,
            y=y_values_original,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter} (Original)'
        )

        # Chart layout
        layout = {
            'title': f'{selected_parameter} for {selected_year}',
            'xaxis': {
                'title': 'Attendance Number',
                'tickmode': 'array',
                'tickvals': x_positions,
                'ticktext': attendance_numbers,
            },
            'yaxis': {'title': f'{selected_parameter} Value'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'
        }

        # Initialize existing graphs list if needed
        if existing_graphs is None or isinstance(existing_graphs, dict):
            existing_graphs = []

        # Handle graph addition/removal
        if add_graph_n_clicks > 0:
            existing_graphs.append(dcc.Graph(
                id={'type': 'dynamic-graph', 'index': len(existing_graphs)},
                figure={'data': [original_data], 'layout': layout}
            ))
        elif remove_graph_n_clicks > 0 and existing_graphs:
            existing_graphs.pop()

        return {'data': [original_data], 'layout': layout}, existing_graphs

    
    @app.callback(
        Output('radar-chart', 'figure'),
        [Input('parameter-graph', 'clickData'),  # Click data from bar chart
         Input('year-dropdown', 'value')]  # Selected year
    )
    def display_radar_chart(clickData, selected_year):
        if clickData is None or selected_year is None:
            return {}

        # Extract clicked attendance number
        attendance_number = clickData['points'][0]['text']

        # Retrieve data for the selected attendance number
        data = calculated_results.get(selected_year, {}).get(attendance_number, {})

        if not data:
            return {}

        # Compute the overall maximum values for normalization
        overall_max_values = {
            'video_start_count': max(data.get('video_start_count', 0) for data in calculated_results[selected_year].values()),
            'audio_start_count': max(data.get('audio_start_count', 0) for data in calculated_results[selected_year].values()),
            'answer_count': max(data.get('answer_count', 0) for data in calculated_results[selected_year].values()),
            'correct_answers': max(data.get('correct_answers', 0) for data in calculated_results[selected_year].values()),
            'incorrect_answers': max(data.get('incorrect_answers', 0) for data in calculated_results[selected_year].values()),
            'suspended_count': max(data.get('suspended_count', 0) for data in calculated_results[selected_year].values()),
            'launched_count': max(data.get('launched_count', 0) for data in calculated_results[selected_year].values()),
            'total_answer_time': max(data.get('total_answer_time', 0) for data in calculated_results[selected_year].values()),
            'recording_time': max(data.get('recording_time', 0) for data in calculated_results[selected_year].values()),
            'video_time': max(data.get('video_time', 0) for data in calculated_results[selected_year].values()),
            'recorder_start_count': max(data.get('recorder_start_count', 0) for data in calculated_results[selected_year].values()),
            'movie_completed_count': max(data.get('movie_completed_count', 0) for data in calculated_results[selected_year].values()),
            'continue_count': max(data.get('continue_count', 0) for data in calculated_results[selected_year].values()),
            'result': max(data.get('result', 0) for data in calculated_results[selected_year].values()),
        }

        # Normalize values for radar chart
        normalized_values = [
            data.get('video_start_count', 0) / overall_max_values['video_start_count'] if overall_max_values['video_start_count'] > 0 else 0,
            data.get('audio_start_count', 0) / overall_max_values['audio_start_count'] if overall_max_values['audio_start_count'] > 0 else 0,
            data.get('answer_count', 0) / overall_max_values['answer_count'] if overall_max_values['answer_count'] > 0 else 0,
            data.get('correct_answers', 0) / overall_max_values['correct_answers'] if overall_max_values['correct_answers'] > 0 else 0,
            data.get('incorrect_answers', 0) / overall_max_values['incorrect_answers'] if overall_max_values['incorrect_answers'] > 0 else 0,
            data.get('suspended_count', 0) / overall_max_values['suspended_count'] if overall_max_values['suspended_count'] > 0 else 0,
            data.get('launched_count', 0) / overall_max_values['launched_count'] if overall_max_values['launched_count'] > 0 else 0,
            data.get('total_answer_time', 0) / overall_max_values['total_answer_time'] if overall_max_values['total_answer_time'] > 0 else 0,
            data.get('recording_time', 0) / overall_max_values['recording_time'] if overall_max_values['recording_time'] > 0 else 0,
            data.get('video_time', 0) / overall_max_values['video_time'] if overall_max_values['video_time'] > 0 else 0,
            data.get('recorder_start_count', 0) / overall_max_values['recorder_start_count'] if overall_max_values['recorder_start_count'] > 0 else 0,
            data.get('movie_completed_count', 0) / overall_max_values['movie_completed_count'] if overall_max_values['movie_completed_count'] > 0 else 0,
            data.get('continue_count', 0) / overall_max_values['continue_count'] if overall_max_values['continue_count'] > 0 else 0,
            data.get('result', 0) / overall_max_values['result'] if overall_max_values['result'] > 0 else 0,
        ]

        categories = [
            '動画開始回数', '音声開始回数', '回答回数', '正解数', 
            '不正解数', '一時停止回数', '起動回数', '回答にかかった時間', 
            '録画時間', '動画時間', '録画開始回数', '動画完了回数', 
            '継続回数', '結果'
        ]

        radar_chart = go.Figure(
            data=go.Scatterpolar(
                r=normalized_values,
                theta=categories,
                fill='toself',
                name=f'Attendance Number: {attendance_number}'
            )
        )

        radar_chart.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False
        )

        return radar_chart
