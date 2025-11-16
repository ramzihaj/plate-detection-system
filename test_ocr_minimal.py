#!/usr/bin/env python3
"""
Minimal OCR Test
Tests EasyOCR directly on text extraction
"""
import cv2
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import easyocr
    print("✅ EasyOCR imported successfully")
except ImportError as e:
    print(f"❌ Failed to import EasyOCR: {e}")
    sys.exit(1)

try:
    from app.services.yolo_plate_detector import YOLOPlateDetector
    print("✅ YOLOPlateDetector imported successfully")
except ImportError as e:
    print(f"❌ Failed to import YOLOPlateDetector: {e}")
    sys.exit(1)

def test_easyocr_basic():
    """Test basic EasyOCR functionality"""
    print("\n" + "="*60)
    print("Testing EasyOCR Basic Functionality")
    print("="*60)
    
    # Create a test image with text
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # White background
    text = "199TN0199"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (30, 70), font, 2, (0, 0, 0), 3)  # Black text
    
    # Test OCR
    print("\n[1] Creating EasyOCR reader...")
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        print("✅ EasyOCR reader created")
    except Exception as e:
        print(f"❌ Failed to create reader: {e}")
        return
    
    print("[2] Running OCR on test text...")
    try:
        results = reader.readtext(img, detail=1)
        print(f"✅ OCR completed, found {len(results)} text block(s)")
        
        for bbox, text, confidence in results:
            print(f"   Text: '{text}'")
            print(f"   Confidence: {confidence:.2%}")
        
        # Extract just text
        texts = [text for (bbox, text, confidence) in results if confidence > 0.3]
        extracted = "".join(texts).strip()
        print(f"\n✅ Extracted: '{extracted}'")
        
        if extracted == "199TN0199":
            print("✅ OCR works correctly!")
        else:
            print(f"⚠️  OCR extracted '{extracted}' instead of '199TN0199'")
    
    except Exception as e:
        print(f"❌ OCR failed: {e}")
        import traceback
        traceback.print_exc()

def check_detector_ocr():
    """Check if detector's OCR works"""
    print("\n" + "="*60)
    print("Testing YOLOPlateDetector OCR Methods")
    print("="*60)
    
    try:
        detector = YOLOPlateDetector()
        print("✅ YOLOPlateDetector initialized")
        
        # Create test plate image
        plate_img = np.ones((50, 150, 3), dtype=np.uint8) * 255
        text = "199TN0199"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(plate_img, text, (10, 40), font, 1.2, (0, 0, 0), 2)
        
        print("\n[1] Testing _preprocess_plate()...")
        processed = detector._preprocess_plate(plate_img)
        print(f"✅ Preprocessed image shape: {processed.shape}")
        
        print("\n[2] Testing _extract_text_from_plate()...")
        extracted_text = detector._extract_text_from_plate(plate_img)
        print(f"✅ Extracted text: '{extracted_text}'")
        
        print("\n[3] Testing validator...")
        from app.utils.tunisia_plate_validator import TunisianPlateValidator
        validator = TunisianPlateValidator()
        is_valid, formatted = validator.validate_and_format(extracted_text)
        print(f"   Input: '{extracted_text}'")
        print(f"   Formatted: '{formatted}'")
        print(f"   Is Valid: {is_valid}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("[Minimal OCR Test]")
    print(f"Current directory: {os.getcwd()}")
    
    test_easyocr_basic()
    check_detector_ocr()
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
