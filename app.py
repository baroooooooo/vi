import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask import Flask, redirect
from graph import register_callbacks
from in_it import prepare_and_collect_data, load_data_result  # load_result_dataをインポート
from data_processing import create_3d_plot
from datetime import datetime
import pandas as pd

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
for data in all_extracted_data:
    if isinstance(data['timeStamp'], str):  # 文字列の場合のみ変換
        data['timeStamp'] = datetime.strptime(data['timeStamp'], '%Y-%m-%d')
df = pd.DataFrame(all_extracted_data)
# Dashのレイアウト
app.layout = html.Div([
    html.H2("KoToToMo Plus Visualizer", style={'text-align': 'center', 'padding-bottom': '20px'}),

    html.Div([
        dcc.Checklist(
            id='normalize-toggle',
            options=[{'label': '正規化する', 'value': 'normalize'}],
            value=[],  # デフォルトは未選択
            inline=True
        ),
        # 年選択のドロップダウン
        html.Div([
            dcc.Dropdown(
                id='year-dropdown',
                options=year_options,  # 年のリスト
                value=years[0] if years else None,  # デフォルト値の設定
                placeholder="年を選択してください",
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'text-align': 'center',
                    'display': 'inline-block',
                    'vertical-align': 'middle',
                    'border': '2px solid black',  # 枠線を太く、濃く設定
                    'border-radius': '5px'  # 角を少し丸める（オプション）
                }
            ),
        ], style={'margin': '0 10px'}),  # 余白を調整

        html.Div([
            dcc.Dropdown(
                id='class-dropdown',
                options=[],  # 後でコールバックで更新
                placeholder='クラスを選択',
                multi=True,
                clearable=True,
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'text-align': 'center',
                    'display': 'inline-block',
                    'vertical-align': 'middle',
                    'border': '2px solid black',  # 枠線を太く、濃く設定
                    'border-radius': '5px'  # 角を少し丸める（オプション）
                }
            ),
        ],style={'margin': '0 10px'}),

        # パラメータ選択のドロップダウン
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
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'text-align': 'center',
                    'display': 'inline-block',
                    'vertical-align': 'middle',
                    'border': '2px solid black',  # 枠線を太く、濃く設定
                    'border-radius': '5px'  # 角を少し丸める（オプション）
                }
            ),
        ], style={'margin': '0 10px'}),

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
                placeholder="追加パラメータを選択してください",
                clearable=True,
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'vertical-align': 'middle',
                    'border': '1px solid #ccc',  # 通常の枠線
                    'border-radius': '4px',  # 標準的な角丸
                }
            ),
        ], style={'margin': '0 10px'}),

        # X軸選択のドロップダウン
        html.Div([
            dcc.Dropdown(
                id='x-parameter-dropdown',
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
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'text-align': 'center',
                    'display': 'inline-block',
                    'vertical-align': 'middle',
                    'border': '2px solid black',  # 枠線を太く、濃く設定
                    'border-radius': '5px'  # 角を少し丸める（オプション）
                }
            ),
        ], style={'margin': '0 10px'}),

        # Y軸選択のドロップダウン
        html.Div([
            dcc.Dropdown(
                id='y-parameter-dropdown',
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
                style={
                    'width': '200px',
                    'font-size': '24px',
                    'text-align': 'center',
                    'display': 'inline-block',
                    'vertical-align': 'middle',
                    'border': '2px solid black',  # 枠線を太く、濃く設定
                    'border-radius': '5px'  # 角を少し丸める（オプション）
                }
            ),
        ], style={'margin': '0 10px'}),

        # 順序ボタン
        html.Div([
            html.Button('番号順', id='order-number', n_clicks=0),
            html.Button('昇順', id='order-asc', n_clicks=0),
            html.Button('降順', id='order-desc', n_clicks=0)
        ], style={'margin': '0 10px'}),

    ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'center', 'align-items': 'center', 'gap': '10px', 'padding': '10px'}),  # レイアウトを一列に並べるためのスタイル

    
    html.Div([
        dcc.Graph(
            id='parameter-graph',
            figure={'data': [], 'layout': {'title': 'グラフがありません'}},
            config={'displayModeBar': True, 'displaylogo': False},
            style={'cursor': 'pointer', 'height': '340px', 'width': '100%', 'margin-bottom': '40px'}
        ),

        dcc.Graph(id='popup-graph', style={'height': '45vh', 'width': '100%', 'margin-top': '40px'}),  # コンパクトに高さ調整
    ], style={'padding': '0', 'margin': '0', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),

    
    html.Div([
        html.Button('Reset Radar Chart', id='reset-radar-button', n_clicks=0, style={'margin-bottom': '1px'}),  # ボタンの余白をさらに小さく
        dcc.Graph(
            id='radar-chart',
            style={'height': '50vh', 'width': '95%', 'margin-bottom': '0px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            config={'displayModeBar': False},
            figure={
                'layout': {
                    'margin': {'l': 0, 'r': 0, 'b': 0, 't': 50},  # marginを最小化
                    'height': 600,
                    'autosize': False,
                    'polar': {
                        'radialaxis': {'visible': True, 'range': [0, 1]},
                        'domain': {'x': [0.1, 0.9], 'y': [0.1, 0.9]}  # グラフの領域を中央に調整
                    }
                }
            }
        ),
    ]),
    html.Div([ 
            
            dcc.Dropdown(id='unit-type-selector', options=[{'label': ut, 'value': ut} for ut in df['UnitType'].unique()], placeholder="Select Unit Type"),
            dcc.Dropdown(id='month-dropdown', options=[{'label': f'{month}月', 'value': month} for month in sorted(df['timeStamp'].dt.month.unique())], placeholder="Select a month"),
            dcc.Dropdown(id='day-dropdown', placeholder="Select a day"),
            html.Button('Reset Graph', id='reset-button', n_clicks=0, style={'margin-top': '1px', 'margin-bottom': '1px'}),  # ボタンの余白を小さく
            dcc.Graph(
                id='3d-graph',
                style={'height': '70vh', 'width': '95%', 'margin-top': '0px'},
                config={'displayModeBar': False},
                figure={
                    'layout': {
                        'margin': {
                            'l': 0, 'r': 0, 'b': 0, 't': 0
                        },
                        'autosize': True
                    }
                }
            ),
            html.Button(id='reset-learning-order-button', n_clicks=0),
            dcc.Graph(
                id='ordered-learning-line-graph',
                style={'height': '70vh', 'width': '95%', 'margin-top': '0px'},
                config={'displayModeBar': False},
                figure={
                    'layout': {
                        'margin': {
                            'l': 0, 'r': 0, 'b': 0, 't': 0
                        },
                        'autosize': True
                    }
                }
            ),
            html.Div([
                dcc.Dropdown(
                    id='activity-type-dropdown',
                    options=[
                        {'label': 'Grammar', 'value': 'grammar'},
                        {'label': 'Pronunciation', 'value': 'pronunciation'},
                        {'label': 'Speaking', 'value': 'speaking'},
                        {'label': 'Listening', 'value': 'listening'}
                    ],
                    value=None,  # デフォルトで選択なし
                    placeholder="アクティビティタイプを選択してください",
                    clearable=True,
                    style={
                        'width': '200px',
                        'font-size': '16px',
                        'margin-bottom': '10px'
                    }
                ),
                dcc.RadioItems(
                    id='order-radio',
                    options=[
                        {'label': '全体順序', 'value': '全体'},
                        {'label': '形式別順序', 'value': '形式別'}
                    ],
                    value='全体',  # デフォルトで全体順序を選択
                    inline=True,  # 横並びに表示
                    labelStyle={'margin-right': '10px'}
                ),
                dcc.RadioItems(
                    id='toggle-backtracking',
                    options=[
                        {'label': '復習の表示', 'value': 'show'},
                        {'label': '復習を非表示', 'value': 'hide'}
                    ],
                    value='hide',  # デフォルトは非表示
                    inline=True
                )
            ]),

    ]),
    dcc.Store(id='graph-data', data=[]),
    dcc.Store(id='selected-attendance-numbers', data=[]),
    html.Button('外れ値の除外ボタン', id='toggle-outliers', n_clicks=0)
])




# コールバックの設定
register_callbacks(app, calculated_results, all_extracted_data)

@server.route('/')
def index():
    return redirect('/dashboard/')

# DashとFlaskを併用してアプリケーションを実行
if __name__ == '__main__':
    app.run_server(debug=True)
