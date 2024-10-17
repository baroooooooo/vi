import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask import Flask, redirect
from graph import register_callbacks
from in_it import prepare_and_collect_data, load_data_result  # load_result_dataをインポート
from data_processing import create_3d_plot

# Flaskサーバーの作成
server = Flask(__name__)

# Dashアプリケーションの作成
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# データの準備
directory = 'datas'  # データが格納されているディレクトリ
result_file = os.path.join('vi/results', 'data_result.csv')  # 成績データファイルのパス

# 成績データを読み込み
result_data = load_data_result()  # ここでresult_dataを読み込む
calculated_results, all_extracted_data = prepare_and_collect_data(directory, result_data)  # result_dataを追加

# 年度のオプションを追加
years = list(calculated_results.keys())  # ディレクトリから取得した年
year_options = [{'label': str(year), 'value': year} for year in years]

# Dashのレイアウト
app.layout = html.Div([
    html.H1("KoToToMo Plus Visualizer", style={'text-align': 'center'}),  # タイトル

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=year_options,  # 年のリスト
                value=years[0] if years else None,  # デフォルト値の設定
                placeholder="年を選択してください",
                style={'width': '100%'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '0 10px'}),

        html.Button('外れ値の除外ボタン', id='toggle-outliers', n_clicks=0),

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
                style={'width': '100%'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '0 10px'}),

        html.Div([
            dcc.Dropdown(
                id='extra-parameter-dropdown',
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
                value=None,
                placeholder="パラメータを選択してください",
                style={'width': '100%'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '0 10px'}),

        html.Div([
            dcc.Dropdown(
                id='x-parameter-dropdown',  # X軸用のドロップダウン
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
                value=None,  # デフォルト値
                placeholder="X軸パラメータを選択してください",
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '0 10px'}),

        html.Div([
            dcc.Dropdown(
                id='y-parameter-dropdown',  # Y軸用のドロップダウン
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
                value=None,  # デフォルト値
                placeholder="Y軸パラメータを選択してください",
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '0 10px'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'padding': '10px'}),

    # ... その他のレイアウトコード ...

    html.Div([
        html.Button('番号順', id='order-number', n_clicks=0, style={'margin': '0 5px'}),
        html.Button('昇順', id='order-asc', n_clicks=0, style={'margin': '0 5px'}),
        html.Button('降順', id='order-desc', n_clicks=0, style={'margin': '0 5px'}),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),

    html.Div([  # レーダーチャートのリセットボタン
        html.Button('Reset Radar Chart', id='reset-radar-button', n_clicks=0),
    ], style={'display': 'flex', 'justify-content': 'center', 'padding': '10px'}),
    dcc.RadioItems(
        id='unit-type-selector',
        options=[
            {'label': 'Main Unit', 'value': 'MainUnit'},
            {'label': 'Basic Unit', 'value': 'BasicUnit'}
        ],
        value='MainUnit',  # デフォルトでは 'MainUnit' が選択される
        labelStyle={'display': 'inline-block'}
    ),

    dcc.Graph(
        id='parameter-graph',
        figure={
            'data': [],
            'layout': {'title': 'グラフがありません'}
        },
        config={'displayModeBar': True, 'displaylogo': False},
        style={'cursor': 'pointer'}
    ),

     dcc.Graph(id='popup-graph', style={'height': '80vh', 'width': '100%'}),  # ポップアップグラフも大きく

    dcc.Graph(
        id='radar-chart',
        style={'height': '70vh', 'overflowX': 'auto'}
    ),
    html.Div([
        dcc.Graph(
            id='3d-graph',  # 初期の空のグラフとして設定
            style={
                'height': '800px',  # グラフの高さを制限
                'margin': 'auto'
            }
        )
    ], style={'text-align': 'center'}),

    dcc.Store(id='graph-data', data=[]),
    dcc.Store(id='selected-attendance-numbers', data=[]),
])


# コールバックの設定
register_callbacks(app, calculated_results, all_extracted_data)

@server.route('/')
def index():
    return redirect('/dashboard/')

# DashとFlaskを併用してアプリケーションを実行
if __name__ == '__main__':
    app.run_server(debug=True)
