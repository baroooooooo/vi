import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    global selected_attendance_numbers
    global first_selected_attendance_number
    selected_attendance_numbers = []
    first_selected_attendance_number = None

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
        Input('reset-radar-button', 'n_clicks'),
        [State('graph-data', 'data')]
    )
    def update_graph(selected_year, selected_parameter, order_number, order_asc, order_desc, add_graph_n_clicks, remove_graph_n_clicks, reset_radar_n_clicks, existing_graphs):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}, existing_graphs
        
        year_data = calculated_results.get(selected_year, {})
        
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if selected_parameter in year_data[attendance_number]
        ]

        # 出席番号のソート
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter])
        elif triggered_id == 'order-desc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter], reverse=True)
        elif triggered_id == 'order-number':
            attendance_numbers.sort(key=int)

        y_values_original = [year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers]
        
        original_data = go.Bar(
            x=list(range(len(attendance_numbers))),
            y=y_values_original,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter} (Original)'
        )

        layout = {
            'title': f'{selected_parameter} for {selected_year}',
            'xaxis': {
                'title': '出席番号',
                'tickmode': 'array',
                'tickvals': list(range(len(attendance_numbers))),
                'ticktext': attendance_numbers,
            },
            'yaxis': {'title': f'{selected_parameter} 値'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'
        }

        if existing_graphs is None or isinstance(existing_graphs, dict):
            existing_graphs = []

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
        [Input('parameter-graph', 'clickData'),
        Input('year-dropdown', 'value'),
        Input('reset-radar-button', 'n_clicks')]
    )
    def display_radar_chart(clickData, selected_year, reset_n_clicks):
        global selected_attendance_numbers

        reset_n_clicks = reset_n_clicks or 0

        # リセットボタンが押されたら全ての選択をリセット
        if reset_n_clicks > 0:
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択リストを空にする
            return generate_radar_chart([], selected_year)  # 空のレーダーチャートを返す

        # clickDataがないか年が選択されていない場合の処理
        if clickData is None or selected_year is None:
            print("clickData or selected_year is None")
            return generate_radar_chart(selected_attendance_numbers, selected_year)  # 選択がない場合は既存の選択を使用

        # クリックされた出席番号を抽出
        attendance_number = clickData['points'][0]['text']
        print(f"Selected attendance number: {attendance_number}")

        # 選択された出席番号をリストに追加
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)
            print(f"Attendance number {attendance_number} added to selection")

        # レーダーチャートを生成
        return generate_radar_chart(selected_attendance_numbers, selected_year)


    def generate_radar_chart(selected_attendance_numbers, selected_year):
        print(f"Generating radar chart with attendance numbers: {selected_attendance_numbers} and year: {selected_year}")
        
        # リセット後の処理: selected_attendance_numbersが空ならば空のグラフを返す
        if not selected_attendance_numbers:
            return {
                'data': [],
                'layout': go.Layout(
                    title='レーダーチャート',
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=True
                )
            }

        radar_traces = []

        for attendance_number in selected_attendance_numbers:
            data = calculated_results.get(selected_year, {}).get(attendance_number, {})
            if not data:
                continue

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
                'test_result': max(data.get('test_result', 0) for data in calculated_results[selected_year].values()),
            }

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
                data.get('test_result', 0) / overall_max_values['test_result'] if overall_max_values['test_result'] > 0 else 0,
            ]

            radar_traces.append(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],  # クローズドなポリゴンを作るために最初の値を再度追加
                theta=[
                    'Video Start Count',
                    'Audio Start Count',
                    'Answer Count',
                    'Correct Answers',
                    'Incorrect Answers',
                    'Suspended Count',
                    'Launched Count',
                    'Total Answer Time',
                    'Recording Time',
                    'Video Time',
                    'Recorder Start Count',
                    'Movie Completed Count',
                    'Continue Count',
                    'Test Result',
                ] + ['Video Start Count'],  # クローズドなポリゴンを作るために最初の値を再度追加
                fill='toself',
                name=attendance_number
            ))

        layout = go.Layout(
            title='出席番号ごとのレーダーチャート',
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True
        )

        return {'data': radar_traces, 'layout': layout}

