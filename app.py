import os
import fitz  # PyMuPDF
import re
from collections import Counter
import math

def text_entropy(text):
    """Simple entropy check to measure randomness of text."""
    if not text:
        return 0
    probs = [freq / len(text) for freq in Counter(text).values()]
    return -sum(p * math.log2(p) for p in probs)

def is_text_garbled(text):
    """Heuristic for determining garbled text."""
    if not text or len(text) < 100:
        return True
    lines = text.splitlines()
    avg_line_len = sum(len(line) for line in lines) / len(lines)
    char_entropy = text_entropy(text)
    non_alpha_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)

    return (
        avg_line_len < 20 or
        char_entropy < 3.5 or
        non_alpha_ratio > 0.5 or
        len(re.findall(r'\b\w{20,}\b', text)) > 5  # lots of nonsensical long words
    )

def scan_pdf_for_garbled_ocr(pdf_path):
    """Returns True if PDF appears to contain garbled OCR text."""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                if text and not is_text_garbled(text):
                    return False  # At least one page is readable
        return True
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return True  # Treat unreadable files as garbled

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

# Replace with your Kent directory
kent_pdf_dir = r"C:\Path\To\Kent\PDFs"
garbled = process_folder(kent_pdf_dir)
