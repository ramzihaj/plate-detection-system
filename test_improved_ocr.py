#!/usr/bin/env python3
"""
Test improved OCR filtering and symbol correction
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.ocr_digit_corrector import intelligently_extract_digits, is_valid_plate_text

print("\n" + "=" * 100)
print("IMPROVED OCR FILTERING TEST")
print("=" * 100 + "\n")

# Test cases simulating the problematic OCR output
test_cases = [
    {
        'name': 'Test #1: Mostly Arabic + garbage',
        'blocks': ['نان 2]2'],  # Arabic + 2]2
        'expected_action': 'REJECT (>60% Arabic)',
    },
    {
        'name': 'Test #2: Symbols that look like digits',
        'blocks': ['2:)56'],  # Symbols: : -> 5, ) -> 6
        'expected_action': 'ACCEPT & CORRECT to 2556',
    },
    {
        'name': 'Test #3: Mixed with errors',
        'blocks': ['2O2TN28O6'],  # O -> 0
        'expected_action': 'ACCEPT & CORRECT to 202TN2806',
    },
    {
        'name': 'Test #4: Correct plate format',
        'blocks': ['202TN2806'],
        'expected_action': 'ACCEPT as-is',
    },
    {
        'name': 'Test #5: Multiple blocks (correct way)',
        'blocks': ['202', 'TN', '2806'],
        'expected_action': 'ACCEPT all, combine to 202TN2806',
    },
    {
        'name': 'Test #6: Arabic numerals (٠-٩)',
        'blocks': ['٢٠٢تن٢٨٠٦'],
        'expected_action': 'ACCEPT & CONVERT to 202TN2806',
    },
]

for test in test_cases:
    print("=" * 100)
    print(test['name'])
    print("=" * 100)
    print(f"Input blocks: {test['blocks']}")
    print(f"Expected: {test['expected_action']}\n")
    
    # Check each block validity
    print("Block validation:")
    valid_blocks = []
    for block in test['blocks']:
        is_valid = is_valid_plate_text(block)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"  '{block}' → {status}")
        if is_valid:
            valid_blocks.append(block)
    
    # Extract and correct digits
    if valid_blocks:
        print(f"\nValid blocks kept: {valid_blocks}")
        corrected = intelligently_extract_digits(valid_blocks)
        result = "".join(corrected)
        print(f"After correction: '{result}'")
    else:
        print(f"\n❌ All blocks rejected - NO OUTPUT")
        result = ""
    
    print()

print("=" * 100)
print("TEST COMPLETE")
print("=" * 100 + "\n")
