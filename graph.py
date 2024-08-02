from dash import dcc, html
from dash.dependencies import Input, Output

def register_callbacks(app, data_dict):
    @app.callback(
        Output('parameter-graph', 'figure'),
        [Input('attendance-dropdown', 'value'),
         Input('parameter-dropdown', 'value')]
    )
    def update_graph(attendance_id, parameter):
        if not attendance_id or not parameter:
            return {}

        df = data_dict.get(attendance_id)
        if df is None:
            return {}

        # 出席番号でソート
        df = df.sort_values(by='attendance_number')

        fig = {
            'data': [{
                'x': df['attendance_number'],  # x軸に出席番号を指定
                'y': df[parameter],
                'type': 'lines',
                'name': f'ID {attendance_id}'
            }],
            'layout': {
                'title': f'{parameter} over Attendance Number',
                'xaxis': {
                    'title': 'Attendance Number',
                    'tickmode': 'linear',
                    'tickvals': df['attendance_number'].tolist(),  # x軸の目盛りを設定
                    'ticktext': [str(num) for num in df['attendance_number']]  # 目盛りのラベルを設定
                },
                'yaxis': {
                    'title': parameter
                },
                'autosize': True,
                'xaxis': {
                    'title': 'Attendance Number',
                    'range': [df['attendance_number'].min(), df['attendance_number'].max()],  # x軸の表示範囲を設定
                    'rangeslider': {'visible': True}  # スクロールバーを表示
                },
                'yaxis': {
                    'title': parameter
                },
                'margin': {
                    'l': 40, 'r': 20, 't': 30, 'b': 60  # グラフの余白を設定
                }
            }
        }
        return fig

