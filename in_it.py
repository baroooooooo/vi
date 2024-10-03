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
    
def load_result_data(directory):
    result_data = []
    for root, dirs, files in os.walk(directory):  # resultsディレクトリを再帰的に探索
        for file in files:
            if file.endswith('.csv'):  # CSVファイルをチェック
                file_path = os.path.join(root, file)
                print(f'Loading result data from: {file_path}')  # デバッグ用
                try:
                    # openIdとtest_resultのみを読み込む
                    data = pd.read_csv(file_path, usecols=['openId', 'test_result'])
                    print(data.head())  # デバッグ: 読み込んだデータを表示
                    print(data.dtypes)  # デバッグ: データ型を表示
                    result_data.extend(data.values.tolist())  # リストに追加
                except Exception as e:
                    print(f"Error loading result data from {file_path}: {e}")

    # 読み込んだresult_dataの内容を出力
    print(f'Loaded result_data: {result_data}')  # デバッグ: result_dataの内容を表示
    return result_data


def process_data(data, is_result_data=False):
    if data.empty:
        return {}

    print(f'Raw Data for Processing: {data.head()}')  # デバッグ: 処理前のデータ確認

    if is_result_data:
        # data_result.csvの場合、openIdとtest_resultのみを処理し、他のカラムは無視する
        processed_data = data[['openId', 'test_result']].values.tolist()
        return processed_data  # リストとして返す
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

def prepare_data(data_directory, result_data):  # result_dataを受け取るように修正
    data_dict = {}
    
    # データディレクトリからのデータ処理
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
                    matching_rows = [row for row in result_data if row[0] == attendance_number]  # openIdと比較
                    print(f'Matching rows for {attendance_number}: {matching_rows}')  # デバッグ: マッチング結果
                    
                    if matching_rows:
                        test_result = matching_rows[0][1]  # 成績を取得
                    else:
                        test_result = None  # 成績が見つからない場合

                    # 出席番号に対する成績を保持
                    if year not in data_dict:
                        data_dict[year] = {}

                    data_dict[year][attendance_number] = {
                        'test_result': test_result  # 成績のみ保存
                    }

                    print(f'Processed data for {attendance_number} in {year}: {data_dict[year][attendance_number]}')
    
    return data_dict



if __name__ == "__main__":
    data_directory = 'C:\\Users\\Syachi\\vi\\datas'  # データのディレクトリ
    result_directory = 'C:\\Users\\Syachi\\vi\\results'  # 結果のディレクトリ

    # 成績データを読み込み
    result_data = load_result_data(result_directory)

    # データの準備
    calculated_results = prepare_data(data_directory, result_data)  # result_dataを渡す
    print("Calculation complete. Results:")
    print(calculated_results)
