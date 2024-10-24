import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
from in_it import parse_objectId, is_within_academic_year, save_random_data_to_csv
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

        save_random_data_to_csv(calculated_results, num_students=5, file_name="random_students_data.csv")
        
        attendance_data = [
            (attendance_number, year_data[attendance_number].get(selected_parameter, 0),
            year_data[attendance_number].get(selected_extra_parameter, 0))
            for attendance_number in year_data
            if selected_parameter in year_data[attendance_number] and year_data[attendance_number].get(selected_extra_parameter) is not None
        ]

        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            attendance_data.sort(key=lambda x: x[1])
        elif triggered_id == 'order-desc':
            attendance_data.sort(key=lambda x: x[1], reverse=True)
        elif triggered_id == 'order-number':
            attendance_data.sort(key=lambda x: int(x[0]))

        attendance_numbers = [x[0] for x in attendance_data]
        y_values_original = [x[1] for x in attendance_data]
        y_values_extra = [x[2] for x in attendance_data]

        if not attendance_numbers:
            return {'data': [], 'layout': {'title': 'No data available'}}, None

        use_outliers = toggle_outliers % 2 == 1 if toggle_outliers else False

        if use_outliers:
            processed_y_values_original = detect_outliers(y_values_original)
        else:
            processed_y_values_original = y_values_original

        max_original_value = max(processed_y_values_original) if processed_y_values_original else 1
        normalized_y_values_original = [value / max_original_value for value in processed_y_values_original]

        if use_outliers:
            processed_y_values_extra = detect_outliers(y_values_extra)
        else:
            processed_y_values_extra = y_values_extra

        max_extra_value = max(processed_y_values_extra) if processed_y_values_extra else 1
        normalized_y_values_extra = [value / max_extra_value for value in processed_y_values_extra]

        parameter_labels = {
            'video_start_count': '動画再生回数',
            'audio_start_count': '音声再生回数',
            'answer_count': '回答回数',
            'total_answer_time': '回答時間',
            'correct_answers': '正解数',
            'incorrect_answers': '不正解数',
            'suspended_count': '中断回数',
            'launched_count': 'アプリ起動回数',
            'recording_time': '録音時間',
            'video_time': '動画再生時間',
            'recorder_start_count': '録音回数',
            'movie_completed_count': '動画再生完了回数',
            'continue_count': '復習回数',
            'test_result': '成績'
        }
        # 日本語ラベルを使用してタイトルと凡例を設定
        selected_param_label = parameter_labels.get(selected_parameter, selected_parameter)
        extra_param_label = parameter_labels.get(selected_extra_parameter, selected_extra_parameter)


        original_data = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_original,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 1)'},
            name=f'{selected_param_label} (メイン)',
            width=0.4,
            hovertemplate=[f'Attendance Number: {attendance_numbers[i]}<br>{selected_parameter}: {normalized_y_values_original[i]:.2f}<br>Original Value: {y_values_original[i]}<extra></extra>' for i in range(len(attendance_numbers))]
        )

        extra_data_trace = go.Bar(
            x=attendance_numbers,
            y=normalized_y_values_extra,
            marker={'color': 'rgba(100, 150, 255, 1)'},
            name=f'{extra_param_label} (サブ)',  # サブパラメータも日本語化
            width=0.4,
            hovertemplate=[f'Attendance Number: {attendance_numbers[i]}<br>{selected_extra_parameter}: {normalized_y_values_extra[i]:.2f}<br>Original Value: {y_values_extra[i]}<extra></extra>' for i in range(len(attendance_numbers))]
        )

        data = [original_data, extra_data_trace]

        layout = {
            'title': f'{selected_param_label} と {extra_param_label}  ({selected_year})',
            'xaxis': {'title': '出席番号', 'type': 'category'},
            'yaxis': {'title': 'Normalized Values'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)',
            'bargap': 0.1,
            'bargroupgap': 0.1,
            'autosize': True,
            'height': 400  # グラフの高さを小さく調整
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

            # 出席番号とパラメータのリストを作成
            attendance_data_popup = [
                (attendance_number,
                year_data[attendance_number].get(x_param, 0), 
                year_data[attendance_number].get(y_param, 0))
                for attendance_number in year_data
                if year_data[attendance_number].get(x_param) is not None and year_data[attendance_number].get(y_param) is not None
            ]

            if attendance_data_popup:
                # 1次元データとして列ごとに分ける
                attendance_numbers, x_values, y_values = zip(*attendance_data_popup)
                
                # DataFrameに変換
                filtered_df = pd.DataFrame({
                    'attendance_number': attendance_numbers,
                    x_param: x_values,
                    y_param: y_values
                })

                # 外れ値の処理
                use_outliers = toggle_outliers % 2 == 1 if toggle_outliers else False
                if use_outliers:
                    filtered_df[x_param] = detect_outliers(filtered_df[x_param])
                    filtered_df[y_param] = detect_outliers(filtered_df[y_param])

                # 散布図の作成
                # パラメータ名の日本語ラベルを定義
                parameter_labels = {
                    'video_start_count': '動画再生回数',
                    'audio_start_count': '音声再生回数',
                    'answer_count': '回答回数',
                    'total_answer_time': '回答時間',
                    'correct_answers': '正解数',
                    'incorrect_answers': '不正解数',
                    'suspended_count': '中断回数',
                    'launched_count': 'アプリ起動回数',
                    'recording_time': '録音時間',
                    'video_time': '動画再生時間',
                    'recorder_start_count': '録音回数',
                    'movie_completed_count': '動画再生完了回数',
                    'continue_count': '復習回数',
                    'test_result': '成績'
                }

                # 日本語ラベルを使用して散布図を作成
                x_label = parameter_labels.get(x_param, x_param)  # x_param に対応する日本語ラベルを取得
                y_label = parameter_labels.get(y_param, y_param)  # y_param に対応する日本語ラベルを取得

                parameter_fig = px.scatter(
                    filtered_df,
                    x=x_param,
                    y=y_param,
                    title=f"X軸 {x_label} Y軸 {y_label} の散布図",  # タイトルも日本語化
                    text='attendance_number'
                )

                # 軸のラベルを設定
                parameter_fig.update_layout(
                    xaxis_title=x_label,  # X軸のラベル
                    yaxis_title=y_label   # Y軸のラベル
                )

                # ID番号のフォントサイズを小さく設定
                parameter_fig.update_traces(textposition='bottom center', textfont_size=10)

                return parameter_fig
            else:
                return {}  # データが無い場合の処理
        else:
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
                    '動画再生回数', '音声再生回数', '回答回数', '正解数',
                    '不正解数', '中断回数', 'アプリ起動回数', '回答時間',
                    '録音時間', '動画再生時間', '録音回数', '動画再生完了回数',
                    '復習回数', '成績', '動画再生回数'  # 最初と同じラベルで閉じる
                ],
                name=f'ID{attendance_number}の個人データ',
                fill='toself'
            ))

        return {
            'data': radar_traces,
            'layout': go.Layout(
                title='レーダーチャート',
                polar={
                    'radialaxis': {'visible': True, 'range': [0, 1]},
                },
                showlegend=True,
                legend={'x': 0.9, 'y': 1, 'xanchor': 'right'},  # レジェンドを右上に移動
                autosize=True,  # レイアウトサイズを自動調整
                margin={'l': 50, 'r': 50, 'b': 50, 't': 50},  # 左右の余白を均等に
                height=500
            )
            }
    
    @app.callback(
        Output('3d-graph', 'figure'),
        [Input('parameter-graph', 'clickData'),
        Input('reset-button', 'n_clicks'),
        Input('year-dropdown', 'value'),
        Input('unit-type-selector', 'value')],
        [State('selected-attendance-numbers', 'data')]
    )
    def display_2d_or_3d_graph(click_data, reset_n_clicks, selected_year, unit_type, stored_numbers):
        global selected_attendance_numbers

        # リセットボタンが押された場合の処理
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-button':
            print("Reset button clicked, clearing selected attendance numbers")
            selected_attendance_numbers = []
            return go.Figure()  # 空のグラフを返す

        # クリックデータがある場合、出席番号を取得
        if click_data and 'points' in click_data:
            attendance_number = str(click_data['points'][0]['label'])  # 明示的にstrに変換
            print(f"Selected attendance number from main graph: {attendance_number}")
        else:
            return dash.no_update

        # 出席番号をリストに追加（重複しないように）
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)

        print(f"Filtering data for Year: {selected_year}, UnitType: {unit_type}, Attendance Numbers: {selected_attendance_numbers}")

        # 選択された出席番号に基づいてグラフを生成
        return generate_graph_with_review(selected_attendance_numbers, selected_year, unit_type)


    def filter_data(attendance_numbers, selected_year, unit_type=None):
        # 年度と出席番号に基づいてフィルタリング
        filtered_data = [data for data in all_extracted_data
                        if str(data['ID']) in attendance_numbers
                        and is_within_academic_year(data['timeStamp'], selected_year)]  # 学年度でフィルタ

        print(f"Data after year and ID filtering: {len(filtered_data)}")

        # ユニットタイプが指定されている場合のみフィルタリング
        if unit_type:
            print(f"Filtering by UnitType: {unit_type}")
            filtered_data = [data for data in filtered_data if data['UnitType'] == unit_type]

        print(f"Data after UnitType filtering: {len(filtered_data)}")

        # 時系列順にソート（timeStampフィールドを基準に昇順に並べる）
        filtered_data.sort(key=lambda x: x['timeStamp'])

        # direction フィールドを計算して追加
        directions = calculate_direction(filtered_data)

        for i in range(len(filtered_data)):
            filtered_data[i]['direction'] = directions[i]

        return filtered_data


    def calculate_direction(filtered_data):
        directions = []
        previous_unit_number = None

        for data in filtered_data:
            current_unit_number = int(data.get('UnitNumber', 0))  # UnitNumber を整数で処理
            if previous_unit_number is None:
                directions.append('Forward')  # 最初のエントリは Forward
            else:
                if current_unit_number >= previous_unit_number:
                    directions.append('Forward')
                else:
                    directions.append('Review')
            previous_unit_number = current_unit_number

        return directions


    def generate_graph_with_review(attendance_numbers, selected_year, unit_type=None):
        if not attendance_numbers:
            print("No attendance numbers selected, returning empty figure.")
            return go.Figure()  # 空のグラフを返す

        filtered_data = filter_data(attendance_numbers, selected_year, unit_type)
        if not filtered_data:
            print(f"No data available for Attendance {attendance_numbers}")
            return go.Figure()  # データがない場合も空のグラフを返す

        fig = go.Figure()

        for attendance_number in attendance_numbers:
            filtered_attendance_data = [data for data in filtered_data if str(data['ID']) == attendance_number]
            if not filtered_attendance_data:
                continue

            filtered_attendance_data.sort(key=lambda x: x['timeStamp'])
            
            x_vals = [data['timeStamp'] for data in filtered_attendance_data]
            y_vals = [int(data.get('UnitNumber', '0')) for data in filtered_attendance_data]
            directions = [data.get('direction', 'Forward') for data in filtered_attendance_data]

            # 全データを1つのセグメントとして扱い、進行方向によって線のスタイルを切り替える
            for i in range(1, len(x_vals)):
                if directions[i] == 'Forward':
                    fig.add_trace(go.Scatter(
                        x=x_vals[i-1:i+1],
                        y=y_vals[i-1:i+1],
                        mode='lines+markers',
                        name='時系列データ',
                        line=dict(color='blue', width=2),
                        marker=dict(symbol='triangle-up', size=8),
                        showlegend=attendance_number == attendance_numbers[0] and i == 1  # 最初の進行のみ凡例表示
                    ))
                else:  # Review
                    fig.add_trace(go.Scatter(
                        x=x_vals[i-1:i+1],
                        y=y_vals[i-1:i+1],
                        mode='lines+markers',
                        name=f'Attendance {attendance_number} - Review',
                        line=dict(color='red', width=2, dash='dash'),
                        marker=dict(symbol='triangle-down', size=8),
                        showlegend=attendance_number == attendance_numbers[0] and i == 1  # 最初のレビューのみ凡例表示
                    ))

        fig.update_layout(
            title=f'ID {attendance_numbers} の時系列データ',
            xaxis_title='Time',
            yaxis_title='Unit Number',
            xaxis=dict(tickformat='%b %Y'),
            yaxis=dict(dtick=1),
            legend=dict(x=1, y=0.5, traceorder='normal', title=''),
            height=400  # 3Dグラフの高さを調整
        )

        return fig







    def configure_graph_layout(fig, title, xaxis_title, yaxis_title, zaxis_title=None):
        print(f"Configuring layout with title: {title}")
        layout = {
            'title': title,
            'xaxis': {'title': xaxis_title, 'range': ['2018-01-01', '2018-12-31']},  # 日付範囲を指定
            'yaxis': {'title': yaxis_title, 'range': [1, 10]}  # y軸の範囲を指定
        }

        if zaxis_title:
            layout['scene'] = {
                'xaxis': {'title': xaxis_title},
                'yaxis': {'title': yaxis_title},
                'zaxis': {'title': zaxis_title}
            }

        fig.update_layout(layout)
        print(f"Layout configured: {fig.layout}")







