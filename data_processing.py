import pandas as pd
import json

COLUMNS = ['actor', 'timeStamp', 'object', 'result', 'verb', 'extension']

def calculate_counts_and_times(data):
    video_start_count = 0
    audio_start_count = 0
    answer_count = 0
    correct_answers = 0
    incorrect_answers = 0
    suspended_count = 0
    launched_count = 0
    total_answer_time = 0
    recording_time = 0
    video_time = 0
    recorder_start_count = 0 
    movie_completed_count = 0
    continue_count = 0

    for index, row in data.iterrows():
        try:
            verbs = json.loads(row['verb'])
            objects = json.loads(row['object'])
            result = json.loads(row['result']) if pd.notna(row['result']) else None

       

            # 動画再生回数と音声再生回数のカウント
            if any(verb.get('display') == 'played' for verb in verbs):
                for obj in objects:
                    object_id = obj.get('objectId', '')
                    if 'movie' in object_id:
                        video_start_count += 1
                    elif 'mp3' in object_id:
                        audio_start_count += 1

            # 回答回数のカウント
            if any(verb.get('display') == 'submitted' for verb in verbs):
                answer_count += 1
                if isinstance(result, list):
                    for res in result:
                        if 'success' in res:
                            if res.get('success') == True:
                                correct_answers += 1
                            elif res.get('success') == False:
                                incorrect_answers += 1
                elif isinstance(result, dict) and 'success' in result:
                    if result.get('success') == True:
                        correct_answers += 1
                    elif result.get('success') == False:
                        incorrect_answers += 1

            # 中断回数とアプリ起動回数のカウント
            if any(verb.get('display') == 'suspended' for verb in verbs):
                suspended_count += 1
            if any(verb.get('display') == 'launched' for verb in verbs):
                launched_count += 1

            # 解答時間の合計
            if any(verb.get('display') == 'finished' for verb in verbs):
                if isinstance(result, list):
                    for res in result:
                        if 'duration' in res:
                            duration = int(res.get('duration', 0))
                            total_answer_time += duration

            # 録音時間と動画再生時間の合計
            if any(verb.get('display') == 'completed' for verb in verbs):
                if isinstance(result, list):
                    for res in result:
                        if 'duration' in res:
                            duration = int(res.get('duration', 0))
                            if 'recorder' in objects[0].get('objectId', ''):
                                recording_time += duration
                            elif 'movie' in objects[0].get('objectId', ''):
                                video_time += duration
                elif isinstance(result, dict) and 'duration' in result:
                    duration = int(result.get('duration', 0))
                    if 'recorder' in objects[0].get('objectId', ''):
                        recording_time += duration
                    elif 'movie' in objects[0].get('objectId', ''):
                        video_time += duration

            if any(verb.get('display') == 'started' and 'recorder' in obj.get('objectId', '') for verb in verbs for obj in objects):
                recorder_start_count += 1

            if any(verb.get('display') == 'completed' and 'movie' in obj.get('objectId', '') for verb in verbs for obj in objects):
                movie_completed_count += 1

            if any(verb.get('display') == 'moved' for verb in verbs):
                if isinstance(result, dict) and result.get('continue') == True:
                    continue_count += 1
                elif isinstance(result, list):
                    for res in result:
                        if isinstance(res, dict) and res.get('continue') == True:
                            continue_count += 1

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Error processing row {index}: {e}")
            continue

    return {
        'video_start_count': video_start_count,
        'audio_start_count': audio_start_count,
        'answer_count': answer_count,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'suspended_count': suspended_count,
        'launched_count': launched_count,
        'total_answer_time': total_answer_time,
        'recording_time': recording_time,
        'video_time': video_time,
        'recorder_start_count': recorder_start_count,
        'movie_completed_count': movie_completed_count,
        'continue_count': continue_count
    }











def calculate_submission_count(data):
    count = 0
    for _, row in data.iterrows():
        try:
            verbs = json.loads(row['verb'])
            if any(verb.get('display') == 'submitted' for verb in verbs):
                count += 1
        except (json.JSONDecodeError, TypeError):
            continue
    return count

def calculate_answer_time(data):
    total_time = 0
    for _, row in data.iterrows():
        try:
            verbs = json.loads(row['verb'])
            objects = json.loads(row['object'])
            if any(verb.get('display') == 'finished' for verb in verbs):
                for obj in objects:
                    if 'duration' in obj.get('objectId', ''):
                        duration = int(obj.get('objectId').split('duration=')[-1].split(';')[0])
                        total_time += duration
        except (json.JSONDecodeError, TypeError):
            continue
    return total_time

def calculate_play_counts(data):
    video_count = 0
    audio_count = 0
    for _, row in data.iterrows():
        try:
            verbs = json.loads(row['verb'])
            objects = json.loads(row['object'])
            if any(verb.get('display') == 'played' for verb in verbs):
                for obj in objects:
                    object_id = obj.get('objectId', '')
                    if 'movie' in object_id:
                        video_count += 1
                    elif 'mp3' in object_id:
                        audio_count += 1
        except (json.JSONDecodeError, TypeError):
            continue
    return video_count, audio_count

def clean_and_parse_json(data, column):
    cleaned_data = []
    for _, row in data.iterrows():
        try:
            json_data = json.loads(row[column])
            cleaned_data.append(json_data)
        except (json.JSONDecodeError, TypeError):
            continue
    return cleaned_data
