#!/usr/bin/env python3
"""
Show step-by-step transformation of OCR text through the pipeline
Example: 152hdkffd14562 → 152TN4562
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.tunisia_plate_validator import TunisianPlateValidator

validator = TunisianPlateValidator()

# Test cases showing step-by-step transformation
test_cases = [
    ("152hdkffd14562", "Messy with garbage characters"),
    ("2O2TN28O6", "OCR errors (O instead of 0)"),
    ("1Z2TN83SS", "Z→2, S→5 errors"),
    ("000تن2522", "Arabic characters"),
    ("1S2 TN 83S5", "Spaces between characters"),
]

print("\n" + "=" * 100)
print("STEP-BY-STEP TEXT TRANSFORMATION PIPELINE")
print("=" * 100 + "\n")

for idx, (input_text, description) in enumerate(test_cases, 1):
    print(f"TEST CASE #{idx}: {description}")
    print("-" * 100)
    print()
    
    print(f"  INPUT STAGE:")
    print(f"    └─ Raw OCR:           '{input_text}'")
    print()
    
    # Stage 1: Clean text (remove spaces, Arabic chars, OCR corrections)
    stage1_cleaned = validator._clean_text(input_text)
    print(f"  STAGE 1 (CLEANING):")
    print(f"    └─ After cleaning:    '{stage1_cleaned}'")
    print(f"       (Removed spaces, converted Arabic, corrected O→0, Z→2, S→5, etc.)")
    print()
    
    # Stage 2: Extract format
    stage2_extracted = validator._extract_tunisian_format(stage1_cleaned)
    print(f"  STAGE 2 (FORMAT EXTRACTION):")
    print(f"    └─ After extraction:  '{stage2_extracted}'")
    print(f"       (Extracted 3 digits + TN + 4 digits with zero padding)")
    print()
    
    # Stage 3: Full validation
    is_valid, stage3_formatted = validator.validate_and_format(input_text)
    print(f"  STAGE 3 (VALIDATION):")
    print(f"    ├─ Final formatted:   '{stage3_formatted}'")
    print(f"    ├─ Is valid format:   {is_valid}")
    print(f"    └─ Pattern matched:   {validator.TUNISIAN_PATTERN.match(stage3_formatted) is not None}")
    print()
    
    # Stage 4: Display format
    if is_valid:
        display_format = validator.format_with_spaces(stage3_formatted)
        print(f"  STAGE 4 (DISPLAY FORMAT):")
        print(f"    └─ With spaces:      '{display_format}'")
        print()
    
    print()

# Now show a complete detailed transformation
print("=" * 100)
print("DETAILED TRANSFORMATION EXAMPLE")
print("=" * 100 + "\n")

example = "2O2TN28O6"
print(f"Input plate with OCR errors: '{example}'")
print()

print("Step-by-step transformation:")
print(f"  Step 1 (Raw OCR):         {example}")
print(f"  Step 2 (After cleaning):  {validator._clean_text(example)}")
print(f"  Step 3 (After extract):   {validator._extract_tunisian_format(validator._clean_text(example))}")
is_valid, final = validator.validate_and_format(example)
print(f"  Step 4 (Final format):    {final}")
if is_valid:
    print(f"  Step 5 (Display format):  {validator.format_with_spaces(final)}")

print()
print("=" * 100)
print("TRANSFORMATION COMPLETE")
print("=" * 100 + "\n")
