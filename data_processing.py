import pandas as pd
import json
# 定義
COLUMNS = ['actor', 'timeStamp', 'object', 'result', 'verb', 'extension']

RESULT_COLUMNS = ['duration', 'position', 'completion', 'questionId', 'success', 'continue']


# display内の行動を1,0,-1のように数値で分類

def sort_by_attendance_number(data_dict):
    # 出席番号をキーにして昇順に並べ替える
    sorted_data_dict = dict(sorted(data_dict.items(), key=lambda item: int(item[0])))
    return sorted_data_dict


def verb_change(data_list):
    VERB_COLUMN = 'verb'  # 'verb' 列にアクセスするためのキー名

    delete_line = []

    for i, record in enumerate(data_list):
        if 'timeStamp' not in record:
            print(f"Record {i} is missing 'timeStamp'.")
            delete_line.append(i)
            continue

        try:
            verb_content = record[VERB_COLUMN]
            
            
            # verbがJSON形式であるかを確認
            if verb_content.startswith('{') or verb_content.startswith('['):
                verb_data = json.loads(verb_content)
                if isinstance(verb_data, list) and len(verb_data) > 0 and 'display' in verb_data[0]:
                    display_value = verb_data[0]['display']
                else:
                    delete_line.append(i)
                    continue
            else:
                # プレーンテキストの場合はそのまま使用
                display_value = verb_content
            
            # 開始系
            if display_value.startswith('launched') or \
                    display_value.startswith('started') or \
                    display_value.startswith('resumed') or \
                    display_value.startswith('played'):
                record[VERB_COLUMN] = 1
            # 途中系
            elif display_value.startswith('finished') or \
                    display_value.startswith('moved') or \
                    display_value.startswith('selected') or \
                    display_value.startswith('opened') or \
                    display_value.startswith('closed') or \
                    display_value.startswith('submitted') or \
                    display_value.startswith('paused'):
                record[VERB_COLUMN] = 0
            # 終了系
            elif display_value.startswith('suspended') or \
                    display_value.startswith('completed') or \
                    display_value.startswith('terminated'):
                record[VERB_COLUMN] = -1
            else:
                delete_line.append(i)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError processing row {i}: {e}")
            delete_line.append(i)
        except (KeyError, IndexError) as e:
            print(f"Error processing row {i}: {e}")
            delete_line.append(i)

    print(f"Rows to delete: {delete_line}")  # デバッグ: 削除対象の行を表示
    print(f"Data before deletion:\n{data_list[:5]}")  # デバッグ: 削除前のデータを表示
    # 後ろから削除
    for d in sorted(delete_line, reverse=True):
        data_list.pop(d)

    print(f"Data after verb_change:\n{data_list[:5]}")  # デバッグ: 処理後のデータを表示
    return data_list




# timeStampをリストに直して、関数からyear,hour,minute,secondに分類
def stamp_to_ymd(df):
    df['timeStamp'] = pd.to_datetime(df['timeStamp'])
    df['year'] = df['timeStamp'].dt.year
    df['month'] = df['timeStamp'].dt.month
    df['day'] = df['timeStamp'].dt.day
    df['hour'] = df['timeStamp'].dt.hour
    df['minute'] = df['timeStamp'].dt.minute
    df['second'] = df['timeStamp'].dt.second
    df['dayofweek'] = df['timeStamp'].dt.dayofweek
    df = df.drop(['timeStamp'], axis=1)
    print(df.columns) 
    return df


def stamp_to_deff_time(df):
    # 'timeStamp'列が存在するか確認
    if 'timeStamp' not in df.columns:
        raise KeyError("'timeStamp' column not found in the data")
    
    try:
        # 'timeStamp'列をdatetime型に変換
        df['timeStamp'] = pd.to_datetime(df['timeStamp'], utc=True)
    except Exception as e:
        raise ValueError(f"Error parsing 'timeStamp' column: {e}")
    
    # 'timeStamp'列が存在し、適切に変換された場合に処理を続行
    df = df.sort_values('timeStamp')
    df['time_diff'] = df['timeStamp'].diff().dt.total_seconds()
    print(f'DataFrame after calculating time_diff:\n{df.head()}')  # デバッグ: time_diff計算後のデータ確認
    
    return df


def compare_number_of_lines(data):
    return len(data[0]) == len(COLUMNS)


def to_value_list(data):
    if not compare_number_of_lines(data):
        print(f"Invalid columns length: expected {len(COLUMNS)}, got {len(data[0])}")
        raise Exception('Invalid columns length')
    seikei_list = []
    for row in data:
        row_dict = dict(zip(COLUMNS, row))
        seikei_list.append(row_dict)
    print(f"Converted list:\n{seikei_list[:5]}")  # デバッグ: 変換後のデータを表示
    return seikei_list



def list_to_dict(RESULT_COLUMNS):
    return {col: 0 for col in RESULT_COLUMNS}


def result_column_split(result_dict, value, column_name):
    result_dict[column_name] = value
    return result_dict


def result_column_split_tf(result_dict, value, column_name):
    if value == 'true':
        result_dict[column_name] = 1
    elif value == 'false':
        result_dict[column_name] = -1
    return result_dict


def switch_two_if(search_word, a, b):
    if search_word in a:
        return b, a
    return a, b
