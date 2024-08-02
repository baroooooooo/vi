import pandas as pd
import json
import os
import traceback
from data_processing import (
    verb_change, stamp_to_ymd, stamp_to_deff_time, to_value_list
)
from utils import extract_attendance_number
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']



def load_data(file_path):
   print(f'Loading data from: {file_path}')  # デバッグ用
   try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            data = pd.read_csv(file)
        
        # 出席番号がファイル名に含まれているため、ファイル名から出席番号を抽出してデータに追加
        attendance_number = int(os.path.splitext(os.path.basename(file_path))[0])
        data['attendance_number'] = attendance_number

        # JSONパース処理
        if 'actor' in data.columns and data['actor'].str.startswith('[').any():
            data['actor'] = data['actor'].apply(lambda x: json.loads(x)[0]['openId'])
        if 'object' in data.columns and data['object'].str.startswith('[').any():
            data['object'] = data['object'].apply(lambda x: json.loads(x)[0]['objectId'])
        if 'verb' in data.columns and data['verb'].str.startswith('[').any():
            data['verb'] = data['verb'].apply(lambda x: json.loads(x)[0]['display'])
        if 'extension' in data.columns and data['extension'].str.startswith('[').any():
            data['extension'] = data['extension'].apply(lambda x: json.loads(x)[0]['deviceId'])
        
        data['timeStamp'] = pd.to_datetime(data['timeStamp'], errors='coerce')
        attendance_number = extract_attendance_number(file_path)
        data['attendance_number'] = attendance_number
        
        return data
   except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す

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
        print(df.columns)

   
def get_file_list(directory):
    file_paths = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f'Found file: {file_path}')  # デバッグ用
                file_paths.append(file_path)

    return file_paths

def sort_by_attendance_number(data_dict):
    # 出席番号をキーにして昇順に並べ替える
    sorted_data_dict = dict(sorted(data_dict.items(), key=lambda item: int(item[0])))
    return sorted_data_dict

def load_all_data(file_paths):
    data_dict = {}
    for file_path in file_paths:
        attendance_number = extract_attendance_number(file_path)
        print(f'Loading file: {file_path} for ID: {attendance_number}')
        data = load_data(file_path)
        if not data.empty:
            data_dict[attendance_number] = data
    print("Loaded data_dict:", data_dict)  # デバッグ用
    return data_dict
