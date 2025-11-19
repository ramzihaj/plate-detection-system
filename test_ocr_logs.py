#!/usr/bin/env python3
"""
Test script to demonstrate detailed OCR extraction logs
"""

import sys
import cv2
import numpy as np
sys.path.insert(0, 'backend')

from app.services.yolo_plate_detector import YOLOPlateDetector

print("=" * 80)
print("OCR EXTRACTION LOGS DEMONSTRATION")
print("=" * 80)
print()

# Initialize detector
print("[INIT] Initializing YOLO detector...")
detector = YOLOPlateDetector()
print("[INIT] ✅ YOLO detector ready\n")

# Create a test image with text similar to a plate
print("[TEST] Creating synthetic plate image...")
img = np.ones((100, 300, 3), dtype=np.uint8) * [255, 255, 200]  # Light yellow
cv2.putText(img, "2O2TN28O6", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
print("[TEST] ✅ Test image created (simulating plate with OCR errors)\n")

# Test extraction directly
print("[TEST] Testing OCR extraction directly...")
print("-" * 80)
print()

# Call the extraction method directly to see all logs
extracted_text = detector._extract_text_from_plate(img)

print()
print("-" * 80)
print(f"[RESULT] Extracted text: '{extracted_text}'")
print()

# Test with full detection
print("[TEST] Testing full detection pipeline...")
print("-" * 80)
print()

# Create YOLO-like detection by simulating
print("[NOTE] In production, YOLO would detect the plate first")
print("[NOTE] Then extract text from each detected region")
print()

# Clean up
import os
if os.path.exists("test_plate.jpg"):
    os.remove("test_plate.jpg")

print("=" * 80)
print("TEST COMPLETE - Check logs above for detailed OCR extraction steps")
print("=" * 80)
