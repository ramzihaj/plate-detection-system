#!/usr/bin/env python3
"""
OCR Digit Confusion Map - Corrects common OCR misreadings for Tunisian plates
Enhanced to handle special symbols and reject invalid blocks
"""
import re

# Common OCR confusion for digits (especially on license plates)
DIGIT_CONFUSION_MAP = {
    '0': '0O',  # 0 can be confused with O
    '1': '1lI',  # 1 can be confused with l or I
    '2': '2Z',  # 2 can be confused with Z
    '3': '3',  # Usually OK
    '4': '4A',  # 4 can be confused with A
    '5': '5S',  # 5 can be confused with S
    '6': '6G',  # 6 can be confused with G
    '7': '7',  # Usually OK
    '8': '8B',  # 8 can be confused with B
    '9': '9g',  # 9 can be confused with g
}

# Special symbol corrections (common OCR misreadings on plates)
SYMBOL_CORRECTIONS = {
    ':': '5',   # Colon : looks like 5
    ';': '5',   # Semicolon ; looks like 5
    ')': '6',   # Parenthesis ) looks like 6
    ']': '1',   # Bracket ] looks like 1
    '[': '1',   # Bracket [ looks like 1
    '(': '8',   # Parenthesis ( looks like 8
    '}': '3',   # Brace } looks like 3
    '{': '8',   # Brace { looks like 8
    '!': '1',   # Exclamation ! looks like 1
    '@': '0',   # At sign @ looks like 0
    ',': '0',   # Comma , looks like 0
    '.': '0',   # Period . looks like 0
    '-': '1',   # Dash - looks like 1
    '=': '8',   # Equals = looks like 8
    '+': '1',   # Plus + looks like 1
    '*': '8',   # Asterisk * looks like 8
    '&': '8',   # Ampersand & looks like 8
}

def is_valid_plate_text(text):
    """
    Check if text block looks like it could be from a plate.
    Rejects blocks that:
    - Are mostly Arabic letters (>40% arabe + not having TN marker or numbers)
    - Have too much garbage/symbols and not enough valid plate content
    
    Args:
        text: Text string to validate
        
    Returns:
        True if block looks like it could be plate text, False otherwise
    """
    if not text or len(text.strip()) == 0:
        return False
    
    # Count different character types
    arabic_letters = sum(1 for c in text if chr(0x0621) <= c <= chr(0x064A))  # Arabic letters only
    arabic_numerals = sum(1 for c in text if chr(0x0660) <= c <= chr(0x0669))  # Arabic numerals ٠-٩
    english_digits = sum(1 for c in text if c.isdigit())
    english_letters = sum(1 for c in text if c.isalpha() and not (ord(c) >= 0x0600 and ord(c) <= 0x06FF))
    tn_marker = sum(1 for c in text if c in 'TNtn')
    
    total_chars = len(text)
    
    # If more than 40% is Arabic letters AND not a valid TN marker with numbers, reject
    if total_chars > 0 and arabic_letters / total_chars > 0.40:
        has_marker = 'T' in text or 'N' in text or 't' in text or 'n' in text
        has_numbers = english_digits + arabic_numerals > 0
        # Reject if mostly Arabic without proper TN marker + numbers
        if not (has_marker and has_numbers):
            return False
    
    # Must have at least 1 digit (English or Arabic) or English letters
    has_valid_content = (english_digits + arabic_numerals + english_letters + tn_marker) > 0
    if not has_valid_content:
        return False
    
    return True

def correct_ocr_digit(char):
    """
    Try to correct a single character to a digit if it looks like one.
    Handles:
    - Arabic numerals (٠-٩) conversion to English (0-9)
    - Arabic letters (ت ن) conversion to English (T N)
    - Letter confusion (O->0, I->1, Z->2, S->5, B->8, G->6)
    - Special symbols (:->5, )->6, ]->1, etc.)
    
    Args:
        char: Character that might be a confused digit, symbol, or Arabic character
        
    Returns:
        Digit string (0-9), letter, or original char if not correctable
    """
    # Convert Arabic numerals (٠-٩) to English numerals (0-9)
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    }
    if char in arabic_to_english:
        return arabic_to_english[char]
    
    # Convert Arabic letters to English (TN marker)
    if char == 'ت':
        return 'T'
    if char == 'ن':
        return 'N'
    
    char_upper = char.upper()
    
    # Direct mappings for letter->digit confusion
    letter_corrections = {
        'O': '0',  # Letter O -> 0
        'I': '1',  # Letter I -> 1
        'L': '1',  # Letter L -> 1
        'Z': '2',  # Letter Z -> 2
        'S': '5',  # Letter S -> 5
        'B': '8',  # Letter B -> 8
        'G': '6',  # Letter G -> 6
    }
    
    if char_upper in letter_corrections:
        return letter_corrections[char_upper]
    
    # Symbol corrections
    if char in SYMBOL_CORRECTIONS:
        return SYMBOL_CORRECTIONS[char]
    
    return char

def intelligently_extract_digits(texts):
    """
    Extract and correct digits from OCR texts.
    Filters out invalid blocks, corrects symbols and letter confusion.
    
    Args:
        texts: List of text strings from OCR
        
    Returns:
        List of corrected digits (only valid characters)
    """
    digits = []
    
    for text in texts:
        # Skip blocks that don't look like valid plate text
        if not is_valid_plate_text(text):
            print(f"[OCR_FILTER] Rejected block (invalid content): '{text}'")
            continue
        
        for char in text:
            corrected = correct_ocr_digit(char)
            
            # Keep only digits or TN markers after correction
            if corrected.isdigit():
                digits.append(corrected)
            elif corrected in 'TN':
                digits.append(corrected)
    
    return digits

# Test
if __name__ == '__main__':
    # Test case with typical OCR confusion
    texts = ['0O0', '2S2', '8B3', '5S']
    corrected = intelligently_extract_digits(texts)
    print(f'Texts: {texts}')
    print(f'Corrected digits: {corrected}')
