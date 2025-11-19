#!/usr/bin/env python3
"""
OCR Digit Confusion Map - Corrects common OCR misreadings for Tunisian plates
"""

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
}

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
        Corrected character (digit, letter, or original)
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
    
    Args:
        texts: List of text strings from OCR
        
    Returns:
        List of corrected digits/letters
    """
    result = []
    
    for text in texts:
        for char in text:
            corrected = correct_ocr_digit(char)
            result.append(corrected)
    
    return result
