from dash import dcc, html


def create_layout(attendance_options, data_options):
    layout = html.Div([
        html.H1("Attendance Data Visualization"),

        # 出席番号の選択肢を含むドロップダウンメニュー
        dcc.Dropdown(
            id='attendance-dropdown',
            options=attendance_options,
            value=attendance_options[0]['value']  # デフォルトの選択肢
        ),

        # データパラメータの選択肢を含むドロップダウンメニュー
        dcc.Dropdown(
            id='parameter-dropdown',
            options=data_options,
            value=data_options[0]['value']  # デフォルトの選択肢
        ),

        # グラフを表示するためのコンポーネント
        dcc.Graph(id='data-graph')
    ])
    return layout
