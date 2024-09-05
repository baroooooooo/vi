import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

def register_callbacks(app, calculated_results):
    @app.callback(
        Output('parameter-graph', 'figure'),
        [Input('year-dropdown', 'value'),
         Input('parameter-dropdown', 'value')]
    )
    def update_graph(selected_year, selected_parameter):
        if not calculated_results or selected_year is None or selected_parameter is None:
            return {}

        # 選択された年のデータを取得
        year_data = calculated_results.get(selected_year, {})
        
        # 存在する出席番号だけを抽出
        attendance_numbers = [
            attendance_number for attendance_number in year_data.keys()
            if year_data.get(attendance_number, {}).get(selected_parameter) is not None
        ]
        
        # 出席番号順にソート
        attendance_numbers.sort()

        # ソートされた出席番号に対応する x 軸の位置を設定
        x_positions = list(range(len(attendance_numbers)))
        y_values = [int(year_data.get(attendance_number, {}).get(selected_parameter, 0)) for attendance_number in attendance_numbers]

        # グラフのデータ
        data = go.Bar(
            x=x_positions,  # ソートされた位置に基づく x 軸の位置
            y=y_values,
            text=attendance_numbers,
            textposition='outside',
            marker={'color': 'rgba(255, 99, 71, 0.6)'},  # 色のカスタマイズ
            name=selected_parameter
        )

        # レイアウトの設定
        layout = {
            'title': f'{selected_parameter} for {selected_year}',
            'xaxis': {
                'title': 'Attendance Number',
                'tickmode': 'array',
                'tickvals': x_positions,  # ソートされた位置に基づくラベル
                'ticktext': attendance_numbers,
                'tickangle': 0,  # ラベルの角度を水平に設定
                'tickfont': {
                    'size': 12,  # フォントサイズを指定
                    'color': 'black'  # フォント色を指定（オプション）
                }
            },
            'yaxis': {'title': 'Value'},
            'barmode': 'group',
            'bargap': 0,  # グラフ間の隙間をさらに小さく設定
            'bargroupgap': 0.1,  # グループ間の隙間を小さく設定
            'plot_bgcolor': 'rgba(240, 240, 240, 0.95)'  # 背景色
        }

        return {'data': [data], 'layout': layout}
    
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
    categories = ['Video Starts', 'Audio Starts', 'Answers', 'Correct Answers', 'Incorrect Answers',
                  'Suspended Count', 'Launched Count', 'Total Answer Time', 'Recording Time', 'Video Time']
    
    values = [data.get('video_start_count', 0),
              data.get('audio_start_count', 0),
              data.get('answer_count', 0),
              data.get('correct_answers', 0),
              data.get('incorrect_answers', 0),
              data.get('suspended_count', 0),
              data.get('launched_count', 0),
              data.get('total_answer_time', 0),
              data.get('recording_time', 0),
              data.get('video_time', 0)]
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
