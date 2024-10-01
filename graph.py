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

        # order の決定
        triggered_id = dash.callback_context.triggered_id
        if triggered_id == 'order-asc':
            order = 'asc'
        elif triggered_id == 'order-desc':
            order = 'desc'
        elif triggered_id == 'order-number':
            order = 'number'
        else:
            order = 'number'

        # 選択された年のデータを取得
        year_data = calculated_results.get(selected_year, {})

        # 存在する出席番号だけを抽出
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if year_data[attendance_number].get(selected_parameter) is not None
        ]

        # 全体の最小値と最大値を計算
        parameter_values = [
            year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers
        ]
        min_value = min(parameter_values)
        max_value = max(parameter_values)

        # ソート順に基づいて出席番号を並べ替え
        if order == 'asc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter])
        elif order == 'desc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter], reverse=True)
        elif order == 'number':
            attendance_numbers.sort(key=int)

        x_positions = list(range(len(attendance_numbers)))

        # 元の値と正規化された値を計算
        y_values_original = [
            year_data[attendance_number][selected_parameter] for attendance_number in attendance_numbers
        ]
        
        # 正規化された値の計算（全体に対して正規化）
        y_values_normalized = [
            (year_data[attendance_number][selected_parameter] - min_value) / (max_value - min_value)
            if max_value != min_value else 0  # 最大値と最小値が等しい場合は0に設定
            for attendance_number in attendance_numbers
        ]

        # 元のデータを表示するためのグラフ
        original_data = go.Bar(
            x=x_positions,
            y=y_values_original,
            text=attendance_numbers,  # 数値を文字列に変換して表示
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=f'{selected_parameter} (Original)'
        )

        layout = {
            'title': f'{selected_parameter} for {selected_year}',
            'xaxis': {
                'title': 'Attendance Number',
                'tickmode': 'array',
                'tickvals': x_positions,
                'ticktext': attendance_numbers,
                'tickangle': 0,
                'tickfont': {
                    'size': 12,
                    'color': 'black'
                }
            },
            'yaxis': {'title': f'{selected_parameter} Value'},
            'barmode': 'group',
            'bargap': 0,
            'bargroupgap': 0.1,
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'
        }

        # 既存のグラフデータをリストとして初期化
        if existing_graphs is None or isinstance(existing_graphs, dict):
            existing_graphs = []

        # 追加と削除のロジック
        if add_graph_n_clicks > 0:
            existing_graphs.append(dcc.Graph(
                id={'type': 'dynamic-graph', 'index': len(existing_graphs)},
                figure={'data': [original_data], 'layout': layout}
            ))
        elif remove_graph_n_clicks > 0:
            if existing_graphs:
                existing_graphs.pop()

        # 最後に表示するグラフデータを返す
        return {'data': [original_data], 'layout': layout}, existing_graphs

    
    @app.callback(
        Output('radar-chart', 'figure'),
        [Input('parameter-graph', 'clickData'),  # クリックデータ
         Input('year-dropdown', 'value')]  # 選択された年
    )
    def display_radar_chart(clickData, selected_year):
        if clickData is None or selected_year is None:
            return {}
        
        # クリックした出席番号を取得
        attendance_number = clickData['points'][0]['text']  # 出席番号が 'text' に格納されている

        # クリックした出席番号のデータを取得
        data = calculated_results.get(selected_year, {}).get(attendance_number, {})

        if not data:
            return {}

        # 全体に対する正規化を行うための最大値を計算
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
        }

        # レーダーチャートのために正規化
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
        ]

        categories = [
            '動画再生回数', '音声再生回数', '回答回数', '正解数', 
            '不正解数', '中断回数', 'アプリ起動回数', '回答時間', 
            '録音時間', '動画再生時間', '録音回数', '動画再生完了回数', '復習回数'
        ]

        # レーダーチャートを作成
        fig = go.Figure()

        # レーダーチャートを描画
        fig.add_trace(go.Scatterpolar(
            r=normalized_values + [normalized_values[0]],  # 最初の値を最後に追加して閉じる
            theta=categories + [categories[0]],  # 最初のカテゴリを追加
            fill='toself'
        ))

        fig.update_layout(polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]  # 正規化した値は 0 から 1 の範囲
            )
        ),
        showlegend=False)

        return fig
