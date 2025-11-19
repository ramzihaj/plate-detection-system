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
    Returns only alphanumeric characters (digits and letters).
    
    Args:
        texts: List of text strings from OCR
        
    Returns:
        List of corrected alphanumeric characters
    """
    characters = []
    
    # First pass: correct all characters
    for text in texts:
        for char in text:
            corrected = correct_ocr_digit(char)
            # Keep alphanumeric characters only
            if corrected.isalnum():
                characters.append(corrected)
    
    return characters

def format_tunisian_plate_cam_center(characters):
    """
    Format Tunisian plate from detected characters (camera center view).
    Extracts 3 digits + TN + 4 digits from variable length input.
    
    Args:
        characters: List of alphanumeric characters from OCR
        
    Returns:
        Formatted plate string or "UNKNOWN" if invalid
    """
    # Extract only digits from characters
    digits = [c for c in characters if c.isdigit()]
    
    print(f"📝 All digits detected: {digits} (total: {len(digits)})")
    
    if len(digits) < 3 or len(digits) > 10:
        print(f"❌ Invalid digit count: {len(digits)}")
        return "UNKNOWN"
    
    # Format based on digit count
    if len(digits) == 3:
        return f"{digits[0]}{digits[1]} TN {digits[2]}"
    elif len(digits) == 4:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}"
    elif len(digits) == 5:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}"
    elif len(digits) == 6:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}{digits[5]}"
    elif len(digits) == 7:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}{digits[5]}{digits[6]}"
    elif len(digits) == 8:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[4]}{digits[5]}{digits[6]}{digits[7]}"
    elif len(digits) == 9:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[5]}{digits[6]}{digits[7]}{digits[8]}"
    elif len(digits) == 10:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[6]}{digits[7]}{digits[8]}{digits[9]}"

def format_tunisian_plate_cam_right(characters):
    """
    Format Tunisian plate from detected characters (camera right view).
    
    Args:
        characters: List of alphanumeric characters from OCR
        
    Returns:
        Formatted plate string or "UNKNOWN" if invalid
    """
    digits = [c for c in characters if c.isdigit()]
    
    print(f"📝 All digits detected: {digits} (total: {len(digits)})")
    
    if len(digits) < 3 or len(digits) > 10:
        print(f"❌ Invalid digit count: {len(digits)}")
        return "UNKNOWN"
    
    if len(digits) == 3:
        return f" TN {digits[0]}{digits[1]}{digits[2]}"
    elif len(digits) == 4:
        return f"TN {digits[0]}{digits[1]}{digits[2]}{digits[3]}"
    elif len(digits) == 5:
        return f"{digits[0]} TN {digits[1]}{digits[2]}{digits[3]}{digits[4]}"
    elif len(digits) == 6:
        return f"{digits[0]}{digits[1]} TN {digits[2]}{digits[3]}{digits[4]}{digits[5]}"
    elif len(digits) == 7:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}{digits[5]}{digits[6]}"
    elif len(digits) == 8:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[4]}{digits[5]}{digits[6]}{digits[7]}"
    elif len(digits) == 9:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[5]}{digits[6]}{digits[7]}{digits[8]}"
    elif len(digits) == 10:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[6]}{digits[7]}{digits[8]}{digits[9]}"

def format_tunisian_plate_cam_left(characters):
    """
    Format Tunisian plate from detected characters (camera left view).
    
    Args:
        characters: List of alphanumeric characters from OCR
        
    Returns:
        Formatted plate string or "UNKNOWN" if invalid
    """
    digits = [c for c in characters if c.isdigit()]
    
    print(f"📝 All digits detected: {digits} (total: {len(digits)})")
    
    if len(digits) < 3 or len(digits) > 7:
        print(f"❌ Invalid digit count: {len(digits)}")
        return "UNKNOWN"
    
    if len(digits) == 3:
        return f"{digits[0]}{digits[1]} TN {digits[2]}"
    elif len(digits) == 4:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}"
    elif len(digits) == 5:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}"
    elif len(digits) == 6:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}{digits[5]}"
    elif len(digits) == 7:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[3]}{digits[4]}{digits[5]}{digits[6]}"
