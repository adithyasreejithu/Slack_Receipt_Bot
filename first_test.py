import os, pathlib
import cv2
import re
import numpy as np
import pytesseract
from dotenv import load_dotenv

# in the future this could be a dict and I could loop to run both
CONFIG1 = r"--oem 3 --psm 6"
CONFIG2 = r"--oem 1 --psm 6"

def gather_picture_files(dir: pathlib.Path):
    receipt_list = []

    for file in dir.iterdir():
        receipt_list.append(file)

    return receipt_list

#dataclass
def process_receipt(receipt, config_setting):

    def gray_scale (img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def extract_text(text: str):
        purchase_Date = ""
        supplier = ""
        cost = ""

        date_pattern_1 = r"\d{2}-[A-Z]{3}-\d{4}"


        for i, line in enumerate(text.splitlines()):  
            if i == 0:
                supplier = line
            elif "Total" in line:
                cost = line
        
            match = re.search(date_pattern_1, line, re.IGNORECASE)

            if match:
                purchase_Date = match.group(0)  # full matched string
                break


        print(f"Supplier: {supplier} \nTotal: {cost} \nPurchase_date: {purchase_Date}")
        return [purchase_Date, supplier, cost]
    
    img = cv2.imread(receipt)
    str_receipt = str(receipt)
    gray_img = gray_scale(img)

    basic_text = pytesseract.image_to_string(gray_img ,config=config_setting)

    file_name = str_receipt.split("\\")[1]
    print(file_name)

    return extract_text(basic_text)

    
   

if __name__ == "__main__":
    load_dotenv()
    download_loc = os.environ["DOWNLOAD_LOC"]
    download_dir = pathlib.Path(download_loc)

    receipts = gather_picture_files(download_dir)
    
    receipt_text = {}

    for receipt in receipts:
        output = process_receipt(receipt, CONFIG1)
        receipt_text[receipt] = {
            "Purchase_Date": output[0],
            "Supplier": output[1],
            "Cost": output[2]
        }





