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
    dcc.Dropdown(
        id='year-dropdown',
        options=year_options,
        value=years[0] if years else None
    ),
    dcc.Dropdown(
        id='parameter-dropdown',
        options=[
            {'label': 'Video Start Count', 'value': 'video_start_count'},
            {'label': 'Audio Start Count', 'value': 'audio_start_count'},
            {'label': 'Answer Count', 'value': 'answer_count'},
            {'label': 'Answer Time', 'value': 'answer_time'}
        ],
        value='video_start_count'  # デフォルト値
    ),
    dcc.Graph(
        id='parameter-graph',
        style={'height': '70vh', 'overflowX': 'auto'}
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
