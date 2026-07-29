import os
import creds

def create_file(file_name):
    if not os.path.exists(file_name):
        open(file_name, 'w').close()


def show_history():
    create_file(creds.HISTORY_DOWNLOADS)
    with open(creds.HISTORY_DOWNLOADS, 'r') as file:
        lines = file.readlines()
    for line in lines:
        print(line)

def show_logs():
    create_file(creds.LOGS_FILE)
    with open(creds.LOGS_FILE, 'r', encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()
    for line in lines:
        print(line)