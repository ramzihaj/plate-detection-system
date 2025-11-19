#!/usr/bin/env python3
"""
Test realistic OCR symbol errors
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.ocr_digit_corrector import intelligently_extract_digits, correct_ocr_digit

print("\n" + "=" * 100)
print("OCR SYMBOL CORRECTION TEST")
print("=" * 100 + "\n")

# Test individual character corrections
test_chars = [
    ('2', 'should be 2'),
    (':', 'colon should become 5'),
    (')', 'parenthesis should become 6'),
    ('5', 'should be 5'),
    ('6', 'should be 6'),
    ('O', 'letter O should become 0'),
    ('Z', 'letter Z should become 2'),
    ('S', 'letter S should become 5'),
]

print("Character-by-character corrections:")
for char, desc in test_chars:
    corrected = correct_ocr_digit(char)
    print(f"  '{char}' ({desc}) → '{corrected}'")

print("\n" + "=" * 100)
print("BLOCK PROCESSING EXAMPLES")
print("=" * 100 + "\n")

examples = [
    (['2:)56'], "Symbols in digits", "Should extract: 2, 5 (from :), 6 (from )), 5, 6 = 25656"),
    (['202TN2806'], "Perfect plate", "Should extract: 202TN2806"),
    (['2O2'], "Letter O errors", "Should extract: 202"),
    (['1Z2'], "Letter Z errors", "Should extract: 122"),
    (['1S2 TN 83S5'], "Multiple errors with spaces", "Should extract: 152TN8355"),
]

for blocks, title, expected in examples:
    print(f"Example: {title}")
    print(f"  Input:    {blocks}")
    result_digits = intelligently_extract_digits(blocks)
    result = "".join(result_digits)
    print(f"  Result:   '{result}'")
    print(f"  Expected: {expected}")
    print()
