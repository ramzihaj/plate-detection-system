import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import sys
import json
import os
import logging
import base64

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# Chemin du modèle YOLOv8 (relatif)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best002.pt")

# Vérifier l'existence du fichier modèle
if not os.path.isfile(MODEL_PATH):
    logging.error(f"❌ Le fichier modèle n'existe pas: {MODEL_PATH}")
    sys.exit(1)

# Charger le modèle YOLOv8
try:
    model = YOLO(MODEL_PATH)
    logging.info("✅ Modèle YOLO chargé avec succès.")
except Exception as e:
    logging.error(f"❌ Erreur de chargement du modèle: {e}")
    sys.exit(1)

# Initialiser EasyOCR
reader = easyocr.Reader(['en'], gpu=False)
logging.info("✅ EasyOCR initialisé.")

def format_tunisian_plate(texts):
    """Formater le texte pour correspondre au format XXX TN YYYY."""
    digits = []
    for text in texts:
        # Remplacer les caractères confondus
        text = (text.replace('L', '4')
                    .replace('I', '1')
                    .replace('O', '0')
                    .replace('Z', '2')
                    .replace('S', '5')
                    .replace('R', '4'))
        for char in text:
            if char.isdigit():
                digits.append(char)

    logging.info(f"📝 Tous les chiffres: {digits}")

    if len(digits) < 3:
        logging.warning("⚠️ Pas assez de chiffres pour formater une plaque")
        return "UNKNOWN"

    first_part = ''.join(digits[:3]) if len(digits) >= 3 else ''.join(digits).ljust(3, '0')
    if len(digits) >= 7:
        last_part = ''.join(digits[-4:])
    elif len(digits) >= 4:
        last_part = ''.join(digits[-4:]).rjust(4, '0')
    else:
        last_part = ''.join(digits[3:]).rjust(4, '0') if len(digits) > 3 else '0000'

    formatted_plate = f"{first_part} TN {last_part}"
    logging.info(f"📝 Plaque formatée: {formatted_plate}")
    return formatted_plate

