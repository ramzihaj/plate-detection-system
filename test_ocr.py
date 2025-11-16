#!/usr/bin/env python3
"""
OCR Diagnostic Script
Tests EasyOCR extraction on sample plate images
"""
import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.tunisia_plate_validator import TunisianPlateValidator
from app.services.yolo_plate_detector import YOLOPlateDetector

def test_ocr_on_image(image_path):
    """Test OCR extraction on an image"""
    
    print(f"\n{'='*60}")
    print(f"Testing OCR on: {image_path}")
    print(f"{'='*60}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image")
        return
    
    print(f"✅ Image loaded: {image.shape}")
    
    # Initialize detector
    try:
        detector = YOLOPlateDetector()
        print(f"✅ YOLO detector initialized")
        
        # Run detection
        print(f"\n[1] Running YOLO detection...")
        detections = detector.detect_plates(image)
        
        if not detections:
            print(f"⚠️  No plates detected by YOLO")
            return
        
        print(f"✅ Found {len(detections)} detection(s)")
        
        for i, detection in enumerate(detections):
            print(f"\n[Detection {i+1}]")
            print(f"  Raw Plate Text: '{detection.plate_text}'")
            print(f"  Confidence: {detection.confidence:.2%}")
            print(f"  Is Valid Format: {detection.is_valid_format}")
            print(f"  Bounding Box: {detection.bounding_box}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def find_test_images():
    """Find available test images"""
    test_dirs = [
        'data/test_images',
        'backend/test_data',
        'test_data'
    ]
    
    images = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for ext in ['*.jpg', '*.png', '*.jpeg']:
                images.extend(Path(test_dir).glob(ext))
    
    return images

if __name__ == '__main__':
    print("[OCR Diagnostic Test]")
    print(f"Current directory: {os.getcwd()}")
    
    # Find and test all available images
    images = find_test_images()
    
    if not images:
        print("\n⚠️  No test images found in:")
        print("  - data/test_images/")
        print("  - backend/test_data/")
        print("  - test_data/")
        print("\n💡 To test OCR, please place test images in one of these directories")
        sys.exit(0)
    
    print(f"\n✅ Found {len(images)} test image(s)")
    
    for image_path in images:
        test_ocr_on_image(str(image_path))
