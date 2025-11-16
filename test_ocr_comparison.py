#!/usr/bin/env python3
"""
Test Alternative OCR Engines
Compares EasyOCR, Tesseract, and other options
"""
import cv2
import numpy as np
import sys
import os

# Test if pytesseract is available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ pytesseract available")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  pytesseract not available")

# Test EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    print("✅ easyocr available")
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  easyocr not available")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_plate():
    """Create test plate image"""
    plate = np.ones((120, 400, 3), dtype=np.uint8) * 255
    plate[0:50, 0:50] = [200, 0, 0]
    plate[110:120, :] = [0, 215, 255]
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(plate, "199TN0199", (50, 80), font, 2.5, (0, 0, 0), 4)
    
    return plate

def test_tesseract(image):
    """Test Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        print("❌ Tesseract not available")
        return
    
    print("\n" + "="*60)
    print("Tesseract OCR")
    print("="*60)
    
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Upscale
        upscaled = cv2.resize(gray, (gray.shape[1]*3, gray.shape[0]*3), interpolation=cv2.INTER_CUBIC)
        
        # Test basic OCR
        text = pytesseract.image_to_string(upscaled)
        print(f"Basic OCR: '{text.strip()}'")
        
        # Test with digits config
        text_digits = pytesseract.image_to_string(upscaled, config='--psm 8 -c tessedit_char_whitelist=0123456789TN')
        print(f"Digits OCR: '{text_digits.strip()}'")
        
        # Test with PSM 6 (uniform block of text)
        text_psm6 = pytesseract.image_to_string(upscaled, config='--psm 6')
        print(f"PSM6 OCR: '{text_psm6.strip()}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_easyocr_advanced(image):
    """Test EasyOCR with advanced settings"""
    if not EASYOCR_AVAILABLE:
        print("❌ EasyOCR not available")
        return
    
    print("\n" + "="*60)
    print("EasyOCR Advanced Tests")
    print("="*60)
    
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        
        # Test 1: Original
        print("\n[Test 1] Original Image")
        results = reader.readtext(image, detail=1)
        texts = [t for (_, t, c) in results if c > 0.15]
        print(f"  Extracted: {''.join(texts)}")
        
        # Test 2: Upscaled
        print("\n[Test 2] 3x Upscaled")
        h, w = image.shape[:2]
        upscaled = cv2.resize(image, (w*3, h*3), interpolation=cv2.INTER_CUBIC)
        results = reader.readtext(upscaled, detail=1)
        texts = [t for (_, t, c) in results if c > 0.15]
        print(f"  Extracted: {''.join(texts)}")
        
        # Test 3: Grayscale
        print("\n[Test 3] Grayscale")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray, detail=1)
        texts = [t for (_, t, c) in results if c > 0.15]
        print(f"  Extracted: {''.join(texts)}")
        
        # Test 4: Grayscale + Upscaled + Enhanced
        print("\n[Test 4] Grayscale + Upscaled + CLAHE")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        upscaled = cv2.resize(gray, (gray.shape[1]*3, gray.shape[0]*3), interpolation=cv2.INTER_CUBIC)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(upscaled)
        results = reader.readtext(enhanced, detail=1)
        texts = [t for (_, t, c) in results if c > 0.15]
        print(f"  Extracted: {''.join(texts)}")
        
        # Test 5: Aggressive thresholding
        print("\n[Test 5] Thresholded")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        upscaled = cv2.resize(gray, (gray.shape[1]*3, gray.shape[0]*3), interpolation=cv2.INTER_CUBIC)
        _, thresh = cv2.threshold(upscaled, 127, 255, cv2.THRESH_BINARY)
        results = reader.readtext(thresh, detail=1)
        texts = [t for (_, t, c) in results if c > 0.15]
        print(f"  Extracted: {''.join(texts)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("[OCR Engine Comparison]\n")
    
    plate = create_test_plate()
    cv2.imwrite("ocr_test_plate.jpg", plate)
    print("✅ Created test plate: ocr_test_plate.jpg\n")
    
    test_tesseract(plate)
    test_easyocr_advanced(plate)
    
    print("\n" + "="*60)
    print("Comparison Complete")
    print("="*60)
