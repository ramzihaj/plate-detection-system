import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import sys
import json
import os
import logging
from datetime import datetime

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Chemin du modèle YOLOv8 (relatif)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best002.pt")

# Vérifier l'existence du fichier modèle
if not os.path.isfile(MODEL_PATH):
    logging.error(f"❌ Le fichier modèle n'existe pas: {MODEL_PATH}")
    sys.exit(1)

# Charger le modèle une seule fois au démarrage
model = YOLO(MODEL_PATH)
logging.info("✅ Modèle YOLO chargé avec succès.")

# Initialiser EasyOCR avec 'en' et 'ar'
reader = easyocr.Reader(['en', 'ar'], gpu=False)
logging.info("✅ EasyOCR initialisé sans GPU (langues: en, ar).")

def format_tunisian_plate(texts):
    if not texts:
        logging.warning("⚠️ Aucun texte détecté par EasyOCR")
        return "UNKNOWN"

    # Trier par confiance et prendre le meilleur
    texts = sorted(texts, key=lambda x: x[2], reverse=True)
    text = texts[0][1]
    confidence = texts[0][2]
    logging.info(f"📝 Texte sélectionné (confiance {confidence:.2f}): {text}")

    # Extraire les chiffres caractère par caractère
    digits = []
    for char in text:
        char = (char.replace('L', '4')
                .replace('I', '1')
                .replace('O', '0')
                .replace('Z', '2')
                .replace('S', '5')
                .replace('R', '4'))
        if char.isdigit():
            digits.append(char)

    logging.info(f"📝 Chiffres extraits: {digits}")
    if len(digits) < 6:
        logging.warning("⚠️ Pas assez de chiffres pour formater une plaque")
        return "UNKNOWN"

    # Partie droite : derniers 4 chiffres
    right_digits = digits[-4:]
    if len(right_digits) != 4:
        logging.warning("⚠️ Partie droite doit contenir exactement 4 chiffres")
        return "UNKNOWN"
    right_value = int(''.join(right_digits))
    if right_value < 1000 or right_value > 9999:
        logging.warning(f"⚠️ Valeur de la partie droite invalide: {right_value} (doit être entre 1000 et 9999)")
        return "UNKNOWN"

    # Partie gauche : 2 ou 3 chiffres avant les 4 derniers
    left_digits = digits[:-4]
    if len(left_digits) < 2 or len(left_digits) > 3:
        logging.warning(f"⚠️ Partie gauche doit contenir 2 ou 3 chiffres, trouvé: {len(left_digits)}")
        return "UNKNOWN"
    left_value = int(''.join(left_digits))
    if left_value < 10 or left_value > 260:
        logging.warning(f"⚠️ Valeur de la partie gauche invalide: {left_value} (doit être entre 10 et 260)")
        return "UNKNOWN"

    # Formater la plaque
    left_part = ''.join(left_digits).rjust(3, '0')
    right_part = ''.join(right_digits)
    formatted_plate = f"{left_part} TN {right_part}"
    logging.info(f"📝 Plaque formatée: {formatted_plate}")
    return formatted_plate

