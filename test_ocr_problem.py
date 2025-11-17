#!/usr/bin/env python3
"""
Test OCR extraction for specific plate
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.tunisia_plate_validator import get_tunisia_validator

validator = get_tunisia_validator()

# Test the problematic input
test_input = "0355TوNN521"

print("="*70)
print("Testing Problematic Plate Detection")
print("="*70)
print(f"\nInput OCR result: '{test_input}'")

# Step 1: Clean the text
cleaned = validator._clean_text(test_input)
print(f"After cleaning: '{cleaned}'")

# Step 2: Validate and format
is_valid, formatted = validator.validate_and_format(test_input)
print(f"Formatted result: '{formatted}'")
print(f"Is valid: {is_valid}")

# Test more inputs
print("\n" + "="*70)
print("Testing Various OCR Misreadings")
print("="*70)

test_cases = [
    "0355TوNN521",      # Original problem
    "152TN8355",        # Correct format
    "5538NT251",        # Reversed
    "0355TNO521",       # O instead of 0
    "152تن8355",        # Arabic format correct
]

for test in test_cases:
    is_valid, formatted = validator.validate_and_format(test)
    print(f"\n'{test}' -> '{formatted}' | Valid: {is_valid}")
