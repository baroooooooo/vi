import pandas as pd
import os
from data_processing import (
    verb_change, stamp_to_deff_time, to_value_list
)
from utils import extract_attendance_number
import chardet
import json

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']

def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            data = pd.read_csv(file)
        
        attendance_number = int(os.path.splitext(os.path.basename(file_path))[0])
        
        data['timeStamp'] = pd.to_datetime(data['timeStamp'], errors='coerce')
        
        data_list = data.values.tolist()
        data_list = to_value_list(data_list)
        data_list = verb_change(data_list)
        
        df = pd.DataFrame(data_list)
        df = stamp_to_deff_time(df)

        df['attendance_number'] = attendance_number

        print(f"Loaded data for {file_path} successfully")
        return df
    except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す

def calculate_answer_time(data):
    launched_times = data[data['verb'] == 1]['timeStamp'].reset_index(drop=True)
    suspended_times = data[data['verb'] == -1]['timeStamp'].reset_index(drop=True)

    if len(launched_times) == len(suspended_times):
        answer_time = (suspended_times - launched_times).sum()
    else:
        answer_time = pd.Timedelta(0)

    return answer_time.total_seconds()

def calculate_submission_count(data):
    # 'verb' 列が 0 の行をカウントする
    submission_count = (data['verb'] == 0).sum()
    return submission_count

def calculate_play_counts(data):
    audio_play_count = data[(data['verb'] == 0) & (data['object'].str.contains('.mp3'))].shape[0]
    video_play_count = data[(data['verb'] == 0) & (data['object'].str.contains('movie'))].shape[0]

    return {
        'audio_start_count': audio_play_count,
        'video_start_count': video_play_count
    }

def calculate_parameters(data):
    answer_time = calculate_answer_time(data)
    submission_count = calculate_submission_count(data)
    play_counts = calculate_play_counts(data)

    return {
        'answer_time': answer_time,
        'submission_count': submission_count,
        **play_counts
    }

def prepare_data(directory):
    calculated_results = {}
    
    for root, dirs, files in os.walk(directory):  # os.walkを使用して再帰的にファイルを探索
        for file_name in files:
            if file_name.endswith('.csv'):
                file_path = os.path.join(root, file_name)  # フルパスを取得
                attendance_number = os.path.splitext(file_name)[0]  # 出席番号をファイル名から抽出
                data = load_data(file_path)
                
                if data.empty:
                    print(f"No data loaded for file: {file_path}")
                    continue
                
                parameters = calculate_parameters(data)
                calculated_results[attendance_number] = parameters
    
    print("Prepared data:", calculated_results)  # デバッグ用
    return calculated_results
