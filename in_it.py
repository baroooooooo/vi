import pandas as pd
import os
import json
from data_processing import (
    calculate_counts_and_times,
    calculate_submission_count,
    calculate_answer_time,
    calculate_play_counts,
    clean_and_parse_json
)

def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        data = pd.read_csv(file_path)
        print(data.head())  # デバッグ: データの内容を確認
        # JSONパース処理など、データ処理をここで行います
        return data
    except pd.errors.EmptyDataError:
        print(f"No data found in file: {file_path}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        print(f"Parsing error in file: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す
def process_data(data):
    if data.empty:
        return {}

    print(f'Raw Data for Processing: {data.head()}')  # デバッグ: 処理前のデータ確認

    # `calculate_counts_and_times` 関数を利用してデータを処理
    counts_and_times = calculate_counts_and_times(data)

    # ここで必要に応じて追加の処理を行うこともできます
    # 例: answer_time = calculate_answer_time(data['verb'], data['timeStamp'])
    
    return counts_and_times

def prepare_data(directory):
    data_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                year = os.path.basename(root)  # フォルダ名から年を取得
                file_path = os.path.join(root, file)
                attendance_number = os.path.splitext(file)[0]
                print(f'Loading file: {file_path} for ID: {attendance_number}, Year: {year}')
                data = load_data(file_path)
                if not data.empty:
                    if year not in data_dict:
                        data_dict[year] = {}
                    data_dict[year][attendance_number] = process_data(data)
                    print(f'Processed data for {attendance_number} in {year}: {data_dict[year][attendance_number]}')
    return data_dict

def get_file_list(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_paths.append(os.path.join(root, file))
    return file_paths

def load_all_data(file_paths):
    data_dict = {}
    for file_path in file_paths:
        attendance_number = os.path.basename(file_path).split('.')[0]
        print(f'Loading file: {file_path} for ID: {attendance_number}')
        data = load_data(file_path)
        if not data.empty:  # dataが空でないことを確認
            data_dict[attendance_number] = process_data(data)
    return data_dict

# メイン処理の開始
if __name__ == "__main__":
    directory = 'your_directory_path'  # 処理するディレクトリを指定
    results = prepare_data(directory)
    print("Calculation complete. Results:")
    print(results)
