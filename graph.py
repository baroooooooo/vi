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
            return {'data': [], 'layout': {}}, graph_data

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

        # ソート順に基づいて出席番号を並べ替え
        if order == 'asc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter])
        elif order == 'desc':
            attendance_numbers.sort(key=lambda x: year_data[x][selected_parameter], reverse=True)
        elif order == 'number':
            attendance_numbers.sort(key=int)

        x_positions = list(range(len(attendance_numbers)))
        y_values = [
            year_data[attendance_number][selected_parameter] / 3600 if selected_parameter == 'total_answer_time' 
            else year_data[attendance_number][selected_parameter]
            for attendance_number in attendance_numbers
        ]

        new_data = go.Bar(
            x=x_positions,
            y=y_values,
            text=attendance_numbers,  # 数値を文字列に変換して表示
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},
            name=selected_parameter
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
            'yaxis': {'title': 'Value'},
            'barmode': 'group',
            'bargap': 0,
            'bargroupgap': 0.1,
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'
        }

        # 既存のグラフデータをリストとして初期化
        if existing_graphs is None:
            existing_graphs = []

        # 追加と削除のロジック
        if add_graph_n_clicks > 0:
            existing_graphs.append(dcc.Graph(
                id={'type': 'dynamic-graph', 'index': len(existing_graphs)},
                figure={'data': [new_data], 'layout': layout}
            ))
        elif remove_graph_n_clicks > 0:
            if existing_graphs:
                existing_graphs.pop()

        # 最後に表示するグラフデータを返す
        return {'data': [new_data], 'layout': layout}, existing_graphs
    
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

        print(data)
        if not data:
            return {}

        # レーダーチャートの作成
        return create_radar_chart(data)
def create_radar_chart(data):
    categories = ['動画再生回数', '音声再生回数', '回答数', '正解数', '不正解数',
                  '中断回数', '起動回数', '回答時間', '録音時間', '動画再生時間']
    
    values = [data.get('video_start_count', 0),
              data.get('audio_start_count', 0),
              data.get('answer_count', 0),
              data.get('correct_answers', 0),
              data.get('incorrect_answers', 0),
              data.get('suspended_count', 0),
              data.get('launched_count', 0),
              data.get('total_answer_time', 0)/3600,
              data.get('recording_time', 0)/60,
              data.get('video_time', 0)/60]
    print(values)

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True),
        ),
        showlegend=False
    )
    
    return fig