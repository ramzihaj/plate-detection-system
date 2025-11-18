#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API test script for the plate detection backend.
Tests the complete HTTP API with image uploads.
"""

import requests
import json
import time
from pathlib import Path
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("PLATE DETECTION API TEST")
print("=" * 80)
print()

# Step 1: Register a test user
import uuid
print("[STEP 1] Registering test user...")
test_user = f"testuser_{uuid.uuid4().hex[:8]}"
register_data = {
    "email": f"{test_user}@example.com",
    "username": test_user,
    "password": "TestPassword123!"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code in [200, 201]:
        print(f"  ✅ Registration successful (user: {test_user})")
        user_data = response.json()
    else:
        print(f"  ⚠️  Registration returned {response.status_code}: {response.text[:100]}")
except Exception as e:
    print(f"  ❌ Registration failed: {e}")
    exit(1)

print()

# Step 2: Login
print("[STEP 2] Logging in...")
login_data = {
    "email": f"{test_user}@example.com",
    "password": "TestPassword123!"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        print(f"  ✅ Login successful")
        token = response.json().get("access_token")
        print(f"  Token: {token[:20]}...")
    else:
        print(f"  ❌ Login failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"  ❌ Login failed: {e}")
    exit(1)

print()

# Step 3: Get user stats
print("[STEP 3] Getting user stats...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(f"{BASE_URL}/api/users/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"  ✅ Stats retrieved")
        print(f"     Total detections: {stats.get('total_detections', 0)}")
        print(f"     Valid plates: {stats.get('valid_plates', 0)}")
        print(f"     Invalid plates: {stats.get('invalid_plates', 0)}")
    else:
        print(f"  ❌ Stats failed: {response.status_code}")
except Exception as e:
    print(f"  ❌ Stats failed: {e}")

print()

# Step 4: Test plate detection with sample image
print("[STEP 4] Testing plate detection endpoint...")

# Create a simple test image if none exists
test_image_path = Path("test_plate.jpg")
if not test_image_path.exists():
    print("  Creating synthetic test image...")
    import cv2
    import numpy as np
    
    # Create a simple blue image with white text
    img = np.ones((100, 300, 3), dtype=np.uint8) * [0, 100, 200]  # Yellow background
    cv2.putText(img, "152TN8355", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.imwrite(str(test_image_path), img)
    print(f"  ✅ Test image created: {test_image_path}")

print()

# Upload test image
print("[STEP 5] Uploading test image to detection API...")
try:
    with open(test_image_path, 'rb') as f:
        files = {'file': (test_image_path.name, f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/api/plates/detect", headers=headers, files=files)
    
    if response.status_code == 200:
        print(f"  ✅ Detection successful")
        result = response.json()
        print(f"\n  Detection Result:")
        print(f"    Detected plate:  {result.get('detected_plate')}")
        print(f"    Confidence:      {result.get('confidence', 0):.2%}")
        print(f"    Valid format:    {result.get('is_valid_format')}")
        print(f"    Detection time:  {result.get('detection_time'):.3f}s")
        print(f"    Status:          {result.get('status')}")
    else:
        print(f"  ❌ Detection failed: {response.status_code}")
        print(f"     Response: {response.text}")
except Exception as e:
    print(f"  ❌ Detection failed: {e}")

print()

# Step 6: Get detection history
print("[STEP 6] Getting detection history...")
try:
    response = requests.get(f"{BASE_URL}/api/plates/history", headers=headers)
    if response.status_code == 200:
        history = response.json()
        print(f"  ✅ History retrieved")
        print(f"     Total detections: {history.get('total', 0)}")
        print(f"     Page size: {history.get('page_size', 0)}")
        
        detections = history.get('detections', [])
        if detections:
            print(f"\n     Recent detections:")
            for i, det in enumerate(detections[:3], 1):
                print(f"       {i}. {det.get('detected_plate')} (valid: {det.get('is_valid_format')})")
    else:
        print(f"  ❌ History failed: {response.status_code}")
except Exception as e:
    print(f"  ❌ History failed: {e}")

print()
print("=" * 80)
print("API TEST COMPLETE")
print("=" * 80)
