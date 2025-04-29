import cv2
import threading
import base64
import json
import time
from queue import Queue
from ultralytics import YOLO
import easyocr
from format_tun_plate import format_tunisian_plate_cam_center

class VideoProcessor:
    def __init__(self, video_source):
        self.video_source = video_source
        self.model = YOLO("Model/best002.pt")
        self.reader = easyocr.Reader(['en'])
        self.frame_queue = Queue(maxsize=1)
        self.result_queue = Queue(maxsize=1)
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.read_video, daemon=True).start()
        threading.Thread(target=self.process_frames, daemon=True).start()

    def stop(self):
        self.running = False

    def read_video(self):
        cap = cv2.VideoCapture(self.video_source)
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            time.sleep(1 / 30)  # Ajuste à la cadence de la vidéo
        cap.release()

    def process_frames(self):
        detected_plates = []
        while self.running:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get()
                # frame = cv2.rotate(frame, cv2.ROTATE_180)

                results = self.model(frame)[0]
                for box in results.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    roi = frame[y1:y2, x1:x2]
                    if roi.size != 0:
                        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        texts = self.reader.readtext(gray, detail=0)
                        if texts:
                            plate = format_tunisian_plate_cam_center(texts)
                            if plate not in detected_plates:
                                detected_plates.append(plate)
                            cv2.putText(frame, plate, (x1, y1 - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode()

                data = {
                    "plates": detected_plates,
                    "image": image_base64
                }

                if not self.result_queue.full():
                    self.result_queue.put(data)

    def get_latest_result(self):
        if not self.result_queue.empty():
            return self.result_queue.get()
        return None
