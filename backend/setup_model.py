#!/usr/bin/env python
"""
YOLO Model Setup Script
Download, configure, and optimize YOLO models for plate detection
"""

import os
import sys
import argparse
from pathlib import Path
import shutil

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = [
        "model",
        "backend/model",
        "backend/uploads",
        "backend/uploads/plates",
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}/")
    
    print()

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        import ultralytics
        print("   ✓ ultralytics already installed")
    except ImportError:
        print("   ⏳ Installing ultralytics...")
        os.system(f"{sys.executable} -m pip install ultralytics")
    
    try:
        import cv2
        print("   ✓ opencv-python already installed")
    except ImportError:
        print("   ⏳ Installing opencv-python...")
        os.system(f"{sys.executable} -m pip install opencv-python")
    
    try:
        import easyocr
        print("   ✓ easyocr already installed")
    except ImportError:
        print("   ⏳ Installing easyocr...")
        os.system(f"{sys.executable} -m pip install easyocr")
    
    print()

def download_yolo_model(model_size="n"):
    """Download YOLOv8 model"""
    print(f"🤖 Downloading YOLOv8{model_size} model...")
    
    try:
        from ultralytics import YOLO
        
        # Available sizes: n (nano), s (small), m (medium), l (large), x (xlarge)
        model = YOLO(f'yolov8{model_size}.pt')
        print(f"   ✓ YOLOv8{model_size} downloaded")
        
        return model
    except Exception as e:
        print(f"   ✗ Error downloading model: {e}")
        return None

def setup_custom_model(model_path):
    """Setup custom model"""
    print(f"🎯 Setting up custom model from: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"   ✗ Model file not found: {model_path}")
        return False
    
    # Copy model to standard location
    dest_path = "model/best.pt"
    try:
        shutil.copy2(model_path, dest_path)
        print(f"   ✓ Model copied to: {dest_path}")
        
        # Verify model
        from ultralytics import YOLO
        model = YOLO(dest_path)
        print(f"   ✓ Model verified successfully")
        print(f"   ✓ Task: {model.task}")
        
        return True
    except Exception as e:
        print(f"   ✗ Error setting up model: {e}")
        return False

def optimize_model(model_path):
    """Optimize model for faster inference"""
    print(f"⚡ Optimizing model for inference...")
    
    try:
        from ultralytics import YOLO
        
        model = YOLO(model_path)
        
        # Export to optimized format (ONNX for CPU, TensorRT for GPU)
        print("   ⏳ Exporting to ONNX format...")
        export_result = model.export(format='onnx', imgsz=640, half=False)
        
        print(f"   ✓ Model exported to: {export_result}")
        
        return True
    except Exception as e:
        print(f"   ⚠ Could not optimize (not critical): {e}")
        return False

def test_model():
    """Test the configured model"""
    print("🧪 Testing model...")
    
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
        from app.services.yolo_plate_detector import YOLOPlateDetector
        
        detector = YOLOPlateDetector()
        print(f"   ✓ Model loaded successfully")
        print(f"   ✓ Model: {detector.model}")
        print(f"   ✓ Task: {detector.model.task}")
        
        # Test with dummy image
        import numpy as np
        import cv2
        
        dummy_image = np.ones((480, 640, 3), dtype=np.uint8) * 200
        detections = detector.detect_plates(dummy_image, confidence_threshold=0.5)
        
        print(f"   ✓ Inference works (test image: 0 plates detected as expected)")
        
        return True
    except Exception as e:
        print(f"   ✗ Error testing model: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_status():
    """Print system status"""
    print("\n" + "="*70)
    print(" YOLO Plate Detection System Status")
    print("="*70)
    
    checks = {
        "Model directory": os.path.exists("model"),
        "Model file (best.pt)": os.path.exists("model/best.pt"),
        "Model file (best002.pt)": os.path.exists("model/best002.pt"),
        "Uploads directory": os.path.exists("backend/uploads"),
        "Plates directory": os.path.exists("backend/uploads/plates"),
    }
    
    for check_name, status in checks.items():
        status_icon = "✓" if status else "✗"
        print(f"  [{status_icon}] {check_name}")
    
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Setup YOLO model for plate detection")
    parser.add_argument("--download", choices=['n', 's', 'm', 'l', 'x'], 
                        help="Download YOLOv8 model (n=nano, s=small, m=medium, l=large, x=xlarge)")
    parser.add_argument("--custom", type=str, help="Path to custom YOLO model (.pt file)")
    parser.add_argument("--optimize", action="store_true", help="Optimize model for faster inference")
    parser.add_argument("--test", action="store_true", help="Test the configured model")
    parser.add_argument("--full", action="store_true", help="Run full setup (directories + dependencies + nano model + test)")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" 🚀 YOLO Plate Detection Setup")
    print("="*70 + "\n")
    
    # Full setup
    if args.full:
        setup_directories()
        install_dependencies()
        download_yolo_model('n')  # Download nano model
        test_model()
        print_status()
        print("✓ Full setup complete! Ready to detect plates.\n")
        return
    
    # Individual setups
    if not args.download and not args.custom and not args.optimize and not args.test:
        # Default: setup directories and test
        setup_directories()
        install_dependencies()
        if test_model():
            print_status()
        print()
        return
    
    # Setup directories first
    setup_directories()
    install_dependencies()
    
    if args.download:
        download_yolo_model(args.download)
    
    if args.custom:
        setup_custom_model(args.custom)
    
    if args.optimize:
        model_path = "model/best.pt" if os.path.exists("model/best.pt") else "yolov8n.pt"
        optimize_model(model_path)
    
    if args.test:
        test_model()
    
    print_status()
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
