#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test EasyOCR with Tunisian Plate Specific Optimization
"""
import cv2
import numpy as np
import sys
import os

import easyocr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.tunisia_plate_validator import TunisianPlateValidator

def create_test_plate():
    """Create test plate image"""
    plate = np.ones((120, 400, 3), dtype=np.uint8) * 255
    plate[0:50, 0:50] = [200, 0, 0]
    plate[110:120, :] = [0, 215, 255]
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(plate, "199TN0199", (50, 80), font, 2.5, (0, 0, 0), 4)
    
    return plate

def test_ocr_strategies():
    """Test different preprocessing strategies"""
    print("\n" + "="*70)
    print("EasyOCR Plate Detection Optimization")
    print("="*70)
    
    plate = create_test_plate()
    cv2.imwrite("test_plate_final.jpg", plate)
    print("[*] Test image created: test_plate_final.jpg\n")
    
    reader = easyocr.Reader(['en'], gpu=False)
    validator = TunisianPlateValidator()
    
    strategies = [
        ("1. Original", lambda img: img),
        ("2. Grayscale", lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
        ("3. Grayscale 3x", lambda img: cv2.resize(
            cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
            (img.shape[1]*3, img.shape[0]*3), 
            cv2.INTER_CUBIC)),
        ("4. Grayscale 3x + CLAHE", lambda img: cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8)).apply(
            cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
                      (img.shape[1]*3, img.shape[0]*3), cv2.INTER_CUBIC))),
        ("5. Grayscale 3x + Binary Thresh", lambda img: cv2.threshold(
            cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
                      (img.shape[1]*3, img.shape[0]*3), cv2.INTER_CUBIC),
            127, 255, cv2.THRESH_BINARY)[1]),
        ("6. Grayscale 3x + Adaptive Thresh", lambda img: cv2.adaptiveThreshold(
            cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
                      (img.shape[1]*3, img.shape[0]*3), cv2.INTER_CUBIC),
            255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
    ]
    
    results_summary = []
    
    for name, preprocessing in strategies:
        try:
            processed = preprocessing(plate)
            
            # Run OCR
            ocr_results = reader.readtext(processed, detail=1)
            texts = [t for (_, t, c) in ocr_results if c > 0.15]
            extracted = "".join(texts)
            
            # Validate
            is_valid, formatted = validator.validate_and_format(extracted)
            
            print(f"[{name}]")
            print(f"  Extracted: '{extracted}'")
            print(f"  Formatted: '{formatted}'")
            print(f"  Valid: {is_valid}")
            print()
            
            results_summary.append((name, extracted, is_valid))
            
        except Exception as e:
            print(f"[{name}] ERROR: {e}\n")
    
    # Show best results
    print("="*70)
    print("SUMMARY")
    print("="*70)
    valid_results = [r for r in results_summary if r[2]]
    if valid_results:
        print("SUCCESS - Valid extractions:")
        for name, extracted, _ in valid_results:
            print(f"  {name}: '{extracted}'")
    else:
        print("No valid results. Best approximations:")
        for name, extracted, _ in results_summary[:3]:
            print(f"  {name}: '{extracted}'")

if __name__ == '__main__':
    test_ocr_strategies()
