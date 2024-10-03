import pandas as pd
import os
from data_processing import calculate_counts_and_times

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
    data_result_path = 'C:/Users/Syachi/vi/results/data_result.csv'
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

                    print(f'Processed data for {attendance_number} in {year}: {data_dict[year][attendance_number]}')
                    print(f'Data Dictionary after processing: {data_dict}')  # デバッグ: 最終結果を確認


                else:
                    print(f'No data found for attendance number {attendance_number} in {year}.')  # デバッグ: データが見つからない場合

    return data_dict

if __name__ == "__main__":
    data_directory = 'C:\\Users\\Syachi\\vi\\datas'  # データのディレクトリ
    result_directory = 'C:\\Users\\Syachi\\vi\\results'  # 結果のディレクトリ

    # 成績データを読み込み
    result_data = load_data_result()  # 関数名を修正

    # データの準備
    calculated_results = prepare_data(data_directory, result_data)  # result_dataを渡す
    print("Calculation complete. Results:")  # デバッグ: 処理結果の表示
    print(calculated_results)
