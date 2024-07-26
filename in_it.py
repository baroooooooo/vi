import pandas as pd
import json
import os


def load_data(file_path):
    data = pd.read_excel(file_path)
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


def get_file_list(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xlsx'):
                file_paths.append(os.path.join(root, file))
    return file_paths


def load_all_data(file_paths):
    data_dict = {}
    for file_path in file_paths:
        attendance_number = os.path.basename(file_path).split('.')[0]
        data_dict[attendance_number] = load_data(file_path)
    return data_dict
