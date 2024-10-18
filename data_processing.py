import pandas as pd
import json
from dateutil import parser
import plotly.graph_objs as go
import os


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
                            total_answer_time = total_answer_time / 3600 # 秒を時間に変換

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
                        recording_time = recording_time / 3600 # 秒を時間に変換
                    elif 'movie' in objects[0].get('objectId', ''):
                        video_time += duration
                        video_time = video_time / 3600 # 秒を時間に変換

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





def create_3d_plot(all_data):
    # 辞書のリストをDataFrameに変換
    df = pd.DataFrame(all_data)

    if df.empty:
        print("プロットするデータがありません。")
        return go.Figure()

    # プロット用のデータを準備
    df['ID'] = df['ID'].astype(str)
    df['Unit'] = df['Unit'].astype(str)

    # 'timeStamp' を datetime に変換し、数値に変換
    try:
        df['timeStamp'] = pd.to_datetime(df['timeStamp'], errors='coerce')  # 無効なデータはNaTにする
        df['timeStamp_numeric'] = df['timeStamp'].astype('int64')  # datetimeを数値に変換
    except Exception as e:
        print(f"Error converting timeStamp: {e}")
        return go.Figure()  # エラー発生時は空のグラフを返す

    # 'Unit' を y軸用の数値にマッピング
    unit_labels = df['Unit'].unique()
    unit_mapping = {unit: idx for idx, unit in enumerate(unit_labels)}
    df['Unit_numeric'] = df['Unit'].map(unit_mapping)

    # 'ID' を x軸用の数値にマッピング
    id_labels = df['ID'].unique()
    id_mapping = {id_: idx for idx, id_ in enumerate(id_labels)}
    df['ID_numeric'] = df['ID'].map(id_mapping)

    # 3D散布図を作成
    fig = go.Figure(data=[go.Scatter3d(
        x=df['ID_numeric'],
        y=df['Unit_numeric'],
        z=df['timeStamp_numeric'],
        mode='markers',
        marker=dict(
            size=5,
            color=df['timeStamp_numeric'],  # timeStampをカラースケールに使用
            colorscale='Viridis',
            opacity=0.8
        ),
        text=[f"ID: {row['ID']}<br>Unit: {row['Unit']}<br>Time: {row['timeStamp']}" for index, row in df.iterrows()],
        hoverinfo='text'
    )])

    # レイアウトを更新
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='ID', tickvals=list(id_mapping.values()), ticktext=list(id_mapping.keys())),
            yaxis=dict(title='Unit', tickvals=list(unit_mapping.values()), ticktext=list(unit_mapping.keys())),
            zaxis=dict(title='Time')
        ),
        margin=dict(r=0, b=0, l=0, t=0),
        title='ID vs Unit vs TimeStamp の3Dプロット'
    )

    return fig


