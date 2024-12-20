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
import calendar


def register_callbacks(app, calculated_results, all_extracted_data):
    global selected_attendance_numbers
    selected_attendance_numbers = []

    for data in all_extracted_data:
        if isinstance(data['timeStamp'], str):  # 文字列の場合のみ変換
            data['timeStamp'] = datetime.strptime(data['timeStamp'], '%Y-%m-%d')
    df = pd.DataFrame(all_extracted_data)
    # 異常検知機能用
    def detect_outliers(data, threshold=3.0):
        mean = np.mean(data)
        std_dev = np.std(data)
        return [x if abs(x - mean) <= threshold * std_dev else 0 for x in data]

    BASE_PATH = r"C:\\Users\\Syachi\\vi\\datas"

    @app.callback(
        Output('parameter-graph', 'figure'),
        Output('graph-data', 'data'),
        Input('folder-dropdown', 'value'),  # フォルダ選択ドロップダウン
        Input('year-dropdown', 'value'),
        Input('class-dropdown', 'value'),
        Input('parameter-dropdown', 'value'),
        Input('extra-parameter-dropdown', 'value'),
        Input('order-number', 'n_clicks'),
        Input('order-asc', 'n_clicks'),
        Input('order-desc', 'n_clicks'),
        Input('toggle-outliers', 'n_clicks'),
        Input('normalize-toggle', 'value')
    )
    def update_bar_graph(
        selected_year, selected_classes, selected_parameter, selected_extra_parameter,
        order_number, order_asc, order_desc, toggle_outliers, normalize_toggle, selected_category
    ):
        # データがない場合の早期リターン
        if not calculated_results or not selected_year or not selected_parameter:
            return {'data': [], 'layout': {'title': 'No data available'}}, None

        # 年度データを取得
        year_data = calculated_results.get(selected_year, {})

        # フォルダカテゴリでフィルタリング
        if selected_category:
            year_data = {
                attendance_number: data
                for attendance_number, data in year_data.items()
                if data.get('category') == selected_category
            }

        # クラスでフィルタリング
        if selected_classes:
            if not isinstance(selected_classes, (list, set)):
                selected_classes = [selected_classes]
            filtered_data = {
                attendance_number: data
                for attendance_number, data in year_data.items()
                if data.get('classId') in selected_classes
            }
        else:
            filtered_data = year_data

        # フィルタリング後のデータがない場合の処理
        if not filtered_data:
            return {'data': [], 'layout': {'title': 'No data available'}}, None

        # データをリストに変換
        attendance_data = [
            (
                attendance_number,
                data.get(selected_parameter, 0),
                data.get(selected_extra_parameter, 0) if selected_extra_parameter else None
            )
            for attendance_number, data in filtered_data.items()
            if selected_parameter in data
        ]

        # 並べ替えの処理
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            attendance_data.sort(key=lambda x: x[1])
        elif triggered_id == 'order-desc':
            attendance_data.sort(key=lambda x: x[1], reverse=True)
        elif triggered_id == 'order-number':
            attendance_data.sort(key=lambda x: int(x[0]))

        # グラフデータを抽出
        attendance_numbers = [x[0] for x in attendance_data]
        y_values_original = [x[1] for x in attendance_data]
        y_values_extra = [x[2] for x in attendance_data] if selected_extra_parameter else None

        # 抽出後のデータがない場合の処理
        if not attendance_numbers:
            return {'data': [], 'layout': {'title': 'No data available'}}, None

        # 正規化の処理
        normalize = 'normalize' in normalize_toggle
        if normalize:
            max_original_value = max(y_values_original) if y_values_original else 1
            y_values_original = [value / max_original_value for value in y_values_original]

            if y_values_extra:
                max_extra_value = max(y_values_extra) if y_values_extra else 1
                y_values_extra = [value / max_extra_value for value in y_values_extra]

        # パラメータラベルの設定
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
        selected_param_label = parameter_labels.get(selected_parameter, selected_parameter)
        extra_param_label = parameter_labels.get(selected_extra_parameter, selected_extra_parameter) if selected_extra_parameter else None

        # グラフデータ作成
        original_data = go.Bar(
            x=attendance_numbers,
            y=y_values_original,
            text=y_values_original,  # スコアをラベルとして表示
            textposition='outside',  # ラベルの位置をバーの外側に設定
            marker={'color': 'rgba(255, 99, 71, 1)'},
            name=f'{selected_param_label} (メイン)',
            width=0.4,
            customdata=attendance_numbers  # 必要ならそのまま
        )

        data = [original_data]

        if selected_extra_parameter and y_values_extra:
            extra_data_trace = go.Bar(
                x=attendance_numbers,
                y=y_values_extra,
                text=y_values_extra,  # サブデータのスコアをラベルとして表示
                textposition='outside',
                marker={'color': 'rgba(100, 150, 255, 1)'},
                name=f'{extra_param_label} (サブ)',
                width=0.4,
                customdata=attendance_numbers
            )
            data.append(extra_data_trace)

        # グラフのレイアウト設定
        layout = {
            'title': f'{selected_param_label} ({selected_year})' + (f' と {extra_param_label}' if selected_extra_parameter else ''),
            'xaxis': {'title': '出席番号', 'type': 'category'},
            'yaxis': {'title': 'Normalized Values' if normalize else 'Values'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)',
            'height': 400
        }

        return {'data': data, 'layout': layout}, attendance_data







        
    @app.callback(
        Output('class-dropdown', 'options'),
        Input('year-dropdown', 'value')
    )
    def update_class_dropdown(selected_year):
        if not selected_year or selected_year not in calculated_results:
            return []
        
        year_data = calculated_results[selected_year]
        class_ids = set(student_data.get('classId') for student_data in year_data.values() if 'classId' in student_data)
        return [{'label': f'Class {class_id}', 'value': class_id} for class_id in sorted(class_ids) if class_id is not None]

    @app.callback(
        Output('popup-graph', 'figure'),
        Input('x-parameter-dropdown', 'value'),  # X軸の入力
        Input('y-parameter-dropdown', 'value'),  # Y軸の入力
        Input('year-dropdown', 'value'),         # 年度の入力
        Input('class-dropdown', 'value'),        # クラスの入力
        Input('toggle-outliers', 'n_clicks')     # 外れ値を除外するトグルボタン
    )
    def update_scatter_plot(x_param, y_param, selected_year, selected_classes, toggle_outliers):
        if x_param and y_param and selected_year:
            year_data = calculated_results.get(selected_year, {})

            # クラスによるフィルタリング
            if selected_classes:
                year_data = {
                    attendance_number: data
                    for attendance_number, data in year_data.items()
                    if data.get('classId') in selected_classes
                }

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
                    title={'text': f"X軸 {x_label} Y軸 {y_label} の散布図", 'font': {'size': 28}},  # タイトルのフォントサイズ
                    xaxis_title={'text': f"X軸 {x_label}", 'font': {'size': 28}},  # X軸タイトルのフォントサイズ
                    yaxis_title={'text': f"Y軸 {y_label}", 'font': {'size': 28}}   # Y軸タイトルのフォントサイズ
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
            Input('reset-radar-button', 'n_clicks'),
            Input('toggle-average', 'value'),
            Input('parameter-graph', 'figure')  # 棒グラフ全体のデータを取得
        ]
    )
    def display_radar_chart(parameter_graph_clickData, selected_year, reset_n_clicks, toggle_average, parameter_graph_figure):
        global selected_attendance_numbers
        print(f"Main graph click data: {parameter_graph_clickData}")
        print(f"Selected year: {selected_year}")
        print(f"Selected attendance numbers: {selected_attendance_numbers}")
        print(f"parameter_graph_figure: {parameter_graph_figure}")
        print(f"type(parameter_graph_figure): {type(parameter_graph_figure)}")

        # 棒グラフのデータ構造を確認し取得
        attendance_numbers_in_bar = []
        if isinstance(parameter_graph_figure, str):
            import json
            parameter_graph_figure = json.loads(parameter_graph_figure)

        if 'data' in parameter_graph_figure and isinstance(parameter_graph_figure['data'], list):
            if len(parameter_graph_figure['data']) > 0 and 'x' in parameter_graph_figure['data'][0]:
                attendance_numbers_in_bar = parameter_graph_figure['data'][0]['x']

        # リセットボタンが押された場合
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-radar-button':
            print("Reset button clicked")
            selected_attendance_numbers = []  # 選択された出席番号をリセット
            return generate_radar_chart([], selected_year, attendance_numbers_in_bar, show_average=False)

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

        # トグルボタンの状態を取得
        show_average = 'show_average' in toggle_average
        return generate_radar_chart(selected_attendance_numbers, selected_year, attendance_numbers_in_bar, show_average)



    def generate_radar_chart(selected_attendance_numbers, selected_year, attendance_numbers_in_bar, show_average):
        print(f"Generating radar chart for: {selected_attendance_numbers} in year {selected_year}")
        if not selected_attendance_numbers:
            return {'data': [], 'layout': go.Layout(title='レーダーチャート')}

        radar_traces = []
        overall_data = []

        # 最大値の計算 (全IDのデータ)
        overall_max_values = {
            key: max(
                d.get(key, 0) for d in calculated_results.get(selected_year, {}).values()
            )
            for key in [
                'video_start_count', 'audio_start_count', 'answer_count',
                'correct_answers', 'incorrect_answers', 'suspended_count',
                'launched_count', 'total_answer_time', 'recording_time',
                'video_time', 'recorder_start_count', 'movie_completed_count',
                'continue_count', 'test_result'
            ]
        }

        # 個別データのレーダーチャート追加
        for attendance_number in selected_attendance_numbers:
            data = calculated_results.get(selected_year, {}).get(attendance_number, {})
            if not data:
                continue

            overall_data.append(data)  # 平均値計算のために全データを保存

            normalized_values = [
                data.get(key, 0) / overall_max_values[key] if overall_max_values[key] > 0 else 0
                for key in overall_max_values
            ]

            radar_traces.append(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],  # 閉じた図形にするために最初の値を追加
                theta=list(overall_max_values.keys()) + [list(overall_max_values.keys())[0]],  # ラベルをリスト化
                name=f'ID{attendance_number}の個人データ',
                fill='toself'
            ))

        # 棒グラフ全体の平均値を計算
        if show_average:
            bar_data = [
                calculated_results[selected_year][id_number]
                for id_number in attendance_numbers_in_bar
                if id_number in calculated_results[selected_year]
            ]

            average_data = {
                key: sum(d.get(key, 0) for d in bar_data) / len(bar_data)
                for key in overall_max_values
            }

            # 平均値を正規化
            normalized_average_values = [
                average_data[key] / overall_max_values[key] if overall_max_values[key] > 0 else 0
                for key in overall_max_values
            ]

            radar_traces.append(go.Scatterpolar(
                r=normalized_average_values + [normalized_average_values[0]],  # 閉じた図形にするために最初の値を追加
                theta=list(overall_max_values.keys()) + [list(overall_max_values.keys())[0]],  # ラベルをリスト化
                name='棒グラフ全体の平均値',
                fill='toself',
                line=dict(dash='dash')  # 平均値の線を破線で表示
            ))

        return {
            'data': radar_traces,
            'layout': go.Layout(
                title='レーダーチャート',
                polar={
                    'radialaxis': {'visible': True, 'range': [0, 1], 'tickfont': {'size': 14}},
                    'angularaxis': {'tickfont': {'size': 24}}
                },
                showlegend=True,
                legend={'x': 0.65, 'y': 1, 'xanchor': 'left', 'font': {'size': 22}},
                autosize=True,
                margin={'l': 50, 'r': 50, 'b': 50, 't': 75},
                height=500
            )
        }

    
