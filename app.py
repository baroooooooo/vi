import dash
from in_it import load_all_data, get_file_list
from layout import create_layout
from graph import register_callbacks

# Dashアプリケーションの作成
app = dash.Dash(__name__)

# データの読み込み
directory = 'data'
file_paths = get_file_list(directory)
data_dict = load_all_data(file_paths)

# 出席番号の選択肢を作成
attendance_options = [{'label': f'ID: {num}', 'value': num} 
                      for num in data_dict.keys()]

# 最初のファイルのデータを基にパラメータの選択肢を作成
initial_data = next(iter(data_dict.values()))
data_options = [{'label': col, 'value': col} for col in initial_data.columns]

# レイアウトの設定
app.layout = create_layout(attendance_options, data_options)

# コールバックの登録
register_callbacks(app, data_dict)

# サーバーの起動
if __name__ == '__main__':
    app.run_server(debug=True)
