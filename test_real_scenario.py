#!/usr/bin/env python3
"""
Test with REAL OCR scenario from user feedback
"""

import sys
sys.path.insert(0, 'backend')

from app.utils.ocr_digit_corrector import intelligently_extract_digits

print("\n" + "=" * 100)
print("REAL OCR SCENARIO TEST - User Reported Case")
print("=" * 100 + "\n")

print("SCENARIO: EasyOCR returned 2 blocks from a Tunisian plate")
print()

# This is what the user reported: 2 blocks from OCR
# Block 1: نان 2]2 (mostly Arabic + garbage)
# Block 2: 2:)56 (symbols that look like digits)
ocr_blocks = ['نان 2]2', '2:)56']

print(f"OCR Detected blocks:")
for i, block in enumerate(ocr_blocks, 1):
    print(f"  Block {i}: '{block}'")

print("\n" + "-" * 100)
print("PROCESSING WITH IMPROVED FILTER:")
print("-" * 100 + "\n")

# Process with improved filter
result_digits = intelligently_extract_digits(ocr_blocks)
result = "".join(result_digits)

print(f"Final result: '{result}'")
print()

# Now test with correct block parsing (as it should be)
print("=" * 100)
print("CORRECTED OCR SCENARIO - If parsed correctly:")
print("=" * 100 + "\n")

# If the OCR had been properly segmented:
# Block 1: 202 or 2:)56 (but as separate blocks it should be 202 TN 2806)
# Let's simulate a case where we have:
# - Block 1: 202 (first 3 digits)
# - Block 2: TN (marker)
# - Block 3: 2806 (last 4 digits)

ocr_blocks_correct = ['202', 'TN', '2806']

print(f"OCR Detected blocks (correct segmentation):")
for i, block in enumerate(ocr_blocks_correct, 1):
    print(f"  Block {i}: '{block}'")

print("\n" + "-" * 100)
print("PROCESSING:")
print("-" * 100 + "\n")

result_digits = intelligently_extract_digits(ocr_blocks_correct)
result = "".join(result_digits)

print(f"Final result: '{result}'")
print(f"Expected:    '202TN2806'")
print(f"Status: {'✅ CORRECT' if result == '202TN2806' else '❌ WRONG'}")
print()
