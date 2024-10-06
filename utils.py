import os

def extract_attendance_number(file_name):
    return int(os.path.splitext(os.path.basename(file_name))[0])


# スクリプト内で環境変数を設定
# C:\\Users\\bbaro\\vi\\datas C:\\Users\\bbaro\\vi\\results自宅
# C:\\Users\\Syachi\\vi\\datas C:\\Users\\Syachi\\vi\\results学校
os.environ['DATA_DIRECTORY'] = 'C:\\Users\\bbaro\\vi\\datas'
os.environ['RESULT_DIRECTORY'] = 'C:\\Users\\bbaro\\vi\\results'

# 環境変数からディレクトリパスを取得し、設定されていない場合はデフォルトパスを使用
data_directory = os.environ.get('DATA_DIRECTORY', 'C:\\Users\\bbaro\\vi\\datas')
result_directory = os.environ.get('RESULT_DIRECTORY', 'C:\\Users\\bbaro\\vi\\results')
