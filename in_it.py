import pandas as pd
import os
from data_processing import calculate_counts_and_times
import json
from datetime import datetime
import pytz
import random
import csv

# スクリプト内で環境変数を設定
# C:\\Users\\bbaro\\vi\\datas C:\\Users\\bbaro\\vi\\results自宅
# C:\\Users\\Syachi\\vi\\datas C:\\Users\\Syachi\\vi\\results学校
os.environ['DATA_DIRECTORY'] = 'C:\\Users\\Syachi\\vi\\datas'
os.environ['RESULT_DIRECTORY'] = 'C:\\Users\\Syachi\\vi\\results'

# 環境変数からディレクトリパスを取得し、設定されていない場合はデフォルトパスを使用
data_directory = os.environ.get('DATA_DIRECTORY', 'C:\\Users\\Syachi\\vi\\datas')
result_directory = os.environ.get('RESULT_DIRECTORY', 'C:\\Users\\Syachi\\vi\\results')
global all_extracted_data
def load_data(file_path):
    
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        data = pd.read_csv(file_path)
        
        return data
    except pd.errors.EmptyDataError:
        print(f"No data found in file: {file_path}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        print(f"Parsing error in file: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す

def load_data_result():
    data_result_path = 'C:\\Users\\Syachi\\vi\\results\\data_result.csv'
    try:
        data_result = pd.read_csv(data_result_path)
        print("Loaded result_data:", data_result.head())  # 読み込んだデータを確認
        return data_result
    except Exception as e:
        print(f"Error loading data_result.csv: {e}")
        return pd.DataFrame()  # 読み込み失敗時は空の DataFrame を返す


def process_data(data, is_result_data=False):
    if data.empty:
        return {}

    print(f'Raw Data for Processing: {data.head()}')  # デバッグ: 処理前のデータ確認

    if is_result_data:
        # data_result.csvの場合、openIdとtest_resultのみを処理し、他のカラムは無視する
        processed_data = data[['openId', 'test_result']].values.tolist()
        print(f'Processed Result Data: {processed_data}')  # デバッグ: 処理結果を表示
        return processed_data  # リストとして返す
    else:
        # 通常のcsvファイル処理: verb列があるか確認
        if 'verb' in data.columns:
            # calculate_counts_and_times 関数を利用してデータを処理
            processed_data = calculate_counts_and_times(data)
            print(f'Processed Data Counts and Times: {processed_data}')  # デバッグ: 処理結果を表示
        else:
            # verb列がない場合はエラーを出さず処理をスキップ
            print("Warning: 'verb' column not found, skipping calculation.")
            processed_data = {}

    return processed_data

def prepare_data(data_directory, result_data):
    data_dict = {}
    print(f'Preparing data from directory: {data_directory}')  # デバッグ: ディレクトリの確認

    for root, dirs, files in os.walk(data_directory):  # 指定したディレクトリを再帰的に探索
        for file in files:
            if file.endswith('.csv') and file != 'data_result.csv':  # 'data_result.csv'を除外
                year = os.path.basename(root)  # フォルダ名から年を取得
                file_path = os.path.join(root, file)
                attendance_number = os.path.splitext(file)[0]  # 出席番号取得
                print(f'Loading file: {file_path} for ID: {attendance_number}, Year: {year}')

                # 出席番号のデータを読み込む
                data = load_data(file_path)
                if not data.empty:
                    # result_dataのopenIdと出席番号を比較
                    attendance_number_int = int(attendance_number)  # 出席番号を整数に変換
                    matching_rows = result_data[result_data['openId'] == attendance_number_int]

                    print(f'Matching rows for {attendance_number}: {matching_rows}')  # デバッグ: マッチング結果

                    if not matching_rows.empty:
                        test_result = matching_rows.iloc[0]['test_result']  # 成績を取得
                    else:
                        test_result = None  # 成績が見つからない場合

                    # 出席番号に対する成績を保持
                    if year not in data_dict:
                        data_dict[year] = {}

                    # カウントを計算
                    counts_and_times = calculate_counts_and_times(data)  # カウントを計算
                    counts_and_times['test_result'] = test_result  # テスト結果を追加

                    data_dict[year][attendance_number] = counts_and_times  # 結果を格納

                    


                else:
                    print(f'No data found for attendance number {attendance_number} in {year}.')  # デバッグ: データが見つからない場合

    return data_dict

def prepare_and_collect_data(data_directory, result_data):
    """
    データディレクトリからデータを収集し、classId を含めて集計。
    """
    data_dict = {}
    all_extracted_data = []

    print(f'Preparing data from directory: {data_directory}')  # デバッグ用メッセージ

    for root, dirs, files in os.walk(data_directory):
        year = os.path.basename(root)  # ディレクトリ名から年を取得
        for file in files:
            if file.endswith('.csv') and file != 'data_result.csv':  # 'data_result.csv'を除外
                file_path = os.path.join(root, file)
                attendance_number = os.path.splitext(file)[0]

                print(f'Loading file: {file_path} for ID: {attendance_number}, Year: {year}')

                # 出席番号のデータを読み込む
                data = load_data(file_path)
                if not data.empty:
                    # 結果データから成績を取得
                    attendance_number_int = int(attendance_number)
                    matching_rows = result_data[result_data['openId'] == attendance_number_int]
                    test_result = matching_rows.iloc[0]['test_result'] if not matching_rows.empty else None

                    # カウントを計算
                    counts_and_times = calculate_counts_and_times(data)
                    counts_and_times['test_result'] = test_result

                    # classId を抽出してカウントデータに追加
                    data['classId'] = data['extension'].apply(extract_class_id)
                    counts_and_times['classId'] = data['classId'].mode().iloc[0] if not data['classId'].isnull().all() else None

                    if year not in data_dict:
                        data_dict[year] = {}
                    data_dict[year][attendance_number] = counts_and_times

                    # フィールドを抽出
                    extracted_data = extract_id_object_timestamp(data, year)

                    # 各データに年、成績、クラスIDを追加
                    for item in extracted_data:
                        item['Year'] = year
                        item['test_result'] = test_result
                        item['classId'] = counts_and_times['classId']

                    # リストに追加
                    all_extracted_data.extend(extracted_data)
                else:
                    print(f'No data found for attendance number {attendance_number} in {year}.')

    return data_dict, all_extracted_data

def extract_class_id(extension_str):
    """
    'extension' フィールドから 'classId' を抽出。
    """
    try:
        extension_data = json.loads(extension_str)
        if isinstance(extension_data, list):
            return extension_data[0].get("classId", None)  # リストの場合は最初の要素から取得
        elif isinstance(extension_data, dict):
            return extension_data.get("classId", None)  # 辞書の場合は直接取得
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None  # エラー時は None を返す


def parse_objectId(objectId):
    """
    'objectId' から 'MainUnit' または 'BasicUnit' とその番号を解析し、
    grammar, pronunciation, speaking, listening を判定して返す。
    """
    try:
        parts = objectId.split('/')  # '/' で分割

        # 必要な情報が含まれていない場合、エントリを無視
        if len(parts) < 3:
            return None, None, None

        # フォーマットに基づいてユニットタイプと番号を取得
        unit_type = None
        unit_number = None
        activity_type = None

        if 'MainUnit' in parts[1] or 'BasicUnit' in parts[1]:
            unit_type = parts[1]
            unit_number = parts[2] if parts[2].isdigit() else None  # ユニット番号が数値であることを確認

            # grammar, pronunciation, speaking, listening を判定
            for keyword in ['grammar', 'pronunciation', 'speaking', 'listening']:
                if keyword in objectId:
                    activity_type = keyword
                    break

        # 必須情報が欠けている場合は無効
        if not unit_type or not unit_number:
            return None, None, None

        return unit_type, unit_number, activity_type

    except Exception as e:
        print(f"Error parsing objectId {objectId}: {e}")
        return None, None, None


def extract_id_object_timestamp(data, year):
    extracted_data = []

    for index, row in data.iterrows():
        try:
            # 'actor'フィールドを解析して 'openId' を取得
            actor_json = json.loads(row['actor'])
            openId = actor_json[0].get('openId', 'unknown') if isinstance(actor_json, list) else 'unknown'

            # 'objectId'を解析
            object_json = json.loads(row['object'])
            objectId = object_json[0].get('objectId') if isinstance(object_json, list) else None
            if objectId is None:
                continue

            # 'objectId'からUnitタイプ、番号、およびアクティビティタイプを解析
            unit_type, unit_number, activity_type = parse_objectId(objectId)
            if unit_type is None or unit_number is None:
                continue

            # 'timeStamp'を解析
            timeStamp = parse_timeStamp(row['timeStamp'])
            if timeStamp is None:
                continue

            # 年月日のみを抽出
            date_only = timeStamp.strftime('%Y-%m-%d')

            # 'extension' フィールドから 'classId' を抽出
            classId = extract_class_id(row.get('extension', '{}'))

            # データを追加
            extracted_data.append({
                'ID': openId,
                'UnitType': unit_type,
                'UnitNumber': unit_number,
                'ActivityType': activity_type,
                'timeStamp': timeStamp,
                'date_only': date_only,
                'Year': str(year),
                'classId': classId,
                'objectId': objectId
            })
        except Exception as e:
            print(f"行 {index} の処理中にエラーが発生しました: {e}")
            continue

    # データを時系列順に並べ替え
    sorted_data = sorted(extracted_data, key=lambda x: x['timeStamp'])

    # 全体順序を記録
    for i, entry in enumerate(sorted_data):
        entry['sequence_global'] = i + 1  # 全体順序

    # 形式別順序を記録
    activity_groups = {}
    for entry in sorted_data:
        activity_groups.setdefault(entry['ActivityType'], []).append(entry)

    for activity, entries in activity_groups.items():
        for i, entry in enumerate(entries):
            entry['sequence_activity'] = i + 1  # 形式別順序

    return sorted_data









def parse_timeStamp(timeStamp_str):
    from dateutil import parser
    try:
        return parser.isoparse(timeStamp_str)
    except parser.ParserError:
        try:
            return pd.to_datetime(timeStamp_str)  # フォールバックの処理
        except Exception as e:
            print(f"Error parsing timeStamp {timeStamp_str}: {e}")
            return None
        

def is_within_academic_year(timeStamp, academic_year):
    """
    学年度内にあるかを確認します。
    例: 2018年度なら 2018年4月1日 から 2019年3月31日まで
    """
    tz = pytz.utc  # タイムゾーンを統一
    start_date = tz.localize(datetime(int(academic_year), 4, 1))  # 学年度開始日
    end_date = tz.localize(datetime(int(academic_year) + 1, 3, 31))  # 学年度終了日
    
    # timeStampが学年度の範囲内かどうか確認
    return start_date <= timeStamp <= end_date




def save_random_data_to_csv(data_dict, num_students=5, file_name="random_students_data.csv"):
    # データをフラットなリストに変換
    flat_data = []
    for year, students in data_dict.items():
        for student_id, data in students.items():
            flat_data.append({
                '学生ID': student_id,
                '総学習時間(s)': data.get('total_answer_time', 0),
                '動画再生時間(s)': data.get('video_time', 0),
                '問題への回答数': data.get('answer_count', 0),
                '成績': data.get('test_result', 0),
                '録音回数': data.get('recorder_start_count', 0)
            })
    
    print(f"データ数: {len(flat_data)}")  # デバッグ用メッセージ

    # ランダムに5人分のデータを抽出
    random_data = random.sample(flat_data, min(num_students, len(flat_data)))
    print(f"ランダム抽出データ: {random_data}")  # デバッグ用メッセージ
    
    # CSVに保存
    headers = ['学生ID', '総学習時間(s)', '動画再生時間(s)', '問題への回答数', '成績', '録音回数']
    
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(random_data)
    
    print(f"{num_students}人分のデータを {file_name} に保存しました。")





if __name__ == "__main__":
    os.environ['DATA_DIRECTORY'] = 'C:\\Users\\Syachi\\vi\\datas'
    os.environ['RESULT_DIRECTORY'] = 'C:\\Users\\Syachi\vi\\results'

    # 環境変数からディレクトリパスを取得し、設定されていない場合はデフォルトパスを使用
    data_directory = os.environ.get('DATA_DIRECTORY', 'C:\\Users\\Syachi\\vi\\datas')
    result_directory = os.environ.get('RESULT_DIRECTORY', 'C:\\Users\\Syachi\\vi\\results')


    # 成績データを読み込み
    result_data = load_data_result()  # 関数名を修正

    # データの準備
    calculated_results, all_extracted_data = prepare_and_collect_data(data_directory, result_data)
    # result_dataを渡す
   
    

    print("Calculation complete. Results:")  # デバッグ: 処理結果の表示
    print(calculated_results)