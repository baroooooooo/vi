import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
from in_it import parse_objectId
from datetime import datetime


def register_callbacks(app, calculated_results, all_extracted_data):
    global selected_attendance_numbers
    selected_attendance_numbers = []

    # 異常検知機能用
    def detect_outliers(data, threshold=3.0):
        mean = np.mean(data)
        std_dev = np.std(data)
        return [x if abs(x - mean) <= threshold * std_dev else 0 for x in data]

    @app.callback(
        Output('parameter-graph', 'figure'),
        Output('graph-data', 'data'),
        Input('year-dropdown', 'value'),
        Input('parameter-dropdown', 'value'),
        Input('extra-parameter-dropdown', 'value'),
        Input('order-number', 'n_clicks'),
        Input('order-asc', 'n_clicks'),
        Input('order-desc', 'n_clicks'),
        Input('toggle-outliers', 'n_clicks'),
    )
    def update_bar_graph(selected_year, selected_parameter, selected_extra_parameter, order_number, order_asc, order_desc, toggle_outliers):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}, None

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

        attendance_numbers = [x[0] for x in attendance_data]
        y_values_original = [x[1] for x in attendance_data]
        y_values_extra = [x[2] for x in attendance_data]

        if not attendance_numbers:  # データが存在しない場合
            return {'data': [], 'layout': {'title': 'No data available'}}, None
        
        # 外れ値の検出と切り替え
        use_outliers = toggle_outliers % 2 == 1 if toggle_outliers else False

        # メインパラメータの外れ値処理
        if use_outliers:
            processed_y_values_original = detect_outliers(y_values_original)
        else:
            processed_y_values_original = y_values_original

        # 最大値を取得し、正規化
        max_original_value = max(processed_y_values_original) if processed_y_values_original else 1
        normalized_y_values_original = [value / max_original_value for value in processed_y_values_original]

        # サブパラメータの外れ値処理
        if use_outliers:
            processed_y_values_extra = detect_outliers(y_values_extra)
        else:
            processed_y_values_extra = y_values_extra

        # 最大値を取得し、正規化
        max_extra_value = max(processed_y_values_extra) if processed_y_values_extra else 1
        normalized_y_values_extra = [value / max_extra_value for value in processed_y_values_extra]


        # メインパラメータの棒グラフトレース（外れ値は透過）
        original_data = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_original,  # 正規化された値を表示
            text=[f"ID: {num}, {selected_parameter}: {normalized_y_values_original[i]:.2f}" for i, num in enumerate(attendance_numbers)],
            textposition='outside',
            marker={
                'color': [
                    'rgba(255, 99, 71, 0.6)' if value in processed_y_values_original and value == 0 else 'rgba(255, 99, 71, 1)' 
                    for value in y_values_original
                ]
            },
            name=f'{selected_parameter} (Main)',
            width=0.4,
            hovertemplate=[
                f'Attendance Number: {attendance_numbers[i]}<br>{selected_parameter}: {normalized_y_values_original[i]:.2f}<br>Original Value: {y_values_original[i]}<extra></extra>' 
                for i in range(len(attendance_numbers))
            ]
        )


        # サブパラメータの棒グラフトレース（外れ値は透過）
        extra_data_trace = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_extra,  # 正規化された値を表示
            marker={
                'color': [
                    'rgba(100, 150, 255, 0.6)' if value in processed_y_values_extra and value == 0 else 'rgba(100, 150, 255, 1)' 
                    for value in y_values_extra
                ]
            },
            name=f'{selected_extra_parameter} (Extra)',
            width=0.4,
            hovertemplate=[
                f'Attendance Number: {attendance_numbers[i]}<br>{selected_extra_parameter}: {normalized_y_values_extra[i]:.2f}<br>Original Value: {y_values_extra[i]}<extra></extra>' 
                for i in range(len(attendance_numbers))
            ]
        )



        data = [original_data, extra_data_trace]

        layout = {
            'title': f'{selected_parameter} and {selected_extra_parameter} for {selected_year}',
            'xaxis': {'title': '出席番号', 'type': 'category'},
            'yaxis': {'title': 'Normalized Values'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)',
            'bargap': 0.1,
            'bargroupgap': 0.1,
            'autosize': True,
        }

        return {'data': data, 'layout': layout}, None

    

    @app.callback(
        Output('popup-graph', 'figure'),
        Input('x-parameter-dropdown', 'value'),  # X軸の入力
        Input('y-parameter-dropdown', 'value'),  # Y軸の入力
        Input('year-dropdown', 'value'),
        Input('toggle-outliers', 'n_clicks'),  # 外れ値を除外するトグルボタン
    )
    def update_scatter_plot(x_param, y_param, selected_year, toggle_outliers):
        if x_param and y_param and selected_year:
            year_data = calculated_results.get(selected_year, {})

            attendance_data_popup = [
                (attendance_number,
                year_data[attendance_number].get(x_param, 0),
                year_data[attendance_number].get(y_param, 0))
                for attendance_number in year_data
                if year_data[attendance_number].get(x_param) is not None and \
                year_data[attendance_number].get(y_param) is not None
            ]

            # データフレームを生成
            if attendance_data_popup:
                filtered_df = pd.DataFrame(attendance_data_popup, columns=['attendance_number', x_param, y_param])

                # 外れ値の検出と除外
                use_outliers = toggle_outliers % 2 == 1 if toggle_outliers else False
                if use_outliers:
                    # 外れ値を0に設定
                    filtered_df[x_param] = detect_outliers(filtered_df[x_param])
                    filtered_df[y_param] = detect_outliers(filtered_df[y_param])
                else:
                    filtered_df[x_param] = filtered_df[x_param]
                    filtered_df[y_param] = filtered_df[y_param]

                # グラフ生成
                parameter_fig = px.scatter(
                    filtered_df,
                    x=x_param,
                    y=y_param,
                    title=f"X軸 {x_param} Y軸 {y_param} の散布図",
                    text='attendance_number'  # IDを表示
                )

                # IDの位置を下に設定
                parameter_fig.update_traces(textposition='bottom center')

                print("Parameter graph displayed")
                return parameter_fig
            else:
                print("No valid attendance data found for parameter graph")
                return {}  # データが無い場合の処理
        else:
            print("Please select both parameters and a year")
            return {}



    @app.callback(
        Output('radar-chart', 'figure'),
        [
            Input('parameter-graph', 'clickData'),  # メイングラフ
            Input('year-dropdown', 'value'),
            Input('reset-radar-button', 'n_clicks')
        ]
    )
    def display_radar_chart(parameter_graph_clickData, selected_year, reset_n_clicks):
        global selected_attendance_numbers
        print(f"Main graph click data: {parameter_graph_clickData}")
        print(f"Selected year: {selected_year}")
        print(f"Selected attendance numbers: {selected_attendance_numbers}")

        # リセットボタンが押された場合
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-radar-button':
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択された出席番号をリセット
            return generate_radar_chart([], selected_year)  # 空のレーダーチャートを返す

        attendance_number = None
        # メイングラフのクリックデータを取得
        if parameter_graph_clickData and 'points' in parameter_graph_clickData:
            attendance_number = parameter_graph_clickData['points'][0]['label']
            print(f"Selected attendance number from main graph: {attendance_number}")

        # どちらもクリックされていない場合、更新しない
        if not attendance_number:
            return dash.no_update

        # 出席番号が取得できた場合、リストに追加
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)

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
                r=normalized_values + [normalized_values[0]],  # 閉じた図形にするために最初の値を追加
                theta=[
                    'video_start_count', 'audio_start_count', 'answer_count', 'correct_answers',
                    'incorrect_answers', 'suspended_count', 'launched_count', 'total_answer_time',
                    'recording_time', 'video_time', 'recorder_start_count', 'movie_completed_count',
                    'continue_count', 'test_result', 'video_start_count'
                ],
                name=f'Attendance {attendance_number}',
                fill='toself'
            ))

        return {
            'data': radar_traces,
            'layout': go.Layout(
                title='レーダーチャート',
                polar={
                    'radialaxis': {
                        'visible': True,
                        'range': [0, 1],  # レーダーチャートの範囲を0~1に設定
                    }
                },
                showlegend=True
            )
        }
    
    @app.callback(
        Output('3d-graph', 'figure'),  # 3DグラフのID
        [Input('parameter-graph', 'clickData'),  # メイングラフのクリックイベント
        Input('reset-button', 'n_clicks'),  # リセットボタンのクリックイベント
        Input('year-dropdown', 'value'),  # 年選択
        Input('month-dropdown', 'value'),  # 月選択
        Input('day-dropdown', 'value'),  # 日選択
        Input('unit-type-selector', 'value')]  # ユニットタイプの選択 (Basic Unit, Main Unit)
    )
    def display_2d_or_3d_graph(click_data, reset_n_clicks, selected_year, selected_month, selected_day, unit_type):
        global selected_attendance_numbers

        # リセットボタンが押された場合の処理
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-button':
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択された出席番号をリセット
            return dash.no_update  # グラフの更新を行わない

        attendance_number = None
        # メイングラフのクリックデータを取得
        if click_data and 'points' in click_data:
            attendance_number = click_data['points'][0]['label']
            print(f"Selected attendance number from main graph: {attendance_number}")

        # どちらもクリックされていない場合、更新しない
        if not attendance_number:
            return dash.no_update

        # 出席番号が取得できた場合、リストに追加（重複しないように）
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)

        # デバッグ: フィルタリング条件の確認
        print(f"Selected year: {selected_year}")
        print(f"Selected month: {selected_month}")
        print(f"Selected day: {selected_day}")
        print(f"Unit type: {unit_type}")
        print(f"Selected attendance numbers: {selected_attendance_numbers}")

        # 月、日、ユニットタイプに基づいてデータをフィルタリング
        filtered_data = [data for data in all_extracted_data
                        if data['ID'] in selected_attendance_numbers
                        and data['Year'] == selected_year
                        and (not selected_month or data['timeStamp'].month == selected_month)
                        and (not selected_day or data['timeStamp'].day == selected_day)
                        and data['UnitType'] == unit_type]  # Basic Unit または Main Unit

        # デバッグ: フィルタリング後のデータ確認
        print(f"Filtered data: {filtered_data}")

        if not filtered_data:
            print("No data available for the selected filters.")
            return dash.no_update

        # 1人だけ選択されている場合は2Dグラフを表示
        if len(selected_attendance_numbers) == 1:
            return generate_2d_graph(selected_attendance_numbers[0], selected_year, selected_month, selected_day, unit_type)

        # 2人以上選択されている場合は3Dグラフを表示
        return generate_3d_graph(selected_attendance_numbers, selected_year, selected_month, selected_day, unit_type)

    def generate_2d_graph(attendance_number, selected_year, selected_month, selected_day, unit_type):
        # 選択された出席番号のデータを使用して2Dグラフを作成
        filtered_data = [data for data in all_extracted_data
                        if data['ID'] == attendance_number
                        and data['Year'] == selected_year
                        and (not selected_month or data['timeStamp'].month == selected_month)
                        and (not selected_day or data['timeStamp'].day == selected_day)
                        and data['UnitType'] == unit_type]

        if not filtered_data:
            print(f"No data available for 2D graph for Attendance {attendance_number}")
            return dash.no_update

        fig = go.Figure()
        x_vals = [data['timeStamp'] for data in filtered_data]
        y_vals = [int(data['UnitNumber']) for data in filtered_data]

        # 2Dラインチャートを作成
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name=f'Attendance {attendance_number}'))

        # グラフのレイアウトを設定
        fig.update_layout(
            title=f'2D Line Plot for Attendance {attendance_number}',
            xaxis_title='Time',
            yaxis_title='Unit Number'
        )

        return fig

    def generate_3d_graph(attendance_numbers, selected_year, selected_month, selected_day, unit_type):
        # 選択された出席番号のデータを使用して3Dグラフを作成
        filtered_data = [data for data in all_extracted_data
                        if data['ID'] in attendance_numbers
                        and data['Year'] == selected_year
                        and (not selected_month or data['timeStamp'].month == selected_month)
                        and (not selected_day or data['timeStamp'].day == selected_day)
                        and data['UnitType'] == unit_type]

        if not filtered_data:
            print("No data available for 3D graph.")
            return dash.no_update

        fig = go.Figure()

        for attendance_number in attendance_numbers:
            filtered_attendance_data = [data for data in filtered_data if data['ID'] == attendance_number]

            x_vals = [data['ID'] for data in filtered_attendance_data]
            y_vals = [int(data['UnitNumber']) for data in filtered_attendance_data]
            z_vals = [data['timeStamp'].timestamp() for data in filtered_attendance_data]

            # 3Dラインチャートを作成
            fig.add_trace(go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='lines',
                line=dict(width=2),
                name=f'Attendance {attendance_number}'
            ))

        # グラフのレイアウトを設定
        fig.update_layout(
            scene=dict(
                xaxis_title='ID',
                yaxis_title='Unit Number',
                zaxis_title='Time',
            ),
            title='3D Line Plot for Selected Attendances',
            margin=dict(l=0, r=0, b=0, t=0)
        )

        return fig




