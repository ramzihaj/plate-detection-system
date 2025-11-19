#!/usr/bin/env python3
"""
Complete pipeline test showing all transformation stages
From raw OCR to final formatted plate
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.tunisia_plate_validator import TunisianPlateValidator

print("\n" + "=" * 100)
print("COMPLETE PIPELINE TEST - ALL TRANSFORMATION STAGES")
print("=" * 100 + "\n")

# Initialize
print("[INIT] Initializing validator...\n")
validator = TunisianPlateValidator()

# Test cases with detailed transformation logging
test_cases = [
    {
        'name': 'OCR Errors (O→0)',
        'raw': '2O2TN28O6',
        'description': 'EasyOCR mistook 0 for O'
    },
    {
        'name': 'Multiple Errors (O, Z, S)',
        'raw': '1Z2TN83SS',
        'description': 'Multiple digit confusions'
    },
    {
        'name': 'Arabic Characters',
        'raw': '000تن2522',
        'description': 'Plate with Arabic ت ن'
    },
    {
        'name': 'Spaces in Text',
        'raw': '1S2 TN 83S5',
        'description': 'Spaces between blocks'
    },
    {
        'name': 'Garbage Characters',
        'raw': '152hdkffd14562',
        'description': 'Letters mixed with numbers'
    }
]

for idx, test in enumerate(test_cases, 1):
    print("=" * 100)
    print(f"TEST CASE #{idx}: {test['name']}")
    print("=" * 100)
    print(f"Description: {test['description']}\n")
    
    raw_text = test['raw']
    
    # Stage 1
    print(f"📍 STAGE 1 - Raw OCR extraction:")
    print(f"   └─ {raw_text}")
    print(f"      (Exactly what EasyOCR detected)\n")
    
    # Stage 2
    cleaned = validator._clean_text(raw_text)
    print(f"📍 STAGE 2 - Text cleaning:")
    print(f"   └─ {raw_text} → {cleaned}")
    print(f"      (Removed spaces, converted Arabic, applied corrections)\n")
    
    # Stage 3
    extracted = validator._extract_tunisian_format(cleaned)
    print(f"📍 STAGE 3 - Format extraction:")
    print(f"   └─ {cleaned} → {extracted}")
    print(f"      (Extracted 3 digits + TN + 4 digits)\n")
    
    # Stage 4 - Validation
    is_valid, formatted = validator.validate_and_format(raw_text)
    print(f"📍 STAGE 4 - Final validation & format:")
    print(f"   └─ {extracted} → {formatted}")
    print(f"      (Validated against XXXTNXXXX pattern)\n")
    
    # Stage 5 - Display
    if is_valid:
        displayed = validator.format_with_spaces(formatted)
        print(f"📍 STAGE 5 - Display formatting:")
        print(f"   └─ {formatted} → {displayed}")
        print(f"      (Added spaces: XXX TN XXXX)\n")
        print(f"✅ RESULT: VALID - {displayed}\n\n")
    else:
        print(f"❌ RESULT: INVALID - Doesn't match pattern XXXTNXXXX\n\n")

print("=" * 100)
print("ALL TESTS COMPLETED")
print("=" * 100 + "\n")
