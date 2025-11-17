"""
Tunisian license plate formatter with camera perspective support.

Handles different camera angles:
- cam_center: Camera centered on plate
- cam_right: Camera positioned to the right
- cam_left: Camera positioned to the left
"""


def format_tunisian_plate_cam_center(texts):
    """
    Format Tunisian plate from center camera perspective.
    Format: XXX TN XXXX (7 digits total: 3 + 4)
    
    Args:
        texts: List of extracted text strings
        
    Returns:
        Formatted plate string (with spaces) or "UNKNOWN" if invalid
    """
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 Tous les chiffres (centre): {digits}")

    # Extract exactly 7 digits: first 3 are plate number, last 4 are serial
    if len(digits) >= 7:
        # Take first 3 for plate number
        plate_num = digits[0] + digits[1] + digits[2]
        # Take last 4 for serial
        serial = digits[-4] + digits[-3] + digits[-2] + digits[-1]
        return f"{plate_num} TN {serial}"
    
    return "UNKNOWN"


def format_tunisian_plate_cam_right(texts):
    """
    Format Tunisian plate from right camera perspective.
    Camera positioned to the right, may see partial plate.
    
    Args:
        texts: List of extracted text strings
        
    Returns:
        Formatted plate string (with spaces) or "UNKNOWN" if invalid
    """
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 Tous les chiffres (droite): {digits}")

    # From right side, try to extract 7 digits
    if len(digits) >= 7:
        plate_num = digits[0] + digits[1] + digits[2]
        serial = digits[-4] + digits[-3] + digits[-2] + digits[-1]
        return f"{plate_num} TN {serial}"
    elif len(digits) == 4:
        # Maybe only the TN XXXX part visible
        return f"TN {digits[0] + digits[1] + digits[2] + digits[3]}"
    
    return "UNKNOWN"


def format_tunisian_plate_cam_left(texts):
    """
    Format Tunisian plate from left camera perspective.
    Camera positioned to the left, may see partial plate.
    
    Args:
        texts: List of extracted text strings
        
    Returns:
        Formatted plate string (with spaces) or "UNKNOWN" if invalid
    """
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 Tous les chiffres (gauche): {digits}")

    # From left side, try to extract 7 digits
    if len(digits) >= 7:
        plate_num = digits[0] + digits[1] + digits[2]
        serial = digits[-4] + digits[-3] + digits[-2] + digits[-1]
        return f"{plate_num} TN {serial}"
    elif len(digits) == 3:
        # Maybe only the XXX TN part visible
        return f"{digits[0] + digits[1] + digits[2]} TN"
    
    return "UNKNOWN"


def format_tunisian_plate(texts, camera_position="center"):
    """
    Format Tunisian plate based on camera position.
    
    Args:
        texts: List of extracted text strings
        camera_position: "center", "right", or "left"
        
    Returns:
        Formatted plate string with spaces (XXX TN XXXX)
    """
    if camera_position == "right":
        return format_tunisian_plate_cam_right(texts)
    elif camera_position == "left":
        return format_tunisian_plate_cam_left(texts)
    else:  # Default to center
        return format_tunisian_plate_cam_center(texts)
