import os

def extract_attendance_number(file_name):
    """ファイル名から出席番号を抽出する関数"""
    return int(os.path.splitext(os.path.basename(file_name))[0])