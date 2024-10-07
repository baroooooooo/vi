import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    # グローバル変数を初期化
    global selected_attendance_numbers
    selected_attendance_numbers = []

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

        return {'data': [original_data], 'layout': layout}, existing_graphs
    



    @app.callback(
        Output('graphs-container', 'children'),
        Input('add-graph-button', 'n_clicks'),
        Input('remove-graph-button', 'n_clicks'),
        State('graphs-container', 'children'),
        State('year-dropdown', 'value'),
        State('parameter-dropdown', 'value')
    )
    def update_graph_container(add_graph_n_clicks, remove_graph_n_clicks, existing_graphs, selected_year, selected_parameter):
        if existing_graphs is None:
            existing_graphs = []
            
        # ボタンがクリックされていない場合
        if not add_graph_n_clicks and not remove_graph_n_clicks:
            return existing_graphs

        # グラフ追加ボタンがクリックされた場合
        if add_graph_n_clicks > 0:
            year_data = calculated_results.get(selected_year, {})
            attendance_numbers = [
                attendance_number for attendance_number in year_data.keys()
                if selected_parameter in year_data[attendance_number]
            ]

            y_values = [year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers]
            
            new_graph = html.Div(
                [
                    dcc.Graph(
                        id={'type': 'dynamic-graph', 'index': len(existing_graphs)+1},
                        figure={
                            'data': [go.Bar(
                                x=list(range(len(attendance_numbers))),
                                y=y_values,
                                text=attendance_numbers,
                                textposition='outside',
                                marker={'color': 'rgba(0, 128, 255, 0.6)'},
                                name=f'{selected_parameter} (Year {selected_year})'
                            )],
                            'layout': go.Layout(
                                title=f'{selected_parameter} for Year {selected_year}',
                                xaxis={'title': '出席番号', 'tickvals': list(range(len(attendance_numbers))), 'ticktext': attendance_numbers},
                                yaxis={'title': f'{selected_parameter} 値'},
                                plot_bgcolor='rgba(240, 240, 240, 0.95)'
                            )
                        }
                    ),
                ]
            )
            existing_graphs.append(new_graph)

        # グラフ削除ボタンがクリックされた場合
        if remove_graph_n_clicks > 0 and existing_graphs:
            existing_graphs.pop()  # 一番新しい（最後の）グラフを削除

        return existing_graphs

    # 特定のグラフを削除するためのコールバック
    @app.callback(
        Output('graphs-container', 'children', allow_duplicate=True),
        Input({'type': 'remove-specific-graph', 'index': ALL}, 'n_clicks'),
        Input('parameter-graph', 'clickData'),  # ここを追加
        Input('dynamic-graph', 'clickData'),    # ここを追加
        State('graphs-container', 'children'),
        prevent_initial_call=True
    )
    def remove_specific_graph(remove_graph_n_clicks, parameter_graph_clickData, dynamic_graph_clickData, existing_graphs):
        print("Remove clicks:", remove_graph_n_clicks)
        print("Parameter graph click data:", parameter_graph_clickData)
        print("Dynamic graph click data:", dynamic_graph_clickData)
        print("Existing graphs before removal:", existing_graphs)

        # クリックデータがNoneの場合は何もしない
        if parameter_graph_clickData is None and dynamic_graph_clickData is None:
            return existing_graphs

        # ここでのグラフ削除のロジック
        if remove_graph_n_clicks:
            for index, n_clicks in enumerate(remove_graph_n_clicks):
                if n_clicks and n_clicks > 0 and existing_graphs:
                    print(f"Removing graph at index {index}")
                    existing_graphs.pop(index)
                    break  # 1つのグラフだけ削除する
        
        print("Existing graphs after removal:", existing_graphs)
        return existing_graphs


    # コールバックを追加
    @app.callback(
        Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
        Input({'type': 'dynamic-parameter-dropdown', 'index': MATCH}, 'value'),
        Input('year-dropdown', 'value')
    )
    def update_dynamic_graph(selected_parameter, selected_year):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}
        
        year_data = calculated_results.get(selected_year, {})
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if selected_parameter in year_data[attendance_number]
        ]

        # データの作成
        y_values = [year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers]
        data = go.Bar(
            x=list(range(len(attendance_numbers))),
            y=y_values,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter}'
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

        return {'data': [data], 'layout': layout}



    @app.callback(
        Output('radar-chart', 'figure'),
        [Input('parameter-graph', 'clickData'),
        Input({'type': 'dynamic-graph', 'index': ALL}, 'clickData'),
        Input('year-dropdown', 'value'),
        Input('reset-radar-button', 'n_clicks')],
        [State('radar-chart', 'figure')]
    )
    def display_radar_chart(parameter_graph_clickData, dynamic_graph_clickData, selected_year, reset_n_clicks, current_figure):
        global selected_attendance_numbers

        # リセットボタンが押された場合
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-radar-button':
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択された出席番号をリセット
            return generate_radar_chart([], selected_year)  # 空のレーダーチャートを返す

        print(f"parameter_graph_clickData: {parameter_graph_clickData}")
        print(f"dynamic_graph_clickData: {dynamic_graph_clickData}")
         # dynamic-graph も含めたクリックデータから attendance_number を取得
        clickData = parameter_graph_clickData or next((data for data in reversed(dynamic_graph_clickData) if data), None)
        print(f"clickData: {clickData}")
        # クリックデータが存在しない、または年が選択されていない場合
        if clickData is None or selected_year is None:
            print("clickData or selected_year is None")
            # 何も選択されていない場合、最初のレーダーチャートを生成する
            if not selected_attendance_numbers:  # 最初の状態で何も選択されていない場合
                return generate_radar_chart([], selected_year)
            return current_figure

        attendance_number = clickData['points'][0]['text']
        print(f"Selected attendance number: {attendance_number}")

        # 新しい出席番号を選択リストに追加
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)
            print(f"Attendance number {attendance_number} added to selection")

        # 選択された出席番号に基づいてレーダーチャートを生成
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
                r=normalized_values + [normalized_values[0]],  # 最後の点を最初の点に戻す
                theta=[
                    'video_start_count',
                    'audio_start_count',
                    'answer_count',
                    'correct_answers',
                    'incorrect_answers',
                    'suspended_count',
                    'launched_count',
                    'total_answer_time',
                    'recording_time',
                    'video_time',
                    'recorder_start_count',
                    'movie_completed_count',
                    'continue_count',
                    'test_result'
                ] + ['video_start_count'],  # 閉じるために最初の項目を追加
                fill='toself',
                name=attendance_number,
            ))

        return {
            'data': radar_traces,
            'layout': go.Layout(
                title='選択された出席番号のレーダーチャート',
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True
            )
        }