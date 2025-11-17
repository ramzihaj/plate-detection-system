"""
Tunisian license plate validator and formatter.

Tunisian plate format: XXXTNXXXX
- First 3 characters: digits (0-9)
- 4-5: "TN" (fixed) or Arabic equivalent (ت ن)
- Last 4 characters: digits (0-9)

Example: 199TN0199
Arabic variant: 199تن0199 (will be converted to 199TN0199)
"""

import re
from typing import Tuple


class TunisianPlateValidator:
    """Validate and format Tunisian license plates."""
    
    # Arabic characters for Tunisia country code
    ARABIC_TA = 'ت'  # Arabic ta (equivalent to 'T')
    ARABIC_NOON = 'ن'  # Arabic noon (equivalent to 'N')
    
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
    
    def format_with_spaces(self, text: str) -> str:
        """
        Format valid Tunisian plate with spaces (XXX TN XXXX).
        
        Args:
            text: Tunisian plate text (with or without spaces)
            
        Returns:
            Formatted text with spaces
        """
        # Clean and validate first
        is_valid, formatted = self.validate_and_format(text)
        
        if not is_valid:
            return formatted
        
        # Add spaces for display: XXX TN XXXX
        # Remove any existing spaces first
        clean = formatted.replace(" ", "")
        if len(clean) == 9 and clean[3:5].upper() == "TN":
            return f"{clean[:3]} TN {clean[5:]}"
        
        return formatted
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR text by removing spaces and applying error correction.
        
        Handles both Latin (TN) and Arabic (تن) country markers.
        Removes all Arabic characters and converts Arabic numerals.
        Protects TN marker during cleaning process.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text with TN marker
        """
        # Remove spaces and special characters
        text = text.upper().replace(" ", "").replace("-", "")
        
        # Replace Arabic numerals with Latin equivalents
        # ٠=0, ١=1, ٢=2, ٣=3, ٤=4, ٥=5, ٦=6, ٧=7, ٨=8, ٩=9
        arabic_numerals = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        for arabic, latin in arabic_numerals.items():
            text = text.replace(arabic, latin)
        
        # Replace Arabic characters with Latin equivalents
        # ت (ta) -> T, ن (noon) -> N
        text = text.replace(self.ARABIC_TA, 'T').replace(self.ARABIC_NOON, 'N')
        
        # Remove other Arabic characters that are OCR artifacts
        # ك ل م ه ي ر و ة ا ب ج د ف ق ص ش ض ظ ع غ خ
        arabic_chars = 'كلمهيروةابجدفقصشضظعغخ'
        for char in arabic_chars:
            text = text.replace(char, '')
        
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
        - "0355TNN521" -> "355TN0521" (partial recovery)
        
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
            # If no TN found, try to find any T and N separately
            t_pos = text.find("T")
            n_pos = text.find("N", t_pos + 1) if t_pos >= 0 else -1
            if t_pos >= 0 and n_pos > t_pos:
                # Reconstruct with TN marker
                before_tn = text[:t_pos]
                after_tn = text[n_pos + 1:]
                text = before_tn + "TN" + after_tn
                tn_pos = len(before_tn)
            else:
                return ""
        
        # Extract parts: before TN, TN itself, after TN
        before_tn = text[:tn_pos]
        after_tn = text[tn_pos + 2:]
        
        # Extract digits only
        before_digits = ''.join(c for c in before_tn if c.isdigit())
        after_digits = ''.join(c for c in after_tn if c.isdigit())
        
        # Take last 3 digits from before part (in case of leading artifacts)
        before_digits = before_digits[-3:] if len(before_digits) >= 3 else before_digits
        # Take first 4 digits from after part (in case of trailing artifacts)
        after_digits = after_digits[:4] if len(after_digits) >= 4 else after_digits
        
        # Format with proper padding
        if len(before_digits) == 3 and len(after_digits) == 4:
            return f"{before_digits}TN{after_digits}"
        
        # Handle incomplete numbers - pad with zeros
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
