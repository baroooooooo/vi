import pandas as pd
import json
import os
import traceback
from data_processing import (
    verb_change, stamp_to_ymd, stamp_to_deff_time, to_value_list
)



def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        print(f'Initial data:\n{data.head()}')  # デバッグ: データの内容を確認

        # 列名を変更
        if 'timestamp' in data.columns:
            data.rename(columns={'timestamp': 'timeStamp'}, inplace=True)
        else:
            print("Warning: 'timestamp' column not found in the data.")

        print(f'Data after renaming columns:\n{data.head()}')  # デバッグ: 列名変更後のデータ確認

        # 必要な列のみを残す
        required_columns = ['actor', 'timeStamp', 'object', 'result', 'verb', 'extension']

        if not all(col in data.columns for col in required_columns):
            raise Exception(f"Required columns missing in {file_path}")

        data = data[required_columns]
        print(f'Data with required columns:\n{data.head()}')  # デバッグ: 必要な列のみのデータ確認

        # JSON列のパース
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
        print(f'Data with parsed timeStamp:\n{data.head()}')  # デバッグ: timeStamp列のパース後のデータ確認

        # データ整形
        data_list = data.values.tolist()
        print(f'Data list before to_value_list:\n{data_list[:5]}')  # デバッグ: to_value_list前のデータ確認
        data_list = to_value_list(data_list)
        print(f'Data list after to_value_list:\n{data_list[:5]}')  # デバッグ: to_value_list後のデータ確認

        data_list = verb_change(data_list)
        print(f'Data list after verb_change:\n{data_list[:5]}')  # デバッグ: verb_change後のデータ確認

        df = pd.DataFrame(data_list)
        print(f'DataFrame after creating:\n{df.head()}')  # デバッグ: DataFrame作成後のデータ確認

        df = stamp_to_deff_time(df)
        print(f'DataFrame after stamp_to_deff_time:\n{df.head()}')  # デバッグ: stamp_to_deff_time後のデータ確認

        df = stamp_to_ymd(df)
        print(f'DataFrame after stamp_to_ymd:\n{df.head()}')  # デバッグ: stamp_to_ymd後のデータ確認

        print(f"Loaded data for {file_path} successfully")
        return df

    except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        traceback.print_exc()
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

        data = load_data(file_path)
        if not data.empty:
            data_dict[attendance_number] = data

    return data_dict
