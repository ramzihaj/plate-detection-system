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
from datetime import datetime

from format_tun_plate import format_tunisian_plate_cam_center,format_tunisian_plate_cam_right,format_tunisian_plate_cam_left
app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/")
async def home():
    return FileResponse("templates/index.html")

image_dir = r"C:\Users\PCS\Desktop\PFA projet\Backend\static\images\center"

# Chargement du modèle
try:
    model = YOLO(r"C:\Users\PCS\Desktop\PFA projet\Backend\Model\best002.pt")
    print("✅ Modèle YOLO chargé avec succès.")
except Exception as e:
    logging.error(f"❌ Erreur de chargement du modèle: {e}")
    raise e

reader = easyocr.Reader(['en'])
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
                        texts = reader.readtext(gray_plate, detail=0)
                        print(f"📝 Texte détecté brut: {texts}")

                        if texts:
                            formatted_plate = format_tunisian_plate_cam_center(texts)

                            if formatted_plate not in detected_plates:
                                detected_plates.append(formatted_plate)

                            cv2.putText(frame, formatted_plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            image_base64 = base64.b64encode(buffer).decode()

            # data = {
            #     "filename": image_name,
            #     "plates": detected_plates,
            #     "image": image_base64
            # }
            now = datetime.now()
            date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")  # format : 2025-04-15 21:40:12

            data = {
                "filename": image_name,
                "plates": detected_plates,
                "plate_count": len(detected_plates),
                "datetime": date_time_str,
                "image": image_base64
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"❌ Erreur lors du traitement de {image_name}: {e}")
            await websocket.send_text(json.dumps({"error": str(e), "filename": image_name}))
