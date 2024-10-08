import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    global selected_attendance_numbers
    selected_attendance_numbers = []

    @app.callback(
        Output('parameter-graph', 'figure'),
        Output('graph-data', 'data'),
        Input('year-dropdown', 'value'),
        Input('parameter-dropdown', 'value'),
        Input('extra-parameter-dropdown', 'value'),
        Input('order-number', 'n_clicks'),
        Input('order-asc', 'n_clicks'),
        Input('order-desc', 'n_clicks'),
        [State('graph-data', 'data')]
    )
    def update_graph(selected_year, selected_parameter, selected_extra_parameter, order_number, order_asc, order_desc, existing_graphs):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}, existing_graphs

        year_data = calculated_results.get(selected_year, {})
        
        # 出席番号ごとにメインとサブのパラメータを取得
        attendance_data = [
            (attendance_number, year_data[attendance_number].get(selected_parameter, 0),
            year_data[attendance_number].get(selected_extra_parameter, 0))
            for attendance_number in year_data
            if selected_parameter in year_data[attendance_number] and year_data[attendance_number].get(selected_extra_parameter) is not None
        ]

        # ソート条件に基づいて出席番号ごとに並び替え
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            attendance_data.sort(key=lambda x: x[1])  # メインパラメータで昇順ソート
        elif triggered_id == 'order-desc':
            attendance_data.sort(key=lambda x: x[1], reverse=True)  # メインパラメータで降順ソート
        elif triggered_id == 'order-number':
            attendance_data.sort(key=lambda x: int(x[0]))  # 出席番号でソート

        # ソート済みの出席番号と値をリストに格納
        attendance_numbers = [x[0] for x in attendance_data]
        y_values_original = [x[1] for x in attendance_data]
        y_values_extra = [x[2] for x in attendance_data]

        if not attendance_numbers:  # データが存在しない場合
            return {'data': [], 'layout': {'title': 'No data available'}}, existing_graphs

        # メインパラメータの最大値を取得して正規化
        max_original_value = max(y_values_original) if y_values_original else 1  # 最大値が0の場合を避けるためデフォルト値を設定
        normalized_y_values_original = [value / max_original_value for value in y_values_original]  # 正規化

        # サブパラメータの最大値を取得して正規化
        max_extra_value = max(y_values_extra) if y_values_extra else 1  # 最大値が0の場合を避けるためデフォルト値を設定
        normalized_y_values_extra = [value / max_extra_value for value in y_values_extra]  # 正規化

        # メインパラメータの棒グラフトレース
        original_data = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_original,
            text=[f"ID: {num}, {selected_extra_parameter}: {y_values_extra[i]}" for i, num in enumerate(attendance_numbers)],
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter} (Main)',
            width=0.4  # 幅を狭めてバー同士が重ならないように
        )

        # サブパラメータの棒グラフトレース
        extra_data_trace = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_extra,  # 正規化したサブパラメータの値を使用
            marker={'color': 'rgba(100, 150, 255, 0.6)'},
            name=f'{selected_extra_parameter} (Extra)',
            width=0.4  # 幅を狭めてバー同士が重ならないように
        )

        data = [original_data, extra_data_trace]

        layout = {
            'title': f'{selected_parameter} and {selected_extra_parameter} for {selected_year}',
            'xaxis': {
                'title': '出席番号',
                'type': 'category',  # 存在する出席番号のみをカテゴリとして表示
            },
            'yaxis': {'title': 'Normalized Values'},  # 正規化した値に応じたY軸のタイトル
            'barmode': 'group',  # 同じグラフで並べて表示
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)',
            'bargap': 0.1,  # バー間の隙間を調整
            'bargroupgap': 0.1,  # グループ間の隙間を調整
            'autosize': True  # レイアウトのサイズを自動調整
        }
        
        return {'data': data, 'layout': layout}, existing_graphs







    @app.callback(
        Output('radar-chart', 'figure'),
        [Input('parameter-graph', 'clickData'),
         Input('year-dropdown', 'value'),
         Input('reset-radar-button', 'n_clicks')]
    )
    def display_radar_chart(parameter_graph_clickData, selected_year, reset_n_clicks):
        global selected_attendance_numbers
        print(f"Click data: {parameter_graph_clickData}")

        # リセットボタンが押された場合
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-radar-button':
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択された出席番号をリセット
            return generate_radar_chart([], selected_year)  # 空のレーダーチャートを返す

        # クリックデータが存在するか確認
        if parameter_graph_clickData is not None and 'points' in parameter_graph_clickData:
            # 出席番号のみを取得
            attendance_number = parameter_graph_clickData['points'][0].get('text', '').split(',')[0].replace('ID: ', '')
            print(f"Selected attendance number: {attendance_number}")

            # 新しい出席番号を選択リストに追加
            if attendance_number and attendance_number not in selected_attendance_numbers:
                selected_attendance_numbers.append(attendance_number)
                print(f"Attendance number {attendance_number} added to selection")


        # 選択された出席番号に基づいてレーダーチャートを生成
        return generate_radar_chart(selected_attendance_numbers, selected_year)


    def generate_radar_chart(selected_attendance_numbers, selected_year):
        print(f"Generating radar chart for: {selected_attendance_numbers} in year {selected_year}")
        if not selected_attendance_numbers:
            return {'data': [], 'layout': go.Layout(title='レーダーチャート')}

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
                data.get('suspended_count', 0) / overall_max_values['suspended_count'] if overall_max_values['suspended_count'] > 0 else 0,                    data.get('launched_count', 0) / overall_max_values['launched_count'] if overall_max_values['launched_count'] > 0 else 0,
                data.get('total_answer_time', 0) / overall_max_values['total_answer_time'] if overall_max_values['total_answer_time'] > 0 else 0,
                data.get('recording_time', 0) / overall_max_values['recording_time'] if overall_max_values['recording_time'] > 0 else 0,
                data.get('video_time', 0) / overall_max_values['video_time'] if overall_max_values['video_time'] > 0 else 0,
                data.get('recorder_start_count', 0) / overall_max_values['recorder_start_count'] if overall_max_values['recorder_start_count'] > 0 else 0,
                data.get('movie_completed_count', 0) / overall_max_values['movie_completed_count'] if overall_max_values['movie_completed_count'] > 0 else 0,                    data.get('continue_count', 0) / overall_max_values['continue_count'] if overall_max_values['continue_count'] > 0 else 0,
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

        
