import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
import imagehash
from datetime import datetime
from dateutil import parser

# --- TESSERACT CONFIGURATION ---
# If you uncommented this in test_setup.py, UNCOMMENT IT HERE TOO:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """
    Reads image, converts to grayscale, applies thresholding for better OCR.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Denoising and thresholding to make text pop against background
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return gray, thresh

def extract_text(image_path):
    """
    Uses Tesseract to extract raw text from the processed image.
    """
    gray, thresh = preprocess_image(image_path)
    # --oem 3: Default engine mode, --psm 6: Assume a single uniform block of text
    custom_config = r'--oem 3 --psm 6' 
    text = pytesseract.image_to_string(thresh, config=custom_config)
    return text

def parse_receipt_data(text):
    """
    Parses raw text to find Date, Amount, Merchant, and Category.
    """
    data = {
        "merchant": "Unknown Merchant",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": 0.0,
        "currency": "INR", 
        "category": "Other"
    }

    lines = text.split('\n')
    
    # 1. Extract Amount (looks for numbers like 1,200.00 or 50.00)
    amount_pattern = r'[\$\€\₹]?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
    amounts = []
    
    for line in lines:
        match = re.search(amount_pattern, line)
        if match:
            try:
                # Remove commas to convert to float
                amt = float(match.group(1).replace(',', ''))
                amounts.append(amt)
            except:
                continue
    
    if amounts:
        # We assume the total is usually the largest number found
        data["amount"] = max(amounts)

    # 2. Extract Date
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    match_date = re.search(date_pattern, text)
    if match_date:
        try:
            dt = parser.parse(match_date.group(0))
            data["date"] = dt.strftime("%Y-%m-%d")
        except:
            pass

    # 3. Simple Merchant Logic (Take the first non-numeric line as merchant name)
    for line in lines:
        clean_line = line.strip()
        if len(clean_line) > 3 and not re.search(r'\d', clean_line):
            data["merchant"] = clean_line
            break

    # 4. Keyword based categorization
    text_lower = text.lower()
    if any(x in text_lower for x in ['food', 'restaurant', 'burger', 'coffee', 'cafe']):
        data["category"] = "Food"
    elif any(x in text_lower for x in ['uber', 'ola', 'fuel', 'petrol', 'parking']):
        data["category"] = "Travel"
    elif any(x in text_lower for x in ['mart', 'grocer', 'supermarket', 'milk']):
        data["category"] = "Groceries"
    
    return data

def get_image_hash(image_path):
    """ Generates a perceptual hash for duplicate detection. """
    img = Image.open(image_path)
    return str(imagehash.phash(img))

def check_duplicate_image(current_hash, existing_hashes):
    """ Compares current image hash with database hashes. """
    curr = imagehash.hex_to_hash(current_hash)
    for db_hash_str, db_id in existing_hashes:
        if db_hash_str:
            db_hash = imagehash.hex_to_hash(db_hash_str)
            # If images are very similar (Hamming distance < 5)
            if curr - db_hash < 5: 
                return True, db_id
    return False, None