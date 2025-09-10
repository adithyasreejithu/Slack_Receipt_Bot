import os, pathlib
import cv2
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

def process_receipt(receipt, config_setting):

    def gray_scale (img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    img = cv2.imread(receipt)
    str_receipt = str(receipt)
    gray_img = gray_scale(img)

    file_name = str_receipt.split("\\")[1]
    print(file_name)

    # text = pytesseract.image_to_string(img,config=config_setting)
    # print(text)
    # print(len(text))

    # print("----------------")

    # text2 = pytesseract.image_to_string(gray_img,config=config_setting)
    # print(text2)
    # print(len(text2))
    import difflib

    # Texts from pytesseract OCR
    text = pytesseract.image_to_string(img, config=config_setting)
    text2 = pytesseract.image_to_string(gray_img, config=config_setting)

    # Print the actual outputs
  

    # OPTIONAL: If you want side-by-side comparison with some formatting for easier reading:
    print("\nSide-by-Side Comparison:")
    print(f"{'Original':<60} {'Grayscale'}")
    for line1, line2 in zip(text.splitlines(), text2.splitlines()):
        print(f"{line1:<60} {line2}")


if __name__ == "__main__":
    load_dotenv()
    download_loc = os.environ["DOWNLOAD_LOC"]
    download_dir = pathlib.Path(download_loc)

    receipts = gather_picture_files(download_dir)

    for receipt in receipts:
        process_receipt(receipt, CONFIG1)



