import pandas as pd
# 定義
COLUMNS = ['actor', 'object', 'verb', 'extension', 'timeStamp']
RESULT_COLUMNS = ['duration', 'position', 'completion', 'questionId', 'success', 'continue']


# display内の行動を1,0,-1のように数値で分類
def verb_change(data):
    DISPLAY = COLUMNS.index('display')
    delete_line = []
    for i in range(0, len(data)):
        # 開始系
        if data[i][DISPLAY].startswith('launched') or \
                data[i][DISPLAY].startswith('started') or \
                data[i][DISPLAY].startswith('resumed') or \
                data[i][DISPLAY].startswith('played'):
            data[i][DISPLAY] = 1
        # 途中系
        elif data[i][DISPLAY].startswith('finished') or \
                data[i][DISPLAY].startswith('moved') or \
                data[i][DISPLAY].startswith('selected') or \
                data[i][DISPLAY].startswith('opened') or \
                data[i][DISPLAY].startswith('closed') or \
                data[i][DISPLAY].startswith('submitted') or \
                data[i][DISPLAY].startswith('paused'):
            data[i][DISPLAY] = 0
        # 終了系
        elif data[i][DISPLAY].startswith('suspended') or \
                data[i][DISPLAY].startswith('completed') or \
                data[i][DISPLAY].startswith('terminated'):
            data[i][DISPLAY] = -1
        else:
            delete_line.append(i)
    for d in sorted(delete_line, reverse=True):  # 後ろから削除
        data.pop(d)
    return data


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
    return df


def stamp_to_deff_time(df):
    df['timeStamp'] = pd.to_datetime(df['timeStamp'])
    df['btimeStamp'] = df['timeStamp'].shift(1)
    df.at[df.index[0], 'btimeStamp'] = df['timeStamp'].min()
    df['timeDiff'] = df['timeStamp'] - df['btimeStamp']
    df['timeDiff'] = df['timeDiff'].dt.total_seconds()
    df = df.drop(['btimeStamp'], axis=1)
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
