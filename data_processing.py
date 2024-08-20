import pandas as pd
import json

COLUMNS = ['actor', 'timeStamp', 'object', 'result', 'verb', 'extension']

def verb_change(data_list):
    VERB_COLUMN = 'verb'
    delete_line = []

    for i, record in enumerate(data_list):
        if not isinstance(record, dict):
            print(f"Skipping record {i}: not a dictionary")
            delete_line.append(i)
            continue
        
        if 'timeStamp' not in record:
            print(f"Skipping record {i}: 'timeStamp' not in record")
            delete_line.append(i)
            continue
        
        try:
            verb_content = record[VERB_COLUMN]
            if verb_content.startswith('{') or verb_content.startswith('['):
                verb_data = json.loads(verb_content)
                if isinstance(verb_data, list) and len(verb_data) > 0 and 'display' in verb_data[0]:
                    display_value = verb_data[0]['display']
                else:
                    delete_line.append(i)
                    continue
            else:
                display_value = verb_content

            if display_value.startswith('launched') or display_value.startswith('started'):
                record[VERB_COLUMN] = 1
            elif display_value.startswith('finished') or display_value.startswith('moved'):
                record[VERB_COLUMN] = 0
            elif display_value.startswith('suspended') or display_value.startswith('completed'):
                record[VERB_COLUMN] = -1
            else:
                delete_line.append(i)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError for record {i}: {e}")
            delete_line.append(i)
        except (KeyError, IndexError) as e:
            print(f"Error processing record {i}: {e}")
            delete_line.append(i)

    for d in sorted(delete_line, reverse=True):
        data_list.pop(d)

    return data_list

def to_value_list(data):
    if len(data[0]) != len(COLUMNS):
        raise Exception('Invalid columns length')
    seikei_list = []
    for row in data:
        row_dict = dict(zip(COLUMNS, row))
        seikei_list.append(row_dict)
    return seikei_list



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
        'video_time': video_time
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