def preprocess_roi(roi):
    """Prétraiter la ROI pour EasyOCR."""
    gray_plate = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    alpha = 1.2  # Contraste
    beta = 20    # Luminosité
    gray_plate = cv2.convertScaleAbs(gray_plate, alpha=alpha, beta=beta)
    gray_plate = cv2.GaussianBlur(gray_plate, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_plate = clahe.apply(gray_plate)
    scale_factor = 3
    gray_plate_scaled = cv2.resize(gray_plate, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    return gray_plate_scaled

def process_image(image_path, output_path):
    """Traiter une image pour détecter les plaques."""
    try:
        image_path = os.path.normpath(image_path)
        output_path = os.path.normpath(output_path)

        logging.info(f"📂 Tentative de lecture de l'image: {image_path}")
        if not os.path.isfile(image_path):
            logging.error(f"❌ L'image n'existe pas: {image_path}")
            return {"error": f"L'image n'existe pas: {image_path}"}

        image = cv2.imread(image_path)
        if image is None:
            logging.error(f"❌ Impossible de lire l'image: {image_path}")
            return {"error": f"Impossible de lire l'image: {image_path}"}

        results = model.predict(image, conf=0.2)
        detected_plates = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            logging.info(f"🔎 {len(boxes)} détections trouvées par YOLO.")

            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                margin = 50
                x1, y1, x2, y2 = x1 - margin, y1 - margin, x2 + margin, y2 + margin
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
                plate_roi = image[y1:y2, x1:x2]

                if plate_roi.size != 0:
                    gray_plate_scaled = preprocess_roi(plate_roi)
                    texts = reader.readtext(gray_plate_scaled, detail=0, min_size=10, text_threshold=0.7)
                    logging.info(f"📝 Texte détecté brut: {texts}")

                    if texts:
                        formatted_plate = format_tunisian_plate(texts)
                        if formatted_plate != "UNKNOWN" and not any(p["text"] == formatted_plate for p in detected_plates):
                            detected_plates.append({
                                "text": formatted_plate,
                                "confidence": float(box[4]) if len(box) > 4 else 0.9,
                                "bbox": [x1, y1, x2, y2]
                            })
                            cv2.putText(image, formatted_plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imwrite(output_path, image)
        logging.info(f"✅ Image annotée sauvegardée: {output_path}")
        return {
            "plates": detected_plates,
            "annotated_file": output_path
        }
    except Exception as e:
        logging.error(f"❌ Erreur lors du traitement de l'image: {e}")
        return {"error": str(e)}

def process_video(video_path, output_path):
    """Traiter une vidéo pour détecter les plaques."""
    try:
        video_path = os.path.normpath(video_path)
        output_path = os.path.normpath(output_path)

        logging.info(f"📂 Tentative de lecture de la vidéo: {video_path}")
        if not os.path.isfile(video_path):
            logging.error(f"❌ La vidéo n'existe pas: {video_path}")
            return {"error": f"La vidéo n'existe pas: {video_path}"}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logging.error(f"❌ Impossible d'ouvrir la vidéo: {video_path}")
            return {"error": f"Impossible d'ouvrir la vidéo: {video_path}"}

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        detected_plates = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model.predict(frame, conf=0.2)
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box[:4])
                    margin = 50
                    x1, y1, x2, y2 = x1 - margin, y1 - margin, x2 + margin, y2 + margin
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                    plate_roi = frame[y1:y2, x1:x2]

                    if plate_roi.size != 0:
                        gray_plate_scaled = preprocess_roi(plate_roi)
                        texts = reader.readtext(gray_plate_scaled, detail=0, min_size=10, text_threshold=0.7)
                        if texts:
                            formatted_plate = format_tunisian_plate(texts)
                            if formatted_plate != "UNKNOWN" and not any(p["text"] == formatted_plate for p in detected_plates):
                                detected_plates.append({
                                    "text": formatted_plate,
                                    "confidence": float(box[4]) if len(box) > 4 else 0.9,
                                    "bbox": [x1, y1, x2, y2]
                                })
                                cv2.putText(frame, formatted_plate, (x1, y1 - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            out.write(frame)

        cap.release()
        out.release()
        logging.info(f"✅ Vidéo annotée sauvegardée: {output_path}")
        return {
            "plates": detected_plates,
            "annotated_file": output_path
        }
    except Exception as e:
        logging.error(f"❌ Erreur lors du traitement de la vidéo: {e}")
        return {"error": str(e)}

def process_frame(frame_data):
    """Traiter une frame webcam pour détecter les plaques."""
    try:
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            logging.error("❌ Impossible de décoder la frame")
            return {"error": "Impossible de décoder la frame"}

        results = model.predict(frame, conf=0.2)
        detected_plates = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            logging.info(f"🔎 {len(boxes)} détections trouvées par YOLO.")

            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                margin = 50
                x1, y1, x2, y2 = x1 - margin, y1 - margin, x2 + margin, y2 + margin
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                plate_roi = frame[y1:y2, x1:x2]

                if plate_roi.size != 0:
                    gray_plate_scaled = preprocess_roi(plate_roi)
                    texts = reader.readtext(gray_plate_scaled, detail=0, min_size=10, text_threshold=0.7)
                    logging.info(f"📝 Texte détecté brut: {texts}")

                    if texts:
                        formatted_plate = format_tunisian_plate(texts)
                        if formatted_plate != "UNKNOWN" and not any(p["text"] == formatted_plate for p in detected_plates):
                            detected_plates.append({
                                "text": formatted_plate,
                                "confidence": float(box[4]) if len(box) > 4 else 0.9,
                                "bbox": [x1, y1, x2, y2]
                            })
                            cv2.putText(frame, formatted_plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        annotated_frame = base64.b64encode(buffer).decode()
        return {
            "plates": detected_plates,
            "annotated_frame": annotated_frame
        }
    except Exception as e:
        logging.error(f"❌ Erreur lors du traitement de la frame: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "image":
        input_path, output_path = sys.argv[2], sys.argv[3]
        result = process_image(input_path, output_path)
        print(json.dumps(result))
    elif mode == "video":
        input_path, output_path = sys.argv[2], sys.argv[3]
        result = process_video(input_path, output_path)
        print(json.dumps(result))
    elif mode == "frame":
        frame_data = sys.stdin.read()
        result = process_frame(frame_data)
        print(json.dumps(result))
