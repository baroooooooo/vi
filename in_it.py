import pandas as pd
import json
import os
import traceback
from data_processing import verb_change, stamp_to_ymd, stamp_to_deff_time, to_value_list


def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        data = pd.read_csv(file_path)
        print(data.head())  # デバッグ: データの内容を確認
        
        # 必要な列のみを残す
        required_columns = ['actor', 'object', 'verb', 'extension', 'timeStamp']
        data = data[required_columns]
        
        data['actor'] = data['actor'].apply(lambda x: json.loads(x)[0]['openId'])
        data['object'] = data['object'].apply(lambda x: json.loads(x)[0]['objectId'])
        data['verb'] = data['verb'].apply(lambda x: json.loads(x)[0]['display'])
        data['extension'] = data['extension'].apply(lambda x: json.loads(x)[0]['deviceId'])
        data['timeStamp'] = pd.to_datetime(data['timeStamp'])
        
        # データ整形
        data_list = data.values.tolist()
        data_list = to_value_list(data_list)
        data_list = verb_change(data_list)
        df = pd.DataFrame(data_list)
        df = stamp_to_deff_time(df)
        df = stamp_to_ymd(df)
        print(f"Loaded data for {file_path} successfully")
        return df
    except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        traceback.print_exc()
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す


def get_file_list(directory):
    print(f"Searching for files in directory: {directory}")  # デバッグ用
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f'Found file: {file_path}')  # デバッグ用
                file_paths.append(file_path)
    print(f"Found {len(file_paths)} CSV files.")  # デバッグ用
    return file_paths


def load_all_data(file_paths):
    data_dict = {}
    for file_path in file_paths:
        attendance_number = os.path.basename(file_path).split('.')[0]
        print(f'Loading file: {file_path} for ID: {attendance_number}')
        # デバッグ用
        data = load_data(file_path)
        if not data.empty:
            data_dict[attendance_number] = data
            print(f"Data loaded for ID: {attendance_number}")
        else:
            print(f"No data loaded for ID: {attendance_number}")
    print(f"Total IDs loaded: {len(data_dict)}")  # デバッグ用
    return data_dict
