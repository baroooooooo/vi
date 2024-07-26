import pandas as pd
import json
import os


def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        data = pd.read_csv(file_path)
        print(data.head())  # デバッグ: データの内容を確認
        data['actor'] = data['actor'].apply(
            lambda x: json.loads(x)[0]['openId']
        )
        data['object'] = data['object'].apply(
            lambda x: json.loads(x)[0]['objectId']
        )
        data['verb'] = data['verb'].apply(
            lambda x: json.loads(x)[0]['display']
        )
        data['extension'] = data['extension'].apply(
            lambda x: json.loads(x)[0]['deviceId']
        )
        data['timeStamp'] = pd.to_datetime(data['timeStamp'])
        return data
    except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す


def get_file_list(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f'Found file: {file_path}')  # デバッグ用
                file_paths.append(file_path)
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
    return data_dict
