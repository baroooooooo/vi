import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask import Flask, redirect
from graph import register_callbacks
from in_it import prepare_data, load_data_result  # load_result_dataをインポート

# Flaskサーバーの作成
server = Flask(__name__)

# Dashアプリケーションの作成
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# データの準備
directory = 'datas'  # データが格納されているディレクトリ
result_file = os.path.join('vi/results', 'data_result.csv')  # 成績データファイルのパス

# 成績データを読み込み
result_data = load_data_result()  # ここでresult_dataを読み込む
calculated_results = prepare_data(directory, result_data)  # result_dataを追加

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
                    {'label': '動画再生回数', 'value': 'video_start_count'},
                    {'label': '音声再生回数', 'value': 'audio_start_count'},
                    {'label': '回答回数', 'value': 'answer_count'},
                    {'label': '回答時間', 'value': 'total_answer_time'},
                    {'label': '正解数', 'value': 'correct_answers'},
                    {'label': '不正解数', 'value': 'incorrect_answers'},
                    {'label': '中断回数', 'value': 'suspended_count'},
                    {'label': 'アプリ起動回数', 'value': 'launched_count'},
                    {'label': '録音時間', 'value': 'recording_time'},
                    {'label': '動画再生時間', 'value': 'video_time'},
                    {'label': '録音回数', 'value': 'recorder_start_count'},
                    {'label': '動画再生完了回数', 'value': 'movie_completed_count'},
                    {'label': '復習回数', 'value': 'continue_count'},
                    {'label': '成績', 'value': 'test_result'}   
                ],
                value='video_start_count',  # デフォルト値
                placeholder="パラメータを選択してください",
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.Button('番号順', id='order-number', n_clicks=0),
            html.Button('昇順', id='order-asc', n_clicks=0),
            html.Button('降順', id='order-desc', n_clicks=0),
        ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),
    
    html.Div([
        html.Button('Add Graph', id='add-graph-button', n_clicks=0),
        html.Button('Remove Graph', id='remove-graph-button', n_clicks=0),
        html.Button('Reset Radar Chart', id='reset-radar-button', n_clicks=0),  # リセットボタンを追加
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),
    
    html.Div(id='graphs-container', children=[
        dcc.Graph(id='parameter-graph',
                  config={'displayModeBar': True, 'displaylogo': False},
                  style={'cursor': 'pointer'})
    ]),
    
    dcc.Graph(
        id='radar-chart',
        style={'height': '70vh', 'overflowX': 'auto'}
    ),
    dcc.Store(id='graph-data', data={'data': [], 'layout': {}})  # グラフデータを保存
])

# コールバックの設定
register_callbacks(app, calculated_results)

@server.route('/')
def index():
    return redirect('/dashboard/')

# DashとFlaskを併用してアプリケーションを実行
if __name__ == '__main__':
    app.run_server(debug=True)