def preprocess_roi(roi):
    gray_plate = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray_plate = cv2.bilateralFilter(gray_plate, 9, 75, 75)  # Réduire bruit
    alpha = 1.5
    beta = 30
    gray_plate = cv2.convertScaleAbs(gray_plate, alpha=alpha, beta=beta)
    gray_plate = cv2.adaptiveThreshold(
        gray_plate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    scale_factor = 3.0  # Augmenter résolution
    gray_plate_scaled = cv2.resize(gray_plate, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    return gray_plate_scaled

def is_frame_sharp(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var > 50  # Réduire seuil

def process_image(image_path, output_path):
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

        scale_factor = 0.5
        image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        image = cv2.convertScaleAbs(image, alpha=1.2, beta=20)

        results = model.predict(image, conf=0.5, verbose=False)  # Augmenter conf
        detected_plates = []

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            logging.info(f"🔎 {len(boxes)} détections trouvées par YOLO.")

            for box in boxes:
                x1, y1, x2, y2 = map(int, box[:4])
                margin = int(20 * scale_factor)  # Ajuster marge
                x1, y1, x2, y2 = x1 - margin, y1 - margin, x2 + margin, y2 + margin
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(int(image.shape[1]), x2), min(int(image.shape[0]), y2)
                plate_roi = image[y1:y2, x1:x2]

                if plate_roi.size != 0:
                    cv2.imwrite(f"debug_roi_{x1}_{y1}.png", plate_roi)
                    gray_plate_scaled = preprocess_roi(plate_roi)
                    cv2.imwrite(f"debug_processed_roi_{x1}_{y1}.png", gray_plate_scaled)

                    texts = reader.readtext(
                        gray_plate_scaled,
                        detail=1,
                        min_size=8,  # Réduire pour petits textes
                        text_threshold=0.8,  # Moins strict
                        low_text=0.3,
                        mag_ratio=2.0,
                        allowlist='0123456789TN'
                    )
                    logging.info(f"📝 Texte détecté brut avec confiance: {[(text, conf) for _, text, conf in texts]}")

                    if texts:
                        formatted_plate = format_tunisian_plate(texts)
                        if formatted_plate != "UNKNOWN" and not any(p["text"] == formatted_plate for p in detected_plates):
                            detected_plates.append({
                                "text": formatted_plate,
                                "detectionDate": datetime.now().isoformat()
                            })
                            cv2.putText(image, formatted_plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        original_image = cv2.imread(image_path)
        original_height, original_width = original_image.shape[:2]
        image = cv2.resize(image, (original_width, original_height), interpolation=cv2.INTER_LINEAR)
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
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logging.info(f"📹 Vidéo contient {total_frames} frames, résolution: {width}x{height}, FPS: {fps}")

        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width * 0.5), int(height * 0.5)))

        detected_plates = []
        frame_count = 0
        process_every_n_frames = 1  # Traiter chaque frame

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % process_every_n_frames == 0:
                cv2.imwrite(f"debug_frame_{frame_count}.png", frame)

            if frame_count % process_every_n_frames != 0 or not is_frame_sharp(frame):
                out.write(frame)
                continue

            frame = cv2.resize(frame, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_AREA)  # Réduire résolution
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=20)

            results = model.predict(frame, conf=0.5, verbose=False)
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                logging.info(f"🔎 {len(boxes)} détections trouvées par YOLO (frame {frame_count}).")

                for box in boxes:
                    x1, y1, x2, y2 = map(int, box[:4])
                    margin = int(20 * 0.3)
                    x1, y1, x2, y2 = x1 - margin, y1 - margin, x2 + margin, y2 + margin
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(int(frame.shape[1]), x2), min(int(frame.shape[0]), y2)
                    plate_roi = frame[y1:y2, x1:x2]

                    if plate_roi.size != 0:
                        cv2.imwrite(f"debug_roi_{frame_count}_{x1}_{y1}.png", plate_roi)
                        gray_plate_scaled = preprocess_roi(plate_roi)
                        cv2.imwrite(f"debug_processed_roi_{frame_count}_{x1}_{y1}.png", gray_plate_scaled)

                        texts = reader.readtext(
                            gray_plate_scaled,
                            detail=1,
                            min_size=8,
                            text_threshold=0.8,
                            low_text=0.3,
                            mag_ratio=2.0,
                            allowlist='0123456789TN'
                        )
                        logging.info(f"📝 Texte détecté brut (frame {frame_count}): {[(text, conf) for _, text, conf in texts]}")

                        if texts:
                            formatted_plate = format_tunisian_plate(texts)
                            if formatted_plate != "UNKNOWN" and not any(p["text"] == formatted_plate for p in detected_plates):
                                detected_plates.append({
                                    "text": formatted_plate,
                                    "detectionDate": datetime.now().isoformat()
                                })
                                cv2.putText(frame, formatted_plate, (x1, y1 - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            out.write(frame)

        cap.release()
        out.release()
        logging.info(f"✅ Vidéo annotée sauvegardée: {output_path}")

        # Filtrer les doublons similaires
        unique_plates = []
        seen_texts = set()
        for plate in detected_plates:
            if plate["text"] not in seen_texts:
                unique_plates.append(plate)
                seen_texts.add(plate["text"])
        logging.info(f"📝 {len(unique_plates)} plaques uniques après filtrage")

        return {
            "plates": unique_plates,
            "annotated_file": output_path
        }
    except Exception as e:
        logging.error(f"❌ Erreur lors du traitement de la vidéo: {e}")
        return {"error": str(e)}

def process_uploaded_file(file_path, output_dir):
    try:
        file_path = os.path.normpath(file_path)
        logging.info(f"📂 Tentative de traitement du fichier uploadé: {file_path}")
        if not os.path.isfile(file_path):
            logging.error(f"❌ Le fichier n'existe pas: {file_path}")
            return {"error": f"Le fichier n'existe pas: {file_path}"}

        ext = os.path.splitext(file_path)[1].lower()
        is_video = ext in ['.mp4', '.avi', '.mov']
        output_path = os.path.join(os.path.normpath(output_dir), f"annotated_{os.path.basename(file_path)}")

        if is_video:
            logging.info(f"📹 Détection de fichier vidéo: {file_path}")
            return process_video(file_path, output_path)
        else:
            logging.info(f"🖼️ Détection de fichier image: {file_path}")
            return process_image(file_path, output_path)

    except Exception as e:
        logging.error(f"❌ Erreur lors du traitement du fichier uploadé: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "image":
        input_path, output_path = sys.argv[2], sys.argv[3]
        result = process_image(input_path, output_path)
        logging.info(f"✅ Résultat image prêt: {json.dumps(result)}")
        print(json.dumps(result), flush=True)
    elif mode == "video":
        input_path, output_path = sys.argv[2], sys.argv[3]
        result = process_video(input_path, output_path)
        logging.info(f"✅ Résultat vidéo prêt: {json.dumps(result)}")
        print(json.dumps(result), flush=True)
    elif mode == "upload":
        input_path = sys.argv[2]
        output_dir = os.path.dirname(input_path)
        logging.info(f"Mode 'upload' activé avec fichier: {input_path}")
        result = process_uploaded_file(input_path, output_dir)
        logging.info(f"✅ Résultat upload prêt: {json.dumps(result)}")
        print(json.dumps(result), flush=True)
