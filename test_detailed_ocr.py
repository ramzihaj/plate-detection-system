#!/usr/bin/env python3
"""
Test detailed OCR extraction with comprehensive logging
"""

import sys
import cv2
import numpy as np
sys.path.insert(0, 'backend')

from app.services.yolo_plate_detector import YOLOPlateDetector

print("\n" + "=" * 90)
print("DETAILED OCR EXTRACTION TEST WITH COMPREHENSIVE LOGS")
print("=" * 90 + "\n")

# Initialize detector
print("[INIT] Initializing YOLO detector...")
detector = YOLOPlateDetector()
print("[INIT] ✅ Detector ready\n")

# Create a realistic plate image with errors
print("[CREATE] Creating synthetic plate image with OCR challenges...")
print("[CREATE] Simulating: 2O2TN28O6 (with O instead of 0, simulating OCR errors)\n")

# Create test image - white background with black text
img = np.ones((120, 350, 3), dtype=np.uint8) * np.array([200, 255, 255], dtype=np.uint8)

# Draw plate frame
cv2.rectangle(img, (10, 10), (340, 110), (0, 0, 0), 2)

# Draw the plate text (in BGR: blue=255, green=0, red=0 = blue)
cv2.putText(img, "2O2TN28O6", (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)

# Convert to uint8 if needed
img = img.astype(np.uint8)

print("[TEST] Calling OCR extraction method directly...\n")
print("-" * 90)

# Call extraction to see all the detailed logs
extracted_text = detector._extract_text_from_plate(img)

print("-" * 90)

print(f"\n[RESULT] Final extracted text: '{extracted_text}'")
print(f"[RESULT] Length: {len(extracted_text)} characters\n")

print("=" * 90)
print("TEST COMPLETE - See logs above for detailed breakdown of:")
print("  1. Each OCR block detected with confidence scores")
print("  2. Blocks accepted/rejected based on confidence threshold")
print("  3. Raw text joining from all blocks")
print("  4. Character-by-character digit correction")
print("=" * 90 + "\n")
