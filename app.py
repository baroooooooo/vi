from flask import Flask, redirect
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from in_it import load_all_data, get_file_list, load_data
from layout import create_layout
from graph import register_callbacks
import os
import pandas as pd
from utils import extract_attendance_number

# Flaskサーバーの設定
server = Flask(__name__)

# Dashアプリケーションの設定
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')



def load_and_sort_data(directory):
    """指定されたディレクトリからデータを読み込み、出席番号でソートして結合する関数"""
    data_dict = {}
    file_paths = get_file_list(directory)
    
    for file_path in file_paths:
        attendance_number = extract_attendance_number(file_path)
        data = load_data(file_path)
        if not data.empty:
            data_dict[attendance_number] = data

    # 出席番号順にソートしてデータを結合
    sorted_attendance_numbers = sorted(data_dict.keys())
    sorted_data = pd.concat([data_dict[num] for num in sorted_attendance_numbers], ignore_index=True)
    
    return sorted_data

@server.route('/')
def index():
    """Flaskのルートでダッシュボードにリダイレクト"""
    return redirect('/dashboard/')

# データの読み込み
directory = 'datas'
file_paths = get_file_list(directory)
data_dict = load_all_data(file_paths)

# デバッグ: データの内容を確認
print(f'File paths: {file_paths}')
print(f'Data dict keys: {data_dict.keys()}')

# 出席番号の選択肢を作成
if not data_dict:
    raise ValueError("Data dictionary is empty. Please check if the data is loaded correctly.")

attendance_options = [{'label': f'ID: {num}', 'value': num} for num in data_dict.keys()]

# 最初のファイルのデータを基にパラメータの選択肢を作成
initial_data = next(iter(data_dict.values()))
data_options = [{'label': col, 'value': col} for col in initial_data.columns]

# レイアウトの設定
app.layout = create_layout(attendance_options, data_options)

# コールバックの登録
register_callbacks(app, data_dict)

if __name__ == '__main__':
    server.run(debug=True)