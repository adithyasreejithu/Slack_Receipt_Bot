# First fix image downloader
#     - check what files have been read - completed
#     - convert files into jpeg
#     - add error handling to make sure files can be read
#
# Work on setting up the first file reading
#     - create app.py with output screen
#     - add error handling
#
# Finally fix image reader

from slack_receipt_downloader import channel_history, format_excel_output
# from receipt_processing import receipt_ocr_pipline
from receipt_ocr import ocr_pipeline
import os
from dotenv import load_dotenv


load_dotenv()  # Load env variables from .env
CHANNEL_ID = os.environ["CHANNEL_ID"]

def run_downloader():
    channel_history(CHANNEL_ID)
    format_excel_output()

def run_ocr():
    # receipt_ocr_pipline()
    ocr_pipeline()

print("- - - - - SLACK API RECEIPT DOWNLOADER - - - - -")
run_downloader()
run_ocr()