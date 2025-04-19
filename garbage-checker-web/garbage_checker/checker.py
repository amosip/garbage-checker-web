from collections import Counter
import math
from .config import Config
import fitz  # PyMuPDF
import re

def text_entropy(text):
    if not text:
        return 0
    probs = [freq / len(text) for freq in Counter(text).values()]
    return -sum(p * math.log2(p) for p in probs)

def is_text_garbled(text):
    if not text or len(text) < Config.MIN_TEXT_LENGTH:
        return True
    lines = text.splitlines()
    avg_line_len = sum(len(line) for line in lines) / len(lines)
    char_entropy = text_entropy(text)
    non_alpha_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)

    return (
        avg_line_len < Config.MAX_AVG_LINE_LENGTH or
        char_entropy < Config.MIN_ENTROPY or
        non_alpha_ratio > Config.MAX_NON_ALPHA_RATIO or
        len(re.findall(r'\b\w{20,}\b', text)) > Config.MAX_LONG_WORDS
    )

def scan_pdf_for_garbled_ocr(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                if text and not is_text_garbled(text):
                    return False
        return True
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return True

def process_folder(folder_path):
    garbled_files = []
    total_files = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                total_files += 1
                full_path = os.path.join(root, file)
                if scan_pdf_for_garbled_ocr(full_path):
                    garbled_files.append(full_path)
                    print(f"GARBLED: {full_path}")
    print(f"\n{len(garbled_files)} of {total_files} PDFs appear garbled.")
    return garbled_files