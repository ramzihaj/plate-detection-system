from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import base64
import os
import logging
import json
import asyncio
import re

app = FastAPI()

# 📁 Dossier frontend
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/")
async def home():
    return FileResponse("templates/index.html")

# 📂 Répertoire contenant les images
image_dir = r"C:\Users\PCS\Desktop\PFA projet\Backend\static\images2"

# 📦 Chargement du modèle YOLO
try:
    model = YOLO(r"C:\Users\PCS\Desktop\PFA projet\Backend\Model\best002.pt")
    print("✅ Modèle YOLO chargé avec succès.")
except Exception as e:
    logging.error(f"❌ Erreur de chargement du modèle: {e}")
    raise e

# 🔤 Initialisation EasyOCR
reader = easyocr.Reader(['en','ar'])

# 🔧 Fonctions de nettoyage et formatage

def extract_valid_numbers(texts):
    digits_only = []
    for item in texts:
        # Conversion chiffres arabes vers latins
        arabic_to_latin = item.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
        # Extraction groupes de 3 à 5 chiffres
        found = re.findall(r'\d{3,5}', arabic_to_latin)
        digits_only.extend(found)
    return digits_only

def clean_and_format_text(texts):
    numbers = extract_valid_numbers(texts)

    if len(numbers) == 1:
        return f"TN {numbers[0]}"
    elif len(numbers) >= 2:
        shorter = min(numbers, key=len)
        longer = max(numbers, key=len)
        return f"{shorter} TN {longer}" if len(shorter) <= len(longer) else f"{longer} TN {shorter}"
    else:
        return ""

def strict_clean(texts):
    cleaned = []
    for text in texts:
        text = re.sub(r'[^\w\d\s]', '', text)  # Supprimer caractères spéciaux
        text = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))  # chiffres arabes → latins
        cleaned.append(text)
    return cleaned

# 📡 WebSocket pour le streaming
@app.websocket("/ws")
async def detect_images(websocket: WebSocket):
    await websocket.accept()
    detected_plates = []

    if not os.path.isdir(image_dir):
        await websocket.send_text(json.dumps({"error": "Dossier d'images introuvable"}))
        return

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_files:
        await websocket.send_text(json.dumps({"error": "Aucune image trouvée"}))
        return

    for image_name in image_files:
        image_path = os.path.join(image_dir, image_name)
        frame = cv2.imread(image_path)

        if frame is None:
            logging.error(f"❌ Erreur lors du chargement de l'image {image_name}.")
            continue
        else:
            print(f"✅ Image {image_name} chargée avec succès.")

        try:
            results = model(frame)
            print(f"🔎 {len(results)} détections trouvées par YOLO dans {image_name}.")

            for result in results:
                for box in result.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    plate_roi = frame[y1:y2, x1:x2]

                    if plate_roi.size != 0:
                        gray_plate = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
                        raw_texts = reader.readtext(gray_plate, detail=0)
                        texts = strict_clean(raw_texts)
                        print(f"📝 Texte nettoyé : {texts}")

                        plate_text = clean_and_format_text(texts)
                        print(f"📝 Texte formaté : {plate_text}")

                        if plate_text and plate_text not in detected_plates:
                            detected_plates.append(plate_text)

                        if plate_text:
                            cv2.putText(frame, plate_text, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode()

            data = {
                "filename": image_name,
                "plates": detected_plates,
                "image": image_base64
            }

            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"❌ Erreur lors du traitement de {image_name}: {e}")
            await websocket.send_text(json.dumps({"error": str(e), "filename": image_name}))