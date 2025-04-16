def format_tunisian_plate(texts):
    import re

    # 🧱 Étape 1 : Regrouper tous les caractères extraits dans un seul tableau
    characters = []
    for text in texts:
        for char in text:
            if char.isalnum():  # Garde uniquement les chiffres et lettres
                characters.append(char)

    # 🔍 Étape 2 : Garder uniquement les chiffres, dans l’ordre
    digits = [c for c in characters if c.isdigit()]

    # 📏 Étape 3 : Vérification de la longueur
    if len(digits) < 3 or len(digits) > 7:
        return "UNKNOWN"

    # 🧠 Étape 4 : Construction de la plaque selon le nombre de chiffres
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

def test_format_tunisian_plate():
    test_cases = [
        ["123TN4596"],             # Cas idéal : devrait retourner 123 TN 456
        ["1", "2", "3"],          # Pas assez de chiffres → UNKNOWN
        ["1", "2", "3", "4"],     # 4 chiffres → 123 TN 4
        ["a", "1", "%", "2", "3", "@", "4"],  # 123 TN 4 (caractères spéciaux ignorés)
        ["12A3", "4B5C", "D6E"],  # 123456 → 123 TN 456
        ["1919931"],              # 7 chiffres → 191 TN 9931
        ["LL22"],                 # Aucun chiffre → UNKNOWN
        ["12", "34", "56", "78"], # Trop de chiffres → UNKNOWN
        ["AB12TN34CD"],           # 1234 → 123 TN 4
        ["A1", "B2", "C3", "TN", "D4", "E5"], # 12345 → 123 TN 45
    ]

    for i, texts in enumerate(test_cases, 1):
        result = format_tunisian_plate(texts)
        print(f"Test {i}: Input = {texts} → Output = {result}")

# Appelle la fonction de test
test_format_tunisian_plate()
