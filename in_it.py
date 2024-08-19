import pandas as pd
import os
import json

def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    data_dict = {'timeStamp': [], 'verb': [], 'object': [], 'attendance_number': None}

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            data = pd.read_csv(file)
        
        data_dict['attendance_number'] = int(os.path.splitext(os.path.basename(file_path))[0])
        data_dict['timeStamp'] = pd.to_datetime(data['timeStamp'], errors='coerce').tolist()
        data_dict['verb'] = data['verb'].tolist()
        data_dict['object'] = data['object'].tolist()

        print(f"Loaded data for {file_path} successfully")
        print(f"Sample data: {data_dict['timeStamp'][:5]}")  # デバッグ用
        print(f"Verb column values: {pd.Series(data_dict['verb']).value_counts()}")  # デバッグ用
        return data_dict
    except Exception as e:
        print(f'Error loading data from {file_path}: {e}')
        return None  # エラーが発生した場合はNoneを返す

def calculate_submission_count(verbs):
    submission_count = 0
    for i, verb in enumerate(verbs):
        try:
            verb_json = json.loads(verb)
            if 'submitted' in verb_json[0].get('display', ''):
                submission_count += 1
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error processing verb at index {i}: {e}")
            print(f"Offending data: {verb}")  # 問題のデータを表示
            continue  # エラーが発生した場合はスキップ
    
    return submission_count
    
    
def calculate_answer_time(verbs, timestamps):
    launched_times = []
    suspended_times = []

    for i, verb in enumerate(verbs):
        try:
            verb_json = json.loads(verb)
            if verb_json and verb_json[0].get('display', '') == 'launched':
                launched_times.append(timestamps[i])
            elif verb_json and verb_json[0].get('display', '') == 'suspended':
                suspended_times.append(timestamps[i])
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error processing verb at index {i}: {e}")
            continue  # エラーが発生した場合はスキップ

    if len(launched_times) != len(suspended_times):
        print("Warning: Mismatch in launched and suspended times length.")

    total_answer_time = 0
    for i in range(min(len(launched_times), len(suspended_times))):
        start_time = launched_times[i]
        end_time = suspended_times[i]
        duration = (end_time - start_time).total_seconds()
        total_answer_time += duration

    return total_answer_time

  


def calculate_play_counts(object_list):
    audio_play_count = sum(
        1 for obj in object_list
        if any('.mp3' in o.get('objectId', '') for o in json.loads(obj))
    )
    video_play_count = sum(
        1 for obj in object_list
        if any('movie' in o.get('objectId', '') for o in json.loads(obj))
    )

    return {
        'audio_start_count': audio_play_count,
        'video_start_count': video_play_count
    }

def calculate_parameters(data_dict):
    results = {}

    for attendance_number, data in data_dict.items():
        # 各データのカウントなどをここで行う
        answer_time = calculate_answer_time(data['verb'], data['timeStamp'])  # ここで両方の引数を渡す
        submission_count = calculate_submission_count(data['verb'])
        play_counts = calculate_play_counts(data['object'])

        results[attendance_number] = {
            'answer_time': answer_time,
            'submission_count': submission_count,
            'play_counts': play_counts
        }
    
    return results


def prepare_data(directory):
    file_paths = get_file_list(directory)
    data_dict = load_all_data(file_paths)
    calculated_results = calculate_parameters(data_dict)
    return calculated_results

# ここで get_file_list と load_all_data 関数を定義
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
        if data:  # dataがNoneでないことを確認
            data_dict[attendance_number] = data
    return data_dict
