import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask, redirect
from graph import register_callbacks
from in_it import prepare_data

# Flaskサーバーの作成
server = Flask(__name__)

# Dashアプリケーションの作成
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# データの準備
directory = 'datas'
calculated_results = prepare_data(directory)

# 年度のオプションを追加
years = list(calculated_results.keys())  # ディレクトリから取得した年
year_options = [{'label': str(year), 'value': year} for year in years]

# Dashのレイアウト
app.layout = html.Div([
    html.H1("KoToToMo Plus Visualizer"),  # タイトル
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=year_options,
                value=years[0] if years else None,
                placeholder="年度を選択してください",
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='parameter-dropdown',
                options=[
                    {'label': 'Video Start Count', 'value': 'video_start_count'},
                    {'label': 'Audio Start Count', 'value': 'audio_start_count'},
                    {'label': 'Answer Count', 'value': 'answer_count'},
                    {'label': 'Answer Time', 'value': 'total_answer_time'},
                    {'label': 'Correct Answers', 'value': 'correct_answers'},
                    {'label': 'Incorrect Answers', 'value': 'incorrect_answers'},
                    {'label': 'Suspended Count', 'value': 'suspended_count'},
                    {'label': 'Launched Count', 'value': 'launched_count'},
                    {'label': 'Recording Time', 'value': 'recording_time'},
                    {'label': 'Video Time', 'value': 'video_time'},
                    {'label': 'Recorder Start Count', 'value': 'recorder_start_count'},
                    {'label': 'Movie Completed Count', 'value': 'movie_completed_count'},
                    {'label': 'Continue Count', 'value': 'continue_count'}
                ],
                value='video_start_count',  # デフォルト値
                placeholder="パラメータを選択してください",
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),

    dcc.Graph(
        id='parameter-graph',
        style={'height': '70vh', 'overflowX': 'auto'}
    ),

     dcc.Graph(
        id='radar-chart',
        style={'height': '50vh'}  # スタイルを設定
    )
])

# コールバックの設定
register_callbacks(app, calculated_results)

@server.route('/')
def index():
    return redirect('/dashboard/')

# DashとFlaskを併用してアプリケーションを実行
if __name__ == '__main__':
    app.run_server(debug=True)
