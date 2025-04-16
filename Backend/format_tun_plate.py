def format_tunisian_plate_cam_center(texts):
    import re
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 tous les chiffres: {digits}")

    if len(digits) < 3 or len(digits) > 10:
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
    elif len(digits) == 8:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[4]}{digits[5]}{digits[6]}{digits[7]}"
    elif len(digits) == 9:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[5]}{digits[6]}{digits[7]}{digits[8]}"
    elif len(digits) == 10:
        return f"{digits[0]}{digits[1]}{digits[2]} TN {digits[6]}{digits[7]}{digits[8]}{digits[9]}"
def format_tunisian_plate_cam_right(texts):
    import re
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 tous les chiffres: {digits}")

    if len(digits) < 3 or len(digits) > 10:
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
def format_tunisian_plate_cam_left(texts):
    import re
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():
                characters.append(char)

    digits = [c for c in characters if c.isdigit()]
    print(f"📝 tous les chiffres: {digits}")

    if len(digits) < 3 or len(digits) > 7:
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
