#!/usr/bin/env python3
"""Test script to verify YOLO model loading"""

import os
import sys

# Get the current directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")
print(f"Working from: {os.path.abspath('.')}")

# Print all files in current directory
print("\n=== Files in current directory ===")
for item in os.listdir('.'):
    print(f"  {item}")

# Check if model directory exists
print("\n=== Checking model directories ===")
model_dirs = [
    'model',
    'backend/model',
    '../model',
    '../../model',
]

for model_dir in model_dirs:
    exists = os.path.exists(model_dir)
    print(f"  {model_dir}: {exists}")
    if exists:
        print(f"    Contents: {os.listdir(model_dir)}")

# Check specific model file
print("\n=== Checking for best002.pt ===")
candidates = [
    'model/best002.pt',
    'backend/model/best002.pt',
    '../model/best002.pt',
    '../../model/best002.pt',
]

for candidate in candidates:
    exists = os.path.exists(candidate)
    abs_path = os.path.abspath(candidate)
    print(f"  {candidate}: {exists}")
    if exists:
        size = os.path.getsize(candidate)
        print(f"    Size: {size} bytes")
        print(f"    Absolute: {abs_path}")

# Now test YOLO loading
print("\n=== Testing YOLO model loading ===")
try:
    from ultralytics import YOLO
    
    # Try to load best002.pt
    for candidate in candidates:
        if os.path.exists(candidate):
            print(f"\nTrying to load: {candidate}")
            try:
                model = YOLO(candidate)
                print(f"  ✅ Successfully loaded YOLO from {candidate}")
                break
            except Exception as e:
                print(f"  ❌ Failed to load: {e}")
    else:
        print("\n  ⚠️ No custom model found, loading default yolov8n")
        model = YOLO("yolov8n")
        print(f"  ✅ Default model loaded")
        
except Exception as e:
    print(f"Error importing YOLO: {e}")