# UnitType選択に応じて月の選択肢を更新
    @app.callback(
        Output('month-dropdown', 'options'),
        Input('unit-type-selector', 'value')
    )
    def update_month_options(selected_unit_type):
        if selected_unit_type:
            # 選択されたUnitTypeに基づいて、学習が行われた月をフィルタ
            filtered_months = df[df['UnitType'] == selected_unit_type]['timeStamp'].dt.month.unique()
            return [{'label': f'{month}月', 'value': month} for month in sorted(filtered_months)]
        return []

    # 月の選択に応じて日付の選択肢を更新
    @app.callback(
    Output('day-dropdown', 'options'),
    [Input('month-dropdown', 'value')],
    [State('unit-type-selector', 'value')]
)
    def update_day_options(selected_month, selected_unit_type):
        if selected_unit_type and selected_month:
            # UnitTypeと月に基づいて学習が行われた日をフィルタ
            filtered_days = df[(df['UnitType'] == selected_unit_type) & (df['timeStamp'].dt.month == selected_month)]['timeStamp'].dt.day.unique()
            # 月の最大日数を取得
            max_day = calendar.monthrange(2023, selected_month)[1]  # 年は適宜変更可能
            
            # 選択肢に学習が行われた日とその月の全日を含む
            return [{'label': f'{day}日', 'value': day} for day in range(1, max_day + 1) if day in filtered_days]
        return []



    # メインコールバック
    @app.callback(
        Output('3d-graph', 'figure'),
        [
            Input('parameter-graph', 'clickData'),
            Input('reset-button', 'n_clicks'),
            Input('year-dropdown', 'value'),
            Input('unit-type-selector', 'value'),
            Input('month-dropdown', 'value'),
            Input('day-dropdown', 'value')
        ],
        [State('selected-attendance-numbers', 'data')]
    )
    def display_2d_or_3d_graph(click_data, reset_n_clicks, selected_year, unit_type, selected_month, selected_day, stored_numbers):
        global selected_attendance_numbers

        # リセットボタンが押された場合の処理
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-button':
            selected_attendance_numbers = []
            return go.Figure()

        # クリックデータがある場合、出席番号を取得
        if click_data and 'points' in click_data:
            attendance_number = str(click_data['points'][0]['label'])
        else:
            return dash.no_update

        # 出席番号をリストに追加
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)

        return generate_graph_with_review(selected_attendance_numbers, selected_year, unit_type, selected_month, selected_day)

    # データをフィルタリングする関数
    def filter_data(attendance_numbers, selected_year, unit_type=None, selected_month=None, selected_day=None):
        filtered_data = [data for data in all_extracted_data if str(data['ID']) in attendance_numbers and is_within_academic_year(data['timeStamp'], selected_year)]

        # フィルタの適用
        if selected_month:
            filtered_data = [data for data in filtered_data if data['timeStamp'].month == selected_month]
        if selected_day:
            filtered_data = [data for data in filtered_data if data['timeStamp'].day == selected_day]
        if unit_type:
            filtered_data = [data for data in filtered_data if data['UnitType'] == unit_type]

        filtered_data.sort(key=lambda x: x['timeStamp'])
        directions = calculate_direction(filtered_data)

        for i in range(len(filtered_data)):
            filtered_data[i]['direction'] = directions[i]

        return filtered_data

    # 方向を計算する関数
    def calculate_direction(filtered_data):
        directions = []
        previous_unit_number = None
        for data in filtered_data:
            current_unit_number = int(data.get('UnitNumber', 0))  # 現在のUnitNumber
            if previous_unit_number is None:
                directions.append('Forward')  # 初回は常に進行
            else:
                directions.append('Review' if current_unit_number < previous_unit_number else 'Forward')
            previous_unit_number = current_unit_number
        return directions

    # グラフを生成する関数
    def generate_graph_with_review(attendance_numbers, selected_year, unit_type=None, selected_month=None, selected_day=None):
        if not attendance_numbers:
            return go.Figure()

        # フィルタリングしたデータ
        filtered_data = filter_data(attendance_numbers, selected_year, unit_type, selected_month, selected_day)
        if not filtered_data:
            return go.Figure()

        # データを日付順にソート
        filtered_data = sorted(filtered_data, key=lambda x: x['timeStamp'])

        # 横軸の範囲を設定
        if selected_month:
            start_date = datetime(int(selected_year), int(selected_month), 1)
            _, last_day = calendar.monthrange(int(selected_year), int(selected_month))
            end_date = datetime(int(selected_year), int(selected_month), last_day)
        else:
            start_date = datetime(int(selected_year), 4, 1)
            end_date = datetime(int(selected_year) + 1, 2, 28)
            if (int(selected_year) + 1) % 4 == 0 and ((int(selected_year) + 1) % 100 != 0 or (int(selected_year) + 1) % 400 == 0):
                end_date = datetime(int(selected_year) + 1, 2, 29)

        # データの準備
        x_vals = [data['timeStamp'] for data in filtered_data]
        y_vals = [int(data.get('UnitNumber', 0)) for data in filtered_data]
        directions = calculate_direction(filtered_data)

        # グラフ生成
        fig = go.Figure()

        # 復習と進行を個別にプロット
        for i in range(1, len(x_vals)):
            is_forward = directions[i] == 'Forward'
            fig.add_trace(go.Scatter(
                x=x_vals[i - 1:i + 1],
                y=y_vals[i - 1:i + 1],
                mode='lines',  # 点を最小化して線のみ描画
                line=dict(color='blue' if is_forward else 'red', width=2, dash='solid' if is_forward else 'dash'),
                showlegend=False  # 凡例は一回だけ表示
            ))

        # レイアウト設定
        fig.update_layout(
            title={'text': f'ID {attendance_numbers} の時系列データ', 'font': {'size': 25}},
            xaxis_title={'text': '日付', 'font': {'size': 25}},
            yaxis_title={'text': 'Unit番号', 'font': {'size': 25}},
            xaxis=dict(
                range=[start_date, end_date],
                tickformat='%d' if selected_month else '%b %Y',
                tickfont={'size': 20}
            ),
            yaxis=dict(dtick=1, tickfont={'size': 20}),
            height=400
        )

        # 特定の日付の範囲を強調
        if selected_year and selected_month and selected_day:
            selected_date = datetime(int(selected_year), int(selected_month), int(selected_day))
            fig.update_xaxes(
                range=[
                    selected_date.replace(hour=0, minute=0, second=0),
                    selected_date.replace(hour=23, minute=59, second=59)
                ],
                tickformat="%H:%M"
            )

        return fig



    
    @app.callback(
        Output('ordered-learning-line-graph', 'figure'),
        [
            Input('parameter-graph', 'clickData'),
            Input('order-radio', 'value'),  # 全体順序 or 形式別順序
            Input('toggle-backtracking', 'value'),  # 行き戻りの表示切り替え
            Input('activity-type-dropdown', 'value'),  # 選択されたアクティビティタイプ
            Input('reset-learning-order-button', 'n_clicks')  # リセットボタンのクリックイベント
        ],
        [
            State('year-dropdown', 'value'),
            State('class-dropdown', 'value'),
            State('toggle-outliers', 'n_clicks')
        ]
    )
    def update_ordered_learning_line_graph(click_data, order_selection, toggle_backtracking, selected_activity,
                                        reset_n_clicks, selected_year, selected_class, toggle_outliers):
        # リセットボタンが押された場合
        if reset_n_clicks and dash.callback_context.triggered_id == 'reset-learning-order-button':
            print("Reset button clicked")
            return {
                'data': [],
                'layout': {
                    'title': '学習履歴順序',
                    'xaxis': {'title': "学習順序 (順番)"},
                    'yaxis': {'title': "ユニット番号"},
                    'height': 600,
                    'plot_bgcolor': "rgba(240, 240, 240, 0.95)"
                }
            }

        # データがない場合
        if not click_data or not all_extracted_data:
            return {'data': [], 'layout': {'title': 'No data available'}}

        # クリックされたデータポイントから学習者IDを抽出
        selected_id = click_data['points'][0]['customdata']

        # 指定された学習者、年度、クラスのデータをフィルタリング
        filtered_data = [
            entry for entry in all_extracted_data
            if str(entry['ID']) == str(selected_id) and
            entry['Year'] == str(selected_year) and
            (selected_class is None or entry['classId'] == selected_class)
        ]

        if not filtered_data:
            return {'data': [], 'layout': {'title': 'No data available'}}

        # データフレーム生成
        df = pd.DataFrame(filtered_data)
        df['UnitNumber'] = pd.to_numeric(df['UnitNumber'], errors='coerce')
        df = df.dropna(subset=['UnitNumber'])

        # グラフの描画
        if order_selection == '全体':
            x_axis = 'sequence_global'
            df = df.sort_values(by=x_axis)
            title = f"全体の学習履歴順序 - 年度: {selected_year}, クラス: {selected_class or '全体'}"
            fig = go.Figure(
                go.Scatter(
                    x=df[x_axis],
                    y=df['UnitNumber'],
                    mode='lines+markers',
                    name='通常',
                    line=dict(color='blue', width=2),
                    marker=dict(size=8, color='blue')
                )
            )
        else:
            x_axis = 'sequence_activity'
            title = f"形式別の学習履歴順序 - 年度: {selected_year}, クラス: {selected_class or '全体'}"
            fig = go.Figure()
            if selected_activity:
                df = df[df['ActivityType'] == selected_activity]
                if df.empty:
                    return {'data': [], 'layout': {'title': 'No data available'}}
            for activity_type, group in df.groupby('ActivityType'):
                fig.add_trace(
                    go.Scatter(
                        x=group[x_axis],
                        y=group['UnitNumber'],
                        mode='lines+markers',
                        name=f"{activity_type}",
                        line=dict(width=2),
                        marker=dict(size=8)
                    )
                )

        # 行き戻りの処理
        if toggle_backtracking == 'show':
            for i in range(1, len(df)):
                if df['UnitNumber'].iloc[i] < df['UnitNumber'].iloc[i - 1]:
                    fig.add_trace(
                        go.Scatter(
                            x=[df[x_axis].iloc[i - 1], df[x_axis].iloc[i]],
                            y=[df['UnitNumber'].iloc[i - 1], df['UnitNumber'].iloc[i]],
                            mode='lines+markers',
                            line=dict(color='red', width=2, dash='dash'),
                            marker=dict(color='red', size=8),
                            showlegend=False
                        )
                    )

        # レイアウト設定
        fig.update_layout(
            title=title,
            xaxis_title="学習順序 (順番)",
            yaxis_title="ユニット番号",
            height=600,
            plot_bgcolor="rgba(240, 240, 240, 0.95)",
            legend_title_text="区分"
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






        