import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    global selected_attendance_numbers
    global first_selected_attendance_number  # グローバルリストとして選択された出席番号を初期化
    selected_attendance_numbers = []  # 初期化はここで行います。
    first_selected_attendance_number=None

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
        # データが正しく読み込まれているか確認
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {'data': [], 'layout': {}}, existing_graphs

        # 計算結果と年データの構造を確認するためのデバッグ出力
        print(f"calculated_results: {calculated_results}")
        year_data = calculated_results.get(selected_year, {})
        print(f"year_data: {year_data}")
        for attendance_number, data in year_data.items():
            if selected_parameter not in data:
                print(f"'{selected_parameter}' is NOT found in data for attendance_number {attendance_number}")
            else:
                print(f"'{selected_parameter}' is found in data for attendance_number {attendance_number}: {data[selected_parameter]}")
        print(f"selected_parameter: {selected_parameter}")
        print(f"Type of selected_parameter: {type(selected_parameter)}")

        # 'test_result'がyear_dataに存在するか確認
        for attendance_number in year_data:
            print(f"{attendance_number}: {year_data[attendance_number]}")
            test_result = year_data[attendance_number].get('test_result')
            print(f"{attendance_number}のtest_result: {test_result}")
            if test_result is None:
                # test_resultが存在しない場合の処理
                print(f"{attendance_number}のtest_resultが存在しません。データを追加する必要があります。")

        # 特殊ケース: selected_parameterが'test_result'の場合
        if selected_parameter == 'test_result':
            print("test_resultが選択されています")

        # 選択したパラメータで出席番号を抽出
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if selected_parameter in year_data[attendance_number]
        ]
        print(f"attendance_numbers: {attendance_numbers}")  # attendance_numbersを確認

        if not attendance_numbers:
            print("attendance_numbersが空です。selected_parameterが年データ内に存在するか確認してください。")
            print(f"selected_parameter: {selected_parameter}")
            print(f"Type of selected_parameter: {type(selected_parameter)}")
            print(f"year_data keys: {year_data.keys()}")  # year_dataの全キーを表示
            for key, value in year_data.items():
                print(f"{key}: {value}")  # 各キーとその値を表示
            return {'data': [], 'layout': {}}, existing_graphs

        # 選択された順序に基づくソートロジック
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            order = 'asc'
        elif triggered_id == 'order-desc':
            order = 'desc'
        elif triggered_id == 'order-number':
            order = 'number'
        else:
            order = 'number'

        # 出席番号のソート
        if order == 'asc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter])
        elif order == 'desc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter], reverse=True)
        elif order == 'number':
            attendance_numbers.sort(key=int)

        # グラフデータの構築
        x_positions = list(range(len(attendance_numbers)))
        y_values_original = [year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers]
        print(f"y_values_original: {y_values_original}")  # y_values_originalを確認

        # 選択したパラメータの元データ用の棒グラフ
        original_data = go.Bar(
            x=x_positions,
            y=y_values_original,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter} (Original)'
        )
        print(f"original_data: {original_data}")  # original_dataを確認

        # グラフレイアウト
        layout = {
            'title': f'{selected_parameter} for {selected_year}',
            'xaxis': {
                'title': '出席番号',
                'tickmode': 'array',
                'tickvals': x_positions,
                'ticktext': attendance_numbers,
            },
            'yaxis': {'title': f'{selected_parameter} 値'},
            'barmode': 'group',
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'
        }

        # 既存のグラフリストを初期化
        if existing_graphs is None or isinstance(existing_graphs, dict):
            existing_graphs = []

        # グラフの追加/削除を処理
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
        [Input('parameter-graph', 'clickData'),  # 棒グラフのクリックデータ
         Input('year-dropdown', 'value'),  # 選択された年
         Input('reset-radar-button', 'n_clicks')]  # リセットボタンのクリック
    )
    def display_radar_chart(clickData, selected_year, reset_n_clicks):
        global selected_attendance_numbers, first_selected_attendance_number  # グローバル変数を使用することを宣言

        # reset_n_clicks が None の場合は 0 とみなす
        reset_n_clicks = reset_n_clicks or 0

        if reset_n_clicks > 0:
            # リセット処理: 最初の選択を残す
            print("Reset button clicked")
            if first_selected_attendance_number is not None:
                selected_attendance_numbers = [first_selected_attendance_number]
            else:
                selected_attendance_numbers = []  # 最初の選択がない場合は空にする
            return generate_radar_chart(selected_attendance_numbers, selected_year)  # レーダーチャートを生成

        if clickData is None or selected_year is None:
            print("clickData or selected_year is None")
            return {}

        # クリックされた出席番号を抽出
        attendance_number = clickData['points'][0]['text']
        print(f"Selected attendance number: {attendance_number}")

        # 最初の選択を記録
        if first_selected_attendance_number is None:
            first_selected_attendance_number = attendance_number

        # すでに選択された出席番号が存在する場合、追加しない
        if attendance_number not in selected_attendance_numbers:
            selected_attendance_numbers.append(attendance_number)

        return generate_radar_chart(selected_attendance_numbers, selected_year)  # レーダーチャートを生成


    def generate_radar_chart(selected_attendance_numbers, selected_year):
        # レーダーチャートのためのトレースリストを初期化
        radar_traces = []

        # 各選択された出席番号のデータを取得
        for attendance_number in selected_attendance_numbers:
            # 選択された出席番号のデータを取得
            data = calculated_results.get(selected_year, {}).get(attendance_number, {})

            if not data:
                continue

            # 正規化のための全体の最大値を計算
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

            # レーダーチャートのために値を正規化
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

            # カテゴリの設定
            categories = [
                'ビデオ開始回数', '音声開始回数', '回答回数', '正解数', '不正解数',
                '中断回数', '起動回数', '回答時間合計', '録音時間', 'ビデオ時間',
                '録画開始回数', '動画再生完了回数', '継続回数', '成績'
            ]

            # 各出席番号のレーダーチャートのトレースを追加
            radar_traces.append(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],  # 最後の値を最初に戻して閉じる
                theta=categories + [categories[0]],  # 最後のカテゴリを最初に戻して閉じる
                fill='toself',
                name=attendance_number,  # 各出席番号の名前
                opacity=0.5  # 透過度を設定
            ))

        # レーダーチャートのデータ
        radar_data = go.Figure(data=radar_traces)

        # レーダーチャートのレイアウト設定
        radar_data.update_layout(
            title=f'{selected_year}のデータ',
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]  # 正規化されているので0から1の範囲
                )),
            showlegend=True
        )

        print(radar_data)
        return radar_data

