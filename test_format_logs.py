#!/usr/bin/env python3
"""
Test script to verify format detection and logs.
Tests various plate formats and OCR error scenarios.
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.tunisia_plate_validator import TunisianPlateValidator
from app.utils.ocr_digit_corrector import intelligently_extract_digits

validator = TunisianPlateValidator()

# Test cases
test_cases = [
    # (input, expected_output_format, description)
    ("152TN8355", "152TN8355", "Valid format"),
    ("202TN2806", "202TN2806", "Valid format"),
    ("000TN2522", "000TN2522", "Valid with leading zeros"),
    ("2O2TN28O6", "202TN2806", "OCR error: O->0"),
    ("1Z2TN8355", "122TN8355", "OCR error: Z->2 in first position"),
    ("2O2TNZ8O6", "202TN2806", "Multiple OCR errors"),
    ("000تن2522", "000TN2522", "Arabic characters"),
    ("000tn2522", "000TN2522", "Lowercase tn"),
    ("0O0tn2522", "000TN2522", "Arabic + OCR errors"),
]

print("=" * 80)
print("TUNISIAN PLATE FORMAT TEST SUITE")
print("=" * 80)
print()

passed = 0
failed = 0

for idx, (input_text, expected, description) in enumerate(test_cases, 1):
    print(f"Test #{idx}: {description}")
    print(f"  Input:    '{input_text}'")
    
    is_valid, formatted = validator.validate_and_format(input_text)
    display_format = validator.format_with_spaces(formatted) if is_valid else formatted
    
    print(f"  Output:   '{formatted}' (displayed as: '{display_format}')")
    print(f"  Valid:    {is_valid}")
    
    # Check if result matches expectation
    if expected is None:
        # Should be invalid
        if not is_valid:
            print(f"  ✅ PASS - Correctly rejected invalid format")
            passed += 1
        else:
            print(f"  ❌ FAIL - Should have rejected but got valid: {formatted}")
            failed += 1
    else:
        # Should match expected format
        if formatted == expected and is_valid:
            print(f"  ✅ PASS - Correct format and valid")
            passed += 1
        else:
            print(f"  ❌ FAIL - Expected '{expected}' but got '{formatted}'")
            failed += 1
    
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

# Additional OCR correction test
print("\nOCR Digit Correction Test:")
print("-" * 80)

test_texts = [
    ["0O0", "2Z2", "2", "2", "2"],
    ["1I1", "5S5", "8B8"],
    ["A4A", "6G6"],
]

for texts in test_texts:
    corrected = intelligently_extract_digits(texts)
    print(f"Input:     {texts}")
    print(f"Output:    {corrected}")
    print(f"Joined:    {''.join(corrected)}")
    print()
