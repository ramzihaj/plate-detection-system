#!/usr/bin/env python3
"""
OCR Digit Confusion Map - Corrects common OCR misreadings
"""

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

def correct_ocr_digit(char):
    """
    Try to correct a single character to a digit if it looks like one.
    
    Args:
        char: Character that might be a confused digit
        
    Returns:
        Digit string (0-9) or original char if uncertain
    """
    char = char.upper()
    
    # Direct mappings for letter->digit confusion
    corrections = {
        'O': '0',  # Letter O -> 0
        'I': '1',  # Letter I -> 1
        'L': '1',  # Letter L -> 1
        'Z': '2',  # Letter Z -> 2
        'S': '5',  # Letter S -> 5
        'B': '8',  # Letter B -> 8
        'G': '6',  # Letter G -> 6
    }
    
    if char in corrections:
        return corrections[char]
    
    return char

def intelligently_extract_digits(texts):
    """
    Extract and correct digits from OCR texts.
    
    Args:
        texts: List of text strings from OCR
        
    Returns:
        List of corrected digits
    """
    digits = []
    
    for text in texts:
        for char in text:
            corrected = correct_ocr_digit(char)
            if corrected.isdigit():
                digits.append(corrected)
    
    return digits

# Test
if __name__ == '__main__':
    # Test case with typical OCR confusion
    texts = ['0O0', '2S2', '8B3', '5S']
    corrected = intelligently_extract_digits(texts)
    print(f'Texts: {texts}')
    print(f'Corrected digits: {corrected}')
