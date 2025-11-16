#!/usr/bin/env python3
"""
Test End-to-End Plate Detection
"""
import sys
import os
import cv2
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.yolo_plate_detector import YOLOPlateDetector
from app.utils.tunisia_plate_validator import TunisianPlateValidator

def test_detection_on_files():
    """Test detection on all test plate images"""
    
    print("\n" + "="*70)
    print("End-to-End Plate Detection Test")
    print("="*70)
    
    # Find all test images
    test_images = list(Path("data/test_images").glob("*.jpg")) + \
                  list(Path("data/test_images").glob("*.png"))
    
    if not test_images:
        print("No test images found!")
        return
    
    print(f"\nFound {len(test_images)} test image(s)\n")
    
    # Initialize detector
    detector = YOLOPlateDetector()
    print("✅ YOLO detector initialized\n")
    
    for image_path in sorted(test_images):
        print(f"[Testing] {image_path.name}")
        print("-" * 70)
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print("❌ Failed to load image\n")
            continue
        
        print(f"  Image size: {image.shape}")
        
        # Detect plates
        try:
            detections = detector.detect_plates(image)
            
            if not detections:
                print("  ⚠️  No plates detected\n")
                continue
            
            print(f"  ✅ Found {len(detections)} detection(s)\n")
            
            for i, det in enumerate(detections):
                print(f"  [Detection {i+1}]")
                print(f"    Plate Text: '{det.plate_text}'")
                print(f"    Confidence: {det.confidence:.1%}")
                print(f"    Valid Format: {det.is_valid_format}")
                print(f"    Bounding Box: {det.bounding_box}")
                if det.is_valid_format:
                    print(f"    ✅ Valid Tunisian format!")
                print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("[Plate Detection End-to-End Test]")
    print(f"Current directory: {os.getcwd()}")
    
    test_detection_on_files()
    
    print("="*70)
    print("Test Complete")
    print("="*70)
