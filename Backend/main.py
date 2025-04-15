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

# Initialisation FastAPI
app = FastAPI()

# 📁 Répertoire de templates (frontend)
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/")
async def home():
    return FileResponse("templates/index.html")

# 📂 Répertoire contenant les images
image_dir = r"C:\Users\PCS\Desktop\PFA projet\Backend\static\images"

# 📦 Chargement du modèle YOLO
try:
    model = YOLO(r"C:\Users\PCS\Desktop\PFA projet\Backend\Model\best002.pt")
    print("✅ Modèle YOLO chargé avec succès.")
except Exception as e:
    logging.error(f"❌ Erreur de chargement du modèle: {e}")
    raise e

# 🔤 Initialisation EasyOCR
reader = easyocr.Reader(['en','ar'])

# 📡 WebSocket pour le streaming
@app.websocket("/ws")
async def detect_images(websocket: WebSocket):
    await websocket.accept()
    detected_plates = []

    # 📁 Vérification du dossier
    if not os.path.isdir(image_dir):
        await websocket.send_text(json.dumps({"error": "Dossier d'images introuvable"}))
        return

    # 🖼️ Liste des fichiers image
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
                        texts = reader.readtext(gray_plate, detail=0)
                        print(f"📝 Texte détecté brut: {texts}")

                        if texts:
                            texts = [item for text in texts for item in text.split()]
                            print(f"📝 Texte après split: {texts}")

                            plate_text = " ".join(texts)
                            print(f"📝 plate_text: {plate_text}")

                            digits = [x for x in texts if x.isdigit()]
                            tn_text = [x for x in texts if not x.isdigit()]
                            print(f"📝 digits: {digits}")

                            if len(digits) == 1:
                                formatted_plate = f"TN {digits[0]}"
                            elif len(digits) == 2:
                                if len(digits[1]) <= len(digits[0]):
                                    formatted_plate = f"{digits[1]} TN {digits[0]}"
                                else:
                                    formatted_plate = f"{digits[0]} TN {digits[1]}"
                            elif len(digits) == 3:
                                if len(digits[0]) > len(digits[1]) and len(digits[0]) > len(digits[2]):
                                    formatted_plate = f"{digits[2]}{digits[1]} TN {digits[0]}"
                                elif len(digits[1]) > len(digits[0]) and len(digits[1]) > len(digits[2]):
                                    formatted_plate = f"{digits[2]}{digits[0]} TN {digits[1]}"
                                elif len(digits[2]) > len(digits[0]) and len(digits[2]) > len(digits[1]):
                                    formatted_plate = f"{digits[2]}{digits[0]} TN {digits[2]}"
                            else:
                                formatted_plate = plate_text

                            if formatted_plate not in detected_plates:
                                detected_plates.append(formatted_plate)

                            cv2.putText(frame, formatted_plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 📸 Encodage image + envoi WebSocket
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
