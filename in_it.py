import pandas as pd
import os
from data_processing import calculate_counts_and_times

def load_data(file_path):
    print(f'Loading data from: {file_path}')  # デバッグ用
    try:
        data = pd.read_csv(file_path)
        print(data.head())  # デバッグ: データの内容を確認
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

def process_data(data, is_result_data=False):
    if data.empty:
        return {}

    print(f'Raw Data for Processing: {data.head()}')  # デバッグ: 処理前のデータ確認

    if is_result_data:
        # data_result.csvの場合は、openIdとtest_resultの列のみを処理
        processed_data = data[['openId', 'test_result']]
        return processed_data.values.tolist()  # リストとして返す
    else:
        # 通常のcsvファイル処理: verb列があるか確認
        if 'verb' in data.columns:
            # `calculate_counts_and_times` 関数を利用してデータを処理
            processed_data = calculate_counts_and_times(data)
        else:
            # verb列がない場合はエラーを出さず処理をスキップ
            print("Warning: 'verb' column not found, skipping calculation.")
            processed_data = {}

    return processed_data

def prepare_data(directory, result_data):
    data_dict = {}
    for root, dirs, files in os.walk(directory):
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
                    matching_rows = [row for row in result_data if row[0] == attendance_number_int]  # ここを修正
                    print(f'Matching rows for {attendance_number}: {matching_rows}')  # デバッグ: マッチング結果
                    
                    if matching_rows:
                        test_result = matching_rows[0][1]  # 成績を取得
                    else:
                        test_result = None  # 成績が見つからない場合

                    # 出席番号データに成績を追加
                    data['test_result'] = test_result
                    
                    if year not in data_dict:
                        data_dict[year] = {}
                    
                    # データの処理
                    processed_data = process_data(data)

                    # 成績も一緒に保存
                    data_dict[year][attendance_number] = {
                        'processed_data': processed_data,  # 処理されたデータ
                        'test_result': test_result  # 成績
                    }

                    print(f'Processed data for {attendance_number} in {year}: {data_dict[year][attendance_number]}')
    
    return data_dict


def load_result_data(file_path):
    try:
        # 'openId' と 'test_result' のみを読み込む
        result_data = pd.read_csv(file_path, usecols=['openId', 'test_result'])
        return result_data.values.tolist()  # リストとして返す
    except Exception as e:
        print(f"Error loading result data from {file_path}: {e}")
        return []

if __name__ == "__main__":
    directory = 'vi/datas'  # データのディレクトリ
    result_file = os.path.join('vi/results', 'data_result.csv')  # 修正後のファイルパス

    # 成績データを読み込み
    result_data = load_result_data(result_file)  # ここでresult_dataを読み込む

    # データの準備
    calculated_results = prepare_data(directory, result_data)  # result_dataを渡す
    print("Calculation complete. Results:")
    print(calculated_results)
