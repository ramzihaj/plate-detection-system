"""
YOLO-based license plate detection module.

This module provides plate detection using YOLOv8 with:
- Automatic model loading (custom or default yolov8n)
- EasyOCR text extraction with preprocessing
- Tunisian plate format validation
- Visualization capabilities
"""

import os
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from ultralytics import YOLO
import easyocr
from ..utils.tunisia_plate_validator import TunisianPlateValidator


@dataclass
class PlateDetection:
    """Structured plate detection result."""
    plate_text: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]
    is_valid_format: bool
    raw_bbox: np.ndarray


class YOLOPlateDetector:
    """
    YOLO-based plate detector with Tunisian format validation.
    
    Features:
    - Auto-loads custom models or defaults to yolov8n
    - Supports model discovery from multiple locations
    - Preprocessing: 3x upscaling, CLAHE, bilateral filtering
    - OCR with confidence filtering (0.3+ threshold)
    - Validation against Tunisian plate format (XXXTNXXXX)
    """

    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.3):
        """
        Initialize YOLO detector.
        
        Args:
            model_path: Optional path to custom YOLO model
            confidence_threshold: Confidence threshold for detections (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.validator = TunisianPlateValidator()
        self.reader = easyocr.Reader(['en', 'ar'], gpu=False)  # CPU fallback for compatibility
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: Optional[str] = None) -> YOLO:
        """
        Load YOLO model with automatic fallback.
        
        Search order:
        1. Custom model_path (if provided)
        2. model/best002.pt (primary custom trained)
        3. backend/model/best002.pt (alternative location)
        4. model/best.pt (secondary custom)
        5. ../model/best.pt (alternative location)
        6. yolov8n (default nano model)
        
        Args:
            model_path: Optional explicit path to model
            
        Returns:
            Loaded YOLO model
        """
        # Explicit path provided
        if model_path and os.path.exists(model_path):
            print(f"[YOLO] Loading model from: {model_path}")
            return YOLO(model_path)

        # Search for custom models (best002.pt prioritized)
        candidates = [
            "model/best002.pt",
            "backend/model/best002.pt",
            "best002.pt",
            "model/best.pt",
            "backend/model/best.pt",
            "../model/best.pt",
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                print(f"[YOLO] Found custom model: {candidate}")
                return YOLO(candidate)

        # Fallback to default
        print("[YOLO] Using default model: yolov8n")
        return YOLO("yolov8n")

    def detect_plates(self, image: np.ndarray) -> List[PlateDetection]:
        """
        Detect license plates in image.
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            List of PlateDetection objects with text and validation
        """
        if image is None or image.size == 0:
            return []

        detections = []

        try:
            # YOLO inference
            results = self.model(image, conf=self.confidence_threshold, verbose=False)

            for result in results:
                for box in result.boxes:
                    confidence = float(box.conf[0])

                    if confidence < self.confidence_threshold:
                        continue

                    # Extract bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)

                    # Extract plate region
                    plate_region = image[y1:y2, x1:x2]

                    # Extract text from plate
                    plate_text = self._extract_text_from_plate(plate_region)

                    # Validate Tunisian format
                    is_valid, formatted_text = self.validator.validate_and_format(plate_text)

                    detections.append(PlateDetection(
                        plate_text=formatted_text if is_valid else plate_text,
                        confidence=confidence,
                        bounding_box=bbox,
                        is_valid_format=is_valid,
                        raw_bbox=box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], 'cpu') else box.xyxy[0]
                    ))

        except Exception as e:
            print(f"[YOLO] Detection error: {str(e)}")

        return detections

    def _extract_text_from_plate(self, plate_image: np.ndarray) -> str:
        """
        Extract text from plate image using OCR.
        
        Args:
            plate_image: Cropped plate image
            
        Returns:
            Extracted text string
        """
        if plate_image is None or plate_image.size == 0:
            return ""

        # Preprocess plate
        processed = self._preprocess_plate(plate_image)

        try:
            # OCR with confidence filtering
            results = self.reader.readtext(processed, detail=1)

            # Filter by confidence (0.3+) and extract text
            texts = [
                text for (bbox, text, confidence) in results
                if confidence > 0.3
            ]

            return "".join(texts).strip()

        except Exception as e:
            print(f"[OCR] Error: {str(e)}")
            return ""

    def _preprocess_plate(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR.
        
        Steps:
        1. 3x upscaling
        2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        3. Bilateral filtering
        4. Adaptive thresholding
        
        Args:
            plate_image: Input plate image
            
        Returns:
            Preprocessed image
        """
        if plate_image is None or plate_image.size == 0:
            return plate_image

        # Upscale 3x
        h, w = plate_image.shape[:2]
        upscaled = cv2.resize(plate_image, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)

        # Convert to grayscale
        gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY) if len(upscaled.shape) == 3 else upscaled

        # CLAHE for contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Bilateral filtering to preserve edges
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)

        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        return thresh

    def draw_detections(self, image: np.ndarray, detections: List[PlateDetection]) -> np.ndarray:
        """
        Draw detection boxes on image.
        
        Valid Tunisian plates: green box
        Invalid format: orange box
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Image with drawn boxes
        """
        result = image.copy()

        for detection in detections:
            x1, y1, x2, y2 = detection.bounding_box
            color = (0, 255, 0) if detection.is_valid_format else (0, 165, 255)  # Green or Orange
            thickness = 2

            # Draw box
            cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)

            # Draw text label
            label = f"{detection.plate_text} ({detection.confidence:.2f})"
            cv2.putText(result, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.8, color, 2)

        return result


def create_yolo_detector(model_path: Optional[str] = None) -> YOLOPlateDetector:
    """
    Factory function to create YOLO detector.
    
    Args:
        model_path: Optional path to custom model
        
    Returns:
        Initialized YOLOPlateDetector instance
    """
    return YOLOPlateDetector(model_path)
