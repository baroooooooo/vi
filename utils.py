import os

def extract_attendance_number(file_name):
    return int(os.path.splitext(os.path.basename(file_name))[0])
