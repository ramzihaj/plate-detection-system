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
from ..utils.ocr_digit_corrector import intelligently_extract_digits, format_tunisian_plate_cam_center


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
            print(f"[DETECTION] ========== Starting Plate Detection ==========")
            print(f"[DETECTION] Step 1/5: Image input - Shape: {image.shape}, Type: {image.dtype}")
            results = self.model(image, conf=self.confidence_threshold, verbose=False)

            plate_count = sum(len(result.boxes) for result in results)
            print(f"[DETECTION] Step 2/5: YOLO detection - Found {plate_count} potential plate(s)")

            detection_idx = 0
            for result in results:
                for box in result.boxes:
                    detection_idx += 1
                    confidence = float(box.conf[0])

                    if confidence < self.confidence_threshold:
                        print(f"[DETECTION] Plate #{detection_idx}: Confidence {confidence:.2%} below threshold {self.confidence_threshold:.2%}, skipping")
                        continue

                    # Extract bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)
                    print(f"[DETECTION] Plate #{detection_idx}: Confidence {confidence:.2%}, BBox: ({x1}, {y1}, {x2}, {y2})")

                    # Extract plate region
                    plate_region = image[y1:y2, x1:x2]
                    print(f"[DETECTION]   ├─ Step 3/5: Plate ROI extracted - Size: {plate_region.shape}")

                    # Extract text from plate
                    raw_text = self._extract_text_from_plate(plate_region)
                    print(f"[DETECTION]   ├─ Step 4/5: OCR Complete")
                    print(f"[DETECTION]   │  └─ Raw extracted text: '{raw_text}'")

                    # Validate and format Tunisian format
                    is_valid, formatted_text = self.validator.validate_and_format(raw_text)
                    print(f"[DETECTION]   └─ Step 5/5: Validation & Formatting")
                    print(f"[DETECTION]      ├─ Stage 1 - Raw OCR:        '{raw_text}'")
                    print(f"[DETECTION]      ├─ Stage 2 - After clean:    '{self.validator._clean_text(raw_text)}'")
                    print(f"[DETECTION]      ├─ Stage 3 - After extract:  '{self.validator._extract_tunisian_format(self.validator._clean_text(raw_text))}'")
                    print(f"[DETECTION]      ├─ Stage 4 - Final format:   '{formatted_text}'")
                    print(f"[DETECTION]      ├─ Display format:           '{self.validator.format_with_spaces(formatted_text) if is_valid else formatted_text}'")
                    print(f"[DETECTION]      └─ Valid format:             {is_valid}")

                    # Always use the formatted text (whether valid or not)
                    # The validator will clean and attempt to fix the format
                    detections.append(PlateDetection(
                        plate_text=formatted_text if formatted_text else raw_text,
                        confidence=confidence,
                        bounding_box=bbox,
                        is_valid_format=is_valid,
                        raw_bbox=box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], 'cpu') else box.xyxy[0]
                    ))

            print(f"[DETECTION] ========== Detection Complete: {len(detections)} plate(s) processed ==========\n")

        except Exception as e:
            print(f"[YOLO] Detection error: {str(e)}")

        return detections

    def _extract_text_from_plate(self, plate_image: np.ndarray) -> str:
        """
        Extract text from plate image using OCR with intelligent digit correction.
        
        Optimized parameters for license plate text extraction.
        Applies OCR digit confusion correction for better accuracy.
        
        Args:
            plate_image: Cropped plate image
            
        Returns:
            Extracted text string with corrected digits
        """
        if plate_image is None or plate_image.size == 0:
            return ""

        # Preprocess plate for OCR
        processed = self._preprocess_plate(plate_image)

        try:
            # EasyOCR with optimized parameters for plate detection
            results = self.reader.readtext(
                processed,
                detail=1,
                paragraph=False,
                batch_size=1
            )

            if not results:
                print(f"[OCR] ❌ No text detected by EasyOCR")
                return ""

            print(f"[OCR] ========== TEXT EXTRACTION DETAILS ==========")
            print(f"[OCR] Total blocks detected by EasyOCR: {len(results)}")
            
            # Collect all text blocks
            text_blocks = []
            for idx, (bbox, text, confidence) in enumerate(results, 1):
                print(f"[OCR] Block #{idx}:")
                print(f"[OCR]   ├─ Raw text:     '{text}'")
                print(f"[OCR]   ├─ Confidence:   {confidence:.1%}")
                print(f"[OCR]   ├─ BBox:         {bbox}")
                
                if confidence > 0.10 and text.strip():
                    text_blocks.append(text.strip())
                    status = "✅ KEPT" if confidence >= 0.5 else "⚠️ WEAK"
                    print(f"[OCR]   └─ Status:       {status}")
                else:
                    print(f"[OCR]   └─ Status:       ❌ REJECTED")

            if not text_blocks:
                print(f"[OCR] ==========================================\n")
                return ""

            print(f"[OCR] ==========================================")
            print(f"[OCR] Blocks kept: {len(text_blocks)}")
            print(f"[OCR] Blocks list: {text_blocks}\n")
            
            # Apply character correction to get alphanumeric characters
            characters = intelligently_extract_digits(text_blocks)
            print(f"[OCR] Corrected characters: {characters}")
            
            # Format plate using camera center view algorithm
            formatted_plate = format_tunisian_plate_cam_center(characters)
            print(f"[OCR] Formatted plate: '{formatted_plate}'\n")
            
            return formatted_plate

        except Exception as e:
            print(f"[OCR] Error: {str(e)}")
            return ""

    def _preprocess_plate(self, plate_image: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for optimal OCR recognition.
        
        Enhanced preprocessing specifically tuned for Tunisian plates:
        1. Convert to grayscale
        2. 5x upscaling for better character clarity
        3. Denoising to remove artifacts
        4. Adaptive thresholding for high contrast
        5. Morphological operations to enhance digit clarity
        
        Args:
            plate_image: Input plate image
            
        Returns:
            Preprocessed image optimized for OCR
        """
        if plate_image is None or plate_image.size == 0:
            return plate_image

        # Step 1: Convert to grayscale
        if len(plate_image.shape) == 3:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_image
        print(f"[PREPROCESS] Step 1/6: Grayscale conversion - Shape: {gray.shape}")

        # Step 2: Upscale 5x for better digit clarity (increased from 3x)
        h, w = gray.shape[:2]
        upscaled = cv2.resize(gray, (w * 5, h * 5), interpolation=cv2.INTER_CUBIC)
        print(f"[PREPROCESS] Step 2/6: Upscaled 5x - New shape: {upscaled.shape}")

        # Step 3: Denoise to reduce OCR confusion
        denoised = cv2.fastNlMeansDenoising(upscaled, h=8, templateWindowSize=7, searchWindowSize=21)
        print(f"[PREPROCESS] Step 3/6: Denoising (h=8) - Applied")

        # Step 4: Bilateral filtering to preserve edges
        bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
        print(f"[PREPROCESS] Step 4/6: Bilateral filtering - Applied")

        # Step 5: Strong adaptive thresholding for digit clarity
        thresh = cv2.adaptiveThreshold(
            bilateral, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=13, 
            C=5
        )
        print(f"[PREPROCESS] Step 5/6: Adaptive threshold (blockSize=13, C=5) - Applied")

        # Step 6: Morphological operations to enhance digits
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        # Light closing to fill small holes in digits
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        print(f"[PREPROCESS] Step 6/6: Morphological closing - Applied")

        return closed

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
