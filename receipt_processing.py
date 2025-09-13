

import re
import cv2
import os, pathlib

import numpy as np
import pytesseract
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional, Iterable


CONFIG1 = r"--oem 3 --psm 6"
CONFIG2 = r"--oem 1 --psm 6"

DATE_PATTERNS: tuple[re.Pattern,...] = (
    re.compile(r"\d{2}-[A-Z]{3}-\d{4}", re.I),
    re.compile(r"\d{2}-\d{2}-\d{4}"),
    re.compile(r"\d{2}-\d{2}-\d{2}"),
    re.compile(r"\d{2}/\d{2}/\d{4}"),
    re.compile(r"\d{2}/\d{2}/\d{2}"),
)

def gather_picture_files(dir: pathlib.Path):
    receipt_list = []

    for file in dir.iterdir():
        receipt_list.append(file)

    return receipt_list

@dataclass(slots=False)
class ReceiptOCR:
    receipt_path: Path
    config: str = CONFIG1
    
    purchase_date: Optional[str] = field(init=False, default=None)
    supplier: Optional[str] = field(init=False, default=None)
    cost_text : Optional[float] = field(init=False, default=None)
    text: Optional[str] = field(init=False,repr= False, default=None)

    # receipt_path: Path
    # config: str

    # purchase_date: str | None = None
    # supplier: str | None = None
    # cost_text: str | None = None
    # text: str = ""

    def __post_init__(self) -> None:
        try:
            img = cv2.imread(str(self.receipt_path))
        except FileNotFoundError:
            print(f"File not found: {self.receipt_path}")

        processed_img = self._preprocess_grey(img)
        self.text = pytesseract.image_to_string(processed_img, config=self.config)
        self._extract_text(self.text)

    def _preprocess_grey(self, img: np.ndarray) -> np.ndarray:
        # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        den = cv2.medianBlur(grey, 3)
        _, th = cv2.threshold(den, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return th

    def _extract_text(self, text: str) -> None:
        # clean the text - for line in text split and strip trail and return if not empty
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        if lines:
            self.supplier = lines[0]

        for line in lines:

            if "Total" in line.lower():
                amount_pattern = r"\$?\s?\d[\d,]*\.?\d{0,2}"
                match = re.search(amount_pattern, line)
                print(match)

                if match:
                    self.cost_text = match.group(0).replace(" ", "")
                    break

        for line in lines:

            for pattern in DATE_PATTERNS:

                match = pattern.search(line)
                if match:
                    self.purchase_date = match.group(0)
                    break

            if self.purchase_date:
                break

# def process_receipt(receipt: Path, config: str = CONFIG1) -> ReceiptOCR:
#     return ReceiptOCR(receipt_path=receipt, config=config)

def process_receipt(receipt: Path, config: str = CONFIG1) -> ReceiptOCR:
    return ReceiptOCR(receipt_path=receipt, config=config)
if __name__ == "__main__":
    load_dotenv()
    download_dir = Path(os.environ["DOWNLOAD_LOC"])

    receipts = gather_picture_files(download_dir)
    results_con_1 : dict[str, dict[str, Optional[str]]] = {}
    results_con_2 : dict[str, dict[str, Optional[str]]] = {}


    for receipt in receipts:
        rec = process_receipt(receipt, CONFIG1)
        rec2 = process_receipt(receipt, CONFIG2)
        results_con_1[receipt.name] = {
            "Purchase_Date": rec.purchase_date,
            "Supplier": rec.supplier,
            "Cost": rec.cost_text or None,
        }
        results_con_2[receipt.name] = {
            "Purchase_Date": rec2.purchase_date,
            "Supplier": rec2.supplier,
            "Cost": rec2.cost_text or None,
        }

        # quick debug print
    for k, v in results_con_1.items():
        print(k, "→", v)
    print("\n")
    for k, v in results_con_2.items():
        print(k, "→", v)



