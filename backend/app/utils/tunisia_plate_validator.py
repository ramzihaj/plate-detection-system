"""
Tunisian license plate validator and formatter.

Tunisian plate format: XXXTNXXXX
- First 3 characters: digits (0-9)
- 4-5: "TN" (fixed)
- Last 4 characters: digits (0-9)

Example: 199TN0199
"""

import re
from typing import Tuple


class TunisianPlateValidator:
    """Validate and format Tunisian license plates."""
    
    # OCR error correction mapping
    # Common misreadings: O/l/I/S/B/Z/G confusion with numbers
    OCR_ERROR_MAP = {
        'O': '0',  # O -> 0 (most common)
        'I': '1',  # I -> 1
        'L': '1',  # L -> 1
        'S': '5',  # S -> 5
        'B': '8',  # B -> 8
        'Z': '2',  # Z -> 2
        'G': '9',  # G -> 9
        'o': '0',  # lowercase o -> 0
        'i': '1',  # lowercase i -> 1
        'l': '1',  # lowercase l -> 1
        's': '5',  # lowercase s -> 5
        'b': '8',  # lowercase b -> 8
        'z': '2',  # lowercase z -> 2
        'g': '9',  # lowercase g -> 9
    }
    
    # Tunisian plate regex pattern
    TUNISIAN_PATTERN = re.compile(r'^(\d{3})TN(\d{4})$', re.IGNORECASE)
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def validate_and_format(self, text: str) -> Tuple[bool, str]:
        """
        Validate and format OCR text to Tunisian plate format.
        
        Args:
            text: Raw OCR text (may contain errors)
            
        Returns:
            Tuple of (is_valid: bool, formatted_text: str)
            - If valid Tunisian format: (True, "XXXTNXXXX")
            - Otherwise: (False, "cleaned_text")
        """
        if not text:
            return False, ""
        
        # Clean and normalize the text
        cleaned = self._clean_text(text)
        
        # Check if it matches Tunisian format
        if self.TUNISIAN_PATTERN.match(cleaned):
            return True, cleaned
        
        # Try to extract and fix Tunisian format
        fixed = self._extract_tunisian_format(cleaned)
        if fixed and self.TUNISIAN_PATTERN.match(fixed):
            return True, fixed
        
        return False, cleaned
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR text by removing spaces and applying error correction.
        
        Protects TN marker during cleaning process.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove spaces and special characters
        text = text.upper().replace(" ", "").replace("-", "")
        
        # Protect TN marker with placeholder
        text = text.replace("TN", "__TN__")
        
        # Apply OCR error correction only to non-TN characters
        corrected = ""
        for char in text:
            if char in self.OCR_ERROR_MAP:
                corrected += self.OCR_ERROR_MAP[char]
            else:
                corrected += char
        
        # Restore TN marker
        corrected = corrected.replace("__TN__", "TN")
        
        return corrected
    
    def _extract_tunisian_format(self, text: str) -> str:
        """
        Extract and format text to Tunisian plate format.
        
        Handles cases like:
        - "199TN199" -> "199TN0199"
        - "199TN1990" -> "199TN0199"
        - "199T1N99" -> "199TN0199"
        
        Args:
            text: Cleaned text
            
        Returns:
            Formatted text or empty string if extraction fails
        """
        # Already in correct format
        if self.TUNISIAN_PATTERN.match(text):
            return text
        
        # Find TN marker position
        tn_pos = text.find("TN")
        if tn_pos < 0:
            return ""
        
        # Extract parts: before TN, TN itself, after TN
        before_tn = text[:tn_pos]
        after_tn = text[tn_pos + 2:]
        
        # Extract digits only
        before_digits = ''.join(c for c in before_tn if c.isdigit())[-3:]  # Last 3 digits
        after_digits = ''.join(c for c in after_tn if c.isdigit())[:4]      # First 4 digits
        
        # Format with proper padding
        if len(before_digits) == 3 and len(after_digits) == 4:
            return f"{before_digits}TN{after_digits}"
        
        # Handle incomplete numbers
        if len(before_digits) < 3:
            before_digits = before_digits.zfill(3)
        if len(after_digits) < 4:
            after_digits = after_digits.zfill(4)
        
        return f"{before_digits}TN{after_digits}"
    
    def is_valid_tunisian_plate(self, text: str) -> bool:
        """
        Check if text is a valid Tunisian plate format.
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid Tunisian format, False otherwise
        """
        is_valid, _ = self.validate_and_format(text)
        return is_valid


# Singleton instance
_validator = None


def get_tunisia_validator() -> TunisianPlateValidator:
    """Get singleton instance of TunisianPlateValidator."""
    global _validator
    if _validator is None:
        _validator = TunisianPlateValidator()
    return _validator
