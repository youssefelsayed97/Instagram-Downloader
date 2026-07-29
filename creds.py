from datetime import datetime

ERROR_MSG = "Instagram detected suspicious activity. Open Instagram in your browser, " \
            "complete the checkpoint challenge, then rerun the script."


TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


LOGS_FILE = "app.log"
HISTORY_DOWNLOADS = 'History Downloads.txt'
BASE_PATH = "Instagramers"
FILE_PATH = 'TARGET_USERNAMES.json'
