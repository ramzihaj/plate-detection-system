#!/usr/bin/env python3
"""
Enhanced OCR Test with Better Test Images
"""
import cv2
import numpy as np
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.yolo_plate_detector import YOLOPlateDetector
from app.utils.tunisia_plate_validator import TunisianPlateValidator

def create_realistic_plate():
    """Create a more realistic plate image similar to Tunisian plates"""
    # Create white background (Tunisian plates are white with blue band)
    plate = np.ones((120, 400, 3), dtype=np.uint8) * 255
    
    # Add blue band on left (typical Tunisian plate design)
    plate[0:50, 0:50] = [200, 0, 0]  # Blue (BGR format)
    
    # Add yellow band below (for EU plates style)
    plate[110:120, :] = [0, 215, 255]  # Yellow (BGR format)
    
    # Add dark text - main plate number
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "199TN0199"
    
    # Place main text
    cv2.putText(plate, text, (50, 80), font, 2.5, (0, 0, 0), 4)
    
    return plate

def test_on_realistic_plate():
    """Test OCR on realistic plate"""
    print("\n" + "="*60)
    print("Testing OCR on Realistic Plate Image")
    print("="*60)
    
    plate = create_realistic_plate()
    
    # Save for inspection
    cv2.imwrite("test_plate.jpg", plate)
    print(f"✅ Generated test plate image (400x120): test_plate.jpg")
    
    try:
        detector = YOLOPlateDetector()
        validator = TunisianPlateValidator()
        
        # Test preprocessing
        print("\n[1] Preprocessing...")
        processed = detector._preprocess_plate(plate)
        cv2.imwrite("test_plate_preprocessed.jpg", processed)
        print(f"✅ Preprocessed image: {processed.shape} -> test_plate_preprocessed.jpg")
        
        # Test OCR extraction
        print("\n[2] OCR Extraction...")
        extracted = detector._extract_text_from_plate(plate)
        print(f"✅ Extracted: '{extracted}'")
        
        # Test validation
        print("\n[3] Validation...")
        is_valid, formatted = validator.validate_and_format(extracted)
        print(f"   Input: '{extracted}'")
        print(f"   Formatted: '{formatted}'")
        print(f"   Is Valid: {is_valid}")
        
        # Show the flow
        print(f"\n[Flow]")
        print(f"  Input: 199TN0199")
        print(f"  → OCR: '{extracted}'")
        print(f"  → Validated: {is_valid}")
        print(f"  → Formatted: '{formatted}'")
        
        if is_valid and formatted == "199TN0199":
            print("\n✅✅✅ OCR Pipeline Working Correctly!")
        else:
            print(f"\n⚠️  Expected '199TN0199' but got '{formatted}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_on_real_image():
    """Test on actual plate images if available"""
    print("\n" + "="*60)
    print("Testing OCR on Real Plate Images (if available)")
    print("="*60)
    
    test_dirs = [
        'data/test_images',
        'backend/test_data',
        'test_data',
        'uploads/plates'
    ]
    
    images = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for ext in ['*.jpg', '*.png', '*.jpeg']:
                images.extend(Path(test_dir).glob(ext))
    
    if not images:
        print("⚠️  No real plate images found")
        return
    
    print(f"✅ Found {len(images)} real image(s)\n")
    
    try:
        detector = YOLOPlateDetector()
        validator = TunisianPlateValidator()
        
        for image_path in images[:3]:  # Test first 3
            print(f"\nTesting: {image_path}")
            image = cv2.imread(str(image_path))
            
            if image is None:
                print(f"  ❌ Failed to load")
                continue
            
            print(f"  Size: {image.shape}")
            
            extracted = detector._extract_text_from_plate(image)
            is_valid, formatted = validator.validate_and_format(extracted)
            
            print(f"  Extracted: '{extracted}'")
            print(f"  Formatted: '{formatted}' | Valid: {is_valid}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("[Enhanced OCR Test]")
    print(f"Current directory: {os.getcwd()}")
    
    test_on_realistic_plate()
    test_on_real_image()
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)
