import pandas as pd
import os
from data_processing import calculate_counts_and_times
import json
from datetime import datetime
import pytz

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
        print("Loaded Data:")  # デバッグ: 読み込んだデータの表示
        print(data.head())  
        print(data.dtypes)  # デバッグ: データ型を表示
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
            # `calculate_counts_and_times` 関数を利用してデータを処理
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
                    # result_dataの`openId`と出席番号を比較
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
    data_dict = {}
    all_extracted_data = []

    print(f'Preparing data from directory: {data_directory}')  # デバッグ: ディレクトリの確認

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

                    if year not in data_dict:
                        data_dict[year] = {}
                    data_dict[year][attendance_number] = counts_and_times

                    # フィールドを抽出
                    extracted_data = extract_id_object_timestamp(data, year)

                    # 各データに年と成績を追加
                    for item in extracted_data:
                        item['Year'] = year
                        item['test_result'] = test_result

                   

                    # リストに追加
                    all_extracted_data.extend(extracted_data)
                else:
                    print(f'No data found for attendance number {attendance_number} in {year}.')

    return data_dict, all_extracted_data


def extract_id_object_timestamp(data, year):
    extracted_data = []
    
    for index, row in data.iterrows():
        try:
            # 'actor'フィールドを解析して 'openId' を取得
            try:
                actor_json = json.loads(row['actor'])
                if not isinstance(actor_json, list):
                    print(f"Unexpected actor format for row {index}: {row['actor']}")
                    continue
            except json.JSONDecodeError:
                print(f"Failed to parse actor JSON for row {index}: {row['actor']}")
                continue

            openId = None
            for actor in actor_json:
                if 'openId' in actor:
                    openId = actor['openId']
                    break
            if openId is None:
                openId = 'unknown'

            # 'object'フィールドを解析して 'objectId' を取得
            try:
                object_json = json.loads(row['object'])
                if not isinstance(object_json, list):
                    print(f"Unexpected object format for row {index}: {row['object']}")
                    continue
            except json.JSONDecodeError:
                print(f"Failed to parse object JSON for row {index}: {row['object']}")
                continue

            objectId = None
            for obj in object_json:
                if 'objectId' in obj:
                    objectId = obj['objectId']
                    break

            if objectId is None:
                continue

            # 'objectId'からUnitタイプと番号を解析
            unit_type, unit_number = parse_objectId(objectId)
            
            if unit_type is None or unit_number is None:
                continue

            # 'timeStamp'を解析
            timeStamp_str = row['timeStamp']
            timeStamp = parse_timeStamp(timeStamp_str)
            if timeStamp is None:
                continue

            # 年月日のみを抽出 (年は無視)
            date_only = timeStamp.strftime('%Y-%m-%d')

            # 抽出したデータを追加、優先するのは元のYear
            extracted_data.append({
                'ID': openId,
                'UnitType': unit_type,
                'UnitNumber': unit_number,
                'timeStamp': timeStamp,
                'date_only': date_only,  # 年月日のみ使用、年は含まない
                'Year': str(year)  # 元のYearを優先
            })
        except Exception as e:
            print(f"行 {index} の処理中にエラーが発生しました: {e}")
            continue

    return extracted_data







def parse_objectId(objectId):
    """
    'objectId' から 'MainUnit' または 'BasicUnit' とその番号を解析し、返す。
    例:
    'kototomo/BasicUnit/2/basic_pronunciation/2' -> ('BasicUnit', '2')
    'kototomo/MainUnit/1/listening/6/01-6.mp3' -> ('MainUnit', '1')
    """
    try:
        parts = objectId.split('/')  # '/' で分割

        # 必要な情報が含まれていない場合、エントリを無視
        if len(parts) < 3:
            # 必要な形式（例: 'kototomo/MainUnit/9'）を満たさないものは無視
            return None, None

        # フォーマットに基づいてユニットタイプと番号を取得
        if 'MainUnit' in parts[1] or 'BasicUnit' in parts[1]:
            unit_type = parts[1]
            unit_number = parts[2] if parts[2].isdigit() else None  # ユニット番号が数値であることを確認

            if unit_number is None:
                # ユニット番号が不正（数値でない）の場合は無視
                return None, None

            return unit_type, unit_number
        else:
            # ユニットタイプが不明の場合も無視
            return None, None

    except Exception as e:
        print(f"Error parsing objectId {objectId}: {e}")
        return None, None






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
