#!/usr/bin/env python3
"""
Quick debug test for Arabic letter detection
"""

text = 'نان 2]2'

# Check character ranges
print(f"Text: '{text}'")
print("\nCharacter breakdown:")
for c in text:
    code = ord(c)
    is_arabic_letter = chr(0x0621) <= c <= chr(0x064A)
    print(f"  '{c}' (code: {code}) - Arabic letter: {is_arabic_letter}")

# Count
arabic_letters = sum(1 for c in text if chr(0x0621) <= c <= chr(0x064A))
total = len(text)
print(f"\nArabic letters: {arabic_letters}/{total} = {arabic_letters/total:.1%}")
print(f"Should reject if >60%: {arabic_letters/total > 0.6}")
