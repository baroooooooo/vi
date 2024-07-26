from flask import Flask
import dash
from in_it import load_all_data, get_file_list
from layout import create_layout
from graph import register_callbacks

server = Flask(__name__)
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# データの読み込み
directory = 'datas'
file_paths = get_file_list(directory)
data_dict = load_all_data(file_paths)

# デバッグ: データの内容を確認
print(f'File paths: {file_paths}')
print(f'Data dict keys: {data_dict.keys()}')

# 出席番号の選択肢を作成
if not data_dict:
    raise ValueError("Data dictionary is empty."
                     "Please check if the data is loaded correctly.")

attendance_options = [{'label': f'ID: {num}', 'value': num}
                      for num in data_dict.keys()]

# 最初のファイルのデータを基にパラメータの選択肢を作成
initial_data = next(iter(data_dict.values()))
data_options = [{'label': col, 'value': col} for col in initial_data.columns]

# レイアウトの設定
app.layout = create_layout(attendance_options, data_options)

# コールバックの登録
register_callbacks(app, data_dict)


@server.route('/')
def index():
    return 'Hello, this is the Flask app!'


if __name__ == '__main__':
    server.run(debug=True)
