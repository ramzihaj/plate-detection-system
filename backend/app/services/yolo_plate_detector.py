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
        2. ../model/best002.pt (primary - relative to backend dir)
        3. model/best002.pt (from project root)
        4. Absolute path calculations
        5. yolov8n (default nano model)
        
        Args:
            model_path: Optional explicit path to model
            
        Returns:
            Loaded YOLO model
        """
        # Explicit path provided
        if model_path and os.path.exists(model_path):
            print(f"[YOLO] ✅ Loading model from: {model_path}")
            return YOLO(model_path)

        # Search for custom models - ORDERED BY PRIORITY
        # When running from backend/app/services/, ../model/best002.pt is correct
        candidates = [
            "../model/best002.pt",      # Most common when running from backend
            "../../model/best002.pt",   # From nested app/services directory
            "model/best002.pt",         # From project root
            "backend/model/best002.pt", # Alternative
            "../model/best.pt",
            "model/best.pt",
        ]

        print(f"[YOLO] Searching for best002.pt model...")
        for candidate in candidates:
            if os.path.exists(candidate):
                abs_path = os.path.abspath(candidate)
                print(f"[YOLO] ✅ Found custom model: {candidate}")
                print(f"[YOLO]    Size: {os.path.getsize(candidate) / (1024*1024):.1f} MB")
                try:
                    model = YOLO(candidate)
                    print(f"[YOLO] ✅ Successfully loaded best002.pt (optimized for plates)")
                    return model
                except Exception as e:
                    print(f"[YOLO] ⚠️ Failed to load {candidate}: {e}")
                    continue

        # Fallback to default
        print("[YOLO] ⚠️ Using default model: yolov8n (not optimized for plates)")
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
                    raw_text = self._extract_text_from_plate(plate_region)

                    # Validate and format Tunisian format
                    is_valid, formatted_text = self.validator.validate_and_format(raw_text)

                    # Always use the formatted text (whether valid or not)
                    # The validator will clean and attempt to fix the format
                    detections.append(PlateDetection(
                        plate_text=formatted_text if formatted_text else raw_text,
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
        
        Optimized parameters for license plate text extraction.
        
        Args:
            plate_image: Cropped plate image
            
        Returns:
            Extracted text string
        """
        if plate_image is None or plate_image.size == 0:
            return ""

        # Preprocess plate for OCR
        processed = self._preprocess_plate(plate_image)

        try:
            # EasyOCR with optimized parameters for plate detection
            # - paragraph=False: Better for single-line text
            # - min_size: Filter out very small noise
            # - batch_size: Can improve performance on multiple lines
            results = self.reader.readtext(
                processed,
                detail=1,
                paragraph=False,
                batch_size=1
            )

            if not results:
                return ""

            # Collect all text blocks
            text_blocks = []
            for bbox, text, confidence in results:
                # Keep blocks with at least 15% confidence (very permissive)
                if confidence > 0.15 and text.strip():
                    text_blocks.append(text.strip())
                    if confidence < 0.5:  # Log weak detections
                        print(f"[OCR] Weak detection: '{text}' ({confidence:.0%})")

            if not text_blocks:
                return ""

            # Join all detected text blocks
            extracted = "".join(text_blocks)
            
            print(f"[OCR] Extracted: '{extracted}' ({len(text_blocks)} blocks, raw: {len(results)} detections)")
            
            return extracted

        except Exception as e:
            print(f"[OCR] Error: {str(e)}")
            return ""

    def _preprocess_plate(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR.
        
        Simplified preprocessing that preserves image clarity:
        1. Convert to grayscale
        2. 3x upscaling for better character clarity
        3. Subtle contrast enhancement
        
        Args:
            plate_image: Input plate image
            
        Returns:
            Preprocessed image
        """
        if plate_image is None or plate_image.size == 0:
            return plate_image

        # Convert to grayscale
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image

        # Upscale 3x for better character clarity
        h, w = gray.shape[:2]
        upscaled = cv2.resize(gray, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)

        # Subtle contrast enhancement (avoid over-processing)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(upscaled)

        return enhanced

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
