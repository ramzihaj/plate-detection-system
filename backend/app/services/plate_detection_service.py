import cv2
import numpy as np
import easyocr
from typing import Optional, Tuple, Dict, List
import time
from PIL import Image
import os
from dataclasses import dataclass

# Try to import YOLO detector
try:
    from .yolo_plate_detector import create_yolo_detector, PlateDetection
    YOLO_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    YOLO_AVAILABLE = False
    PlateDetection = None

@dataclass
class DetectionResult:
    """Result from a single detection strategy"""
    text: Optional[str]
    confidence: float
    bounding_box: Optional[Dict]
    strategy: str
    success: bool

class PlateDetectionService:
    """Service for detecting and recognizing license plates"""
    
    def __init__(self, model_path: Optional[str] = None):
        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'], gpu=False)
        
        # Cascade classifier for plate detection (optional)
        # You can download haarcascade_russian_plate_number.xml from OpenCV repo
        self.plate_cascade = None
        cascade_path = "haarcascade_russian_plate_number.xml"
        if os.path.exists(cascade_path):
            self.plate_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Initialize YOLO detector if available
        self.yolo_detector = None
        self.use_yolo = False
        if YOLO_AVAILABLE:
            try:
                self.yolo_detector = create_yolo_detector(model_path)
                self.use_yolo = True
                print("[PlateDetectionService] YOLO detector initialized successfully")
            except Exception as e:
                print(f"[PlateDetectionService] Failed to initialize YOLO: {e}")
                self.use_yolo = False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better plate detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        return gray
    
    def preprocess_plate_roi(self, roi: np.ndarray) -> np.ndarray:
        """Advanced preprocessing specifically for plate text extraction"""
        # Convert to grayscale if needed
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi.copy()
        
        # Upscale the image if too small (helps with OCR accuracy)
        if gray.shape[0] < 50 or gray.shape[1] < 200:
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Apply bilateral filter to remove noise
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to improve text visibility
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Invert if needed (text should be black on white for OCR)
        # Check if text is mostly white
        if np.sum(thresh) > thresh.size * 255 * 0.5:
            thresh = cv2.bitwise_not(thresh)
        
        return thresh
    
    def detect_center_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect license plate in center region (optimized for centered plates)"""
        h, w = image.shape[:2]
        
        # Define center region (60% width x 40% height, centered)
        center_w_ratio = 0.6
        center_h_ratio = 0.4
        
        x_start = int(w * (1 - center_w_ratio) / 2)
        y_start = int(h * (1 - center_h_ratio) / 2)
        x_end = int(x_start + w * center_w_ratio)
        y_end = int(y_start + h * center_h_ratio)
        
        # Extract center region
        center_roi = image[y_start:y_end, x_start:x_end]
        
        # Detect plate in center region
        gray = self.preprocess_image(center_roi)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Apply Canny edge detection
        edges = cv2.Canny(morph, 80, 180)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        # Find rectangular contours
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
            
            if len(approx) == 4:
                x, y, box_w, box_h = cv2.boundingRect(approx)
                aspect_ratio = box_w / float(box_h) if box_h > 0 else 0
                area = box_w * box_h
                
                # Stricter criteria for centered plates
                if 2.0 <= aspect_ratio <= 6.0 and area > 800:
                    # Return coordinates relative to original image
                    return (x + x_start, y + y_start, box_w, box_h)
        
        return None
    
    def detect_hsv_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect license plate using HSV color space (targets yellow/white regions)"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Yellow region for license plates
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        
        # White region
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 50, 255])
        
        # Create masks
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        mask = cv2.bitwise_or(mask_yellow, mask_white)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            
            if 2.0 <= aspect_ratio <= 6.0 and cv2.contourArea(contour) > 1000:
                return (x, y, w, h)
        
        return None
    
    def detect_horizontal_lines(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect license plate using horizontal line detection"""
        gray = self.preprocess_image(image)
        
        # Apply morphological operations to enhance horizontal lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 2))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Apply Canny
        edges = cv2.Canny(morph, 100, 200)
        
        # Dilate to connect components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            
            if 2.0 <= aspect_ratio <= 8.0 and cv2.contourArea(contour) > 1000:
                return (x, y, w, h)
        
        return None
    
    def detect_plate_contours(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect license plate using contour detection"""
        gray = self.preprocess_image(image)
        
        # Apply morphological operations to enhance plate edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel, iterations=2)
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Apply edge detection with refined parameters
        edges = cv2.Canny(morph, 100, 200)
        
        # Dilate edges to connect broken lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
        
        plate_contour = None
        
        # Find rectangular contours that match license plate characteristics
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
            
            # If contour has 4 points, it's likely a rectangle
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h) if h > 0 else 0
                area = w * h
                
                # License plates typically have aspect ratio between 2 and 6
                # and minimum area for visibility
                if 2.0 <= aspect_ratio <= 6.0 and area > 1000:
                    plate_contour = (x, y, w, h)
                    break
        
        return plate_contour
    
    def extract_text_from_roi(self, roi: np.ndarray) -> Tuple[Optional[str], float]:
        """Extract text from ROI using OCR"""
        try:
            # Preprocess the ROI for better OCR
            processed_roi = self.preprocess_plate_roi(roi)
            
            # Use EasyOCR to read text
            results = self.reader.readtext(processed_roi)
            
            if results:
                # Combine all detected texts
                all_texts = []
                confidences = []
                
                for detection in results:
                    text = detection[1].upper().strip()
                    confidence = detection[2]
                    
                    if confidence > 0.3:  # Only consider reasonably confident detections
                        all_texts.append(text)
                        confidences.append(confidence)
                
                if all_texts:
                    # Join texts and clean
                    combined_text = ''.join(all_texts).replace(" ", "")
                    
                    # Filter out unwanted characters (keep only alphanumeric)
                    cleaned_text = ''.join(c for c in combined_text if c.isalnum())
                    
                    # Calculate average confidence
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    # Validate plate format (typical license plates have 5-8 alphanumeric chars)
                    if 4 <= len(cleaned_text) <= 12:
                        return cleaned_text, avg_confidence
                    else:
                        # Try fallback: get the text with highest confidence
                        best_result = max(results, key=lambda x: x[2])
                        text = best_result[1].upper().replace(" ", "")
                        text = ''.join(c for c in text if c.isalnum())
                        if text:
                            return text, best_result[2]
            
            return None, 0.0
        
        except Exception as e:
            print(f"OCR Error: {e}")
            return None, 0.0
    
    def detect_plate(self, image_path: str) -> Dict:
        """
        Main method to detect and recognize license plate.
        
        Uses YOLO if available, falls back to legacy multi-strategy detection.
        
        Returns:
            dict with keys: detected_plate, confidence, bounding_box, detection_time, status,
                           is_valid_format, detection_method, all_detections
        """
        start_time = time.time()
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "detected_plate": None,
                    "confidence": 0.0,
                    "bounding_box": None,
                    "detection_time": time.time() - start_time,
                    "status": "failed",
                    "error_message": "Could not read image",
                    "detection_method": "none",
                    "is_valid_format": False,
                    "all_detections": []
                }
            
            # Try YOLO first if available
            if self.use_yolo and self.yolo_detector:
                return self._detect_plate_yolo(image, start_time)
            
            # Fall back to legacy detection
            return self._detect_plate_legacy(image, start_time)
        
        except Exception as e:
            print(f"Detection Error: {e}")
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": str(e),
                "detection_method": "none",
                "is_valid_format": False,
                "all_detections": []
            }
    
    def _detect_plate_yolo(self, image: np.ndarray, start_time: float) -> Dict:
        """
        Detect plate using YOLO.
        
        Args:
            image: Input image (BGR from OpenCV)
            start_time: Time when detection started
            
        Returns:
            Detection result dictionary
        """
        try:
            # Run YOLO detection
            detections = self.yolo_detector.detect_plates(image)
            
            if not detections:
                # No plates detected - this is still a valid operation result
                return {
                    "detected_plate": None,
                    "confidence": 0.0,
                    "bounding_box": None,
                    "detection_time": time.time() - start_time,
                    "status": "success",
                    "error_message": None,
                    "detection_method": "yolo",
                    "is_valid_format": False,
                    "all_detections": []
                }
            
            # Select best detection (highest confidence valid plate)
            best_detection = None
            for detection in detections:
                if detection.is_valid_format:
                    best_detection = detection
                    break
            
            # If no valid format found, use highest confidence
            if not best_detection:
                best_detection = max(detections, key=lambda d: d.confidence)
            
            # Format bounding box for compatibility
            x1, y1, x2, y2 = best_detection.bounding_box
            bbox_dict = {
                "x": int(x1),
                "y": int(y1),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            }
            
            # Convert all detections to dict format
            all_detections = [
                {
                    "plate_text": d.plate_text,
                    "confidence": float(d.confidence),
                    "is_valid_format": d.is_valid_format,
                    "bounding_box": {
                        "x": int(d.bounding_box[0]),
                        "y": int(d.bounding_box[1]),
                        "width": int(d.bounding_box[2] - d.bounding_box[0]),
                        "height": int(d.bounding_box[3] - d.bounding_box[1])
                    }
                }
                for d in detections
            ]
            
            return {
                "detected_plate": best_detection.plate_text,
                "confidence": float(best_detection.confidence),
                "bounding_box": bbox_dict,
                "detection_time": time.time() - start_time,
                "status": "success",
                "error_message": None,
                "detection_method": "yolo",
                "is_valid_format": best_detection.is_valid_format,
                "all_detections": all_detections
            }
        
        except Exception as e:
            print(f"[YOLO Detection Error] {e}")
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "success",
                "error_message": None,
                "detection_method": "yolo",
                "is_valid_format": False,
                "all_detections": []
            }
    
    def _detect_plate_legacy(self, image: Optional[np.ndarray], start_time: float) -> Dict:
        """
        Legacy multi-strategy plate detection (fallback from YOLO).
        
        Args:
            image: Input image (BGR from OpenCV) - can be None if called for error fallback
            start_time: Time when detection started
            
        Returns:
            Detection result dictionary
        """
        if image is None or image.size == 0:
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": "No valid image provided",
                "detection_method": "legacy",
                "is_valid_format": False,
                "all_detections": []
            }
            
        try:
            # Try multiple detection strategies
            detection_results: List[DetectionResult] = []
            
            # Strategy 1: Center region detection (optimized for centered plates)
            center_result = self.detect_center_region(image)
            if center_result:
                x, y, w, h = center_result
                roi = image[y:y+h, x:x+w]
                plate_text, confidence = self.extract_text_from_roi(roi)
                if plate_text and confidence > 0.4:
                    detection_results.append(DetectionResult(
                        text=plate_text,
                        confidence=confidence,
                        bounding_box={"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        strategy="center_region",
                        success=True
                    ))
            
            # Strategy 2: HSV color detection
            hsv_result = self.detect_hsv_region(image)
            if hsv_result:
                x, y, w, h = hsv_result
                roi = image[y:y+h, x:x+w]
                plate_text, confidence = self.extract_text_from_roi(roi)
                if plate_text and confidence > 0.4:
                    detection_results.append(DetectionResult(
                        text=plate_text,
                        confidence=confidence,
                        bounding_box={"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        strategy="hsv_color",
                        success=True
                    ))
            
            # Strategy 3: Horizontal line detection
            line_result = self.detect_horizontal_lines(image)
            if line_result:
                x, y, w, h = line_result
                roi = image[y:y+h, x:x+w]
                plate_text, confidence = self.extract_text_from_roi(roi)
                if plate_text and confidence > 0.4:
                    detection_results.append(DetectionResult(
                        text=plate_text,
                        confidence=confidence,
                        bounding_box={"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        strategy="horizontal_lines",
                        success=True
                    ))
            
            # Strategy 4: Standard contour detection
            contour_result = self.detect_plate_contours(image)
            if contour_result:
                x, y, w, h = contour_result
                roi = image[y:y+h, x:x+w]
                plate_text, confidence = self.extract_text_from_roi(roi)
                if plate_text and confidence > 0.4:
                    detection_results.append(DetectionResult(
                        text=plate_text,
                        confidence=confidence,
                        bounding_box={"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        strategy="contour_detection",
                        success=True
                    ))
            
            # Select best result
            if detection_results:
                # Sort by confidence (descending)
                detection_results.sort(key=lambda x: x.confidence, reverse=True)
                best_result = detection_results[0]
                
                # Validate the best result
                if best_result.text and len(best_result.text) >= 4:
                    return {
                        "detected_plate": best_result.text,
                        "confidence": best_result.confidence,
                        "bounding_box": best_result.bounding_box,
                        "detection_time": time.time() - start_time,
                        "status": "success",
                        "error_message": None,
                        "detection_method": "legacy",
                        "is_valid_format": False,
                        "all_detections": []
                    }
            
            # Fallback: Try OCR on entire image
            plate_text, confidence = self.extract_text_from_roi(image)
            
            if plate_text and confidence > 0.3:
                return {
                    "detected_plate": plate_text,
                    "confidence": confidence,
                    "bounding_box": None,
                    "detection_time": time.time() - start_time,
                    "status": "success",
                    "error_message": None,
                    "detection_method": "legacy",
                    "is_valid_format": False,
                    "all_detections": []
                }
            
            # No plate detected - still a successful operation (just no results)
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "success",
                "error_message": None,
                "detection_method": "legacy",
                "is_valid_format": False,
                "all_detections": []
            }
        
        except Exception as e:
            print(f"Legacy Detection Error: {e}")
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": str(e),
                "detection_method": "legacy",
                "is_valid_format": False,
                "all_detections": []
            }
    
    def detect_plate_video(self, video_path: str, frame_interval: int = 30) -> Dict:
        """
        Detect license plates in a video file.
        
        Args:
            video_path: Path to video file
            frame_interval: Process every Nth frame (default: 30)
            
        Returns:
            dict with keys: detections (list), total_frames, processed_frames, 
                           detection_time, status, video_duration
        """
        start_time = time.time()
        
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {
                    "detections": [],
                    "total_frames": 0,
                    "processed_frames": 0,
                    "detection_time": time.time() - start_time,
                    "status": "failed",
                    "error_message": "Could not open video file",
                    "video_duration": 0
                }
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = total_frames / fps if fps > 0 else 0
            
            detections = []
            frame_count = 0
            processed_count = 0
            
            # Track unique plates to avoid duplicates
            seen_plates = {}
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Process every Nth frame
                if frame_count % frame_interval == 0:
                    processed_count += 1
                    
                    # Detect plate in frame using YOLO or legacy methods
                    if self.use_yolo and self.yolo_detector:
                        frame_detections = self.yolo_detector.detect_plates(frame)
                        
                        for detection in frame_detections:
                            plate_text = detection.plate_text
                            
                            # Check if we've seen this plate
                            if plate_text and plate_text not in seen_plates:
                                seen_plates[plate_text] = {
                                    "plate_text": plate_text,
                                    "confidence": float(detection.confidence),
                                    "frame_number": frame_count,
                                    "timestamp": frame_count / fps if fps > 0 else 0,
                                    "is_valid_format": detection.is_valid_format,
                                    "bounding_box": {
                                        "x": int(detection.bounding_box[0]),
                                        "y": int(detection.bounding_box[1]),
                                        "width": int(detection.bounding_box[2] - detection.bounding_box[0]),
                                        "height": int(detection.bounding_box[3] - detection.bounding_box[1])
                                    }
                                }
                            elif plate_text and detection.confidence > seen_plates[plate_text]["confidence"]:
                                # Update with higher confidence detection
                                seen_plates[plate_text]["confidence"] = float(detection.confidence)
                                seen_plates[plate_text]["frame_number"] = frame_count
                                seen_plates[plate_text]["timestamp"] = frame_count / fps if fps > 0 else 0
                    else:
                        # Use legacy detection
                        # Try multiple detection strategies on frame
                        center_result = self.detect_center_region(frame)
                        if center_result:
                            x, y, w, h = center_result
                            roi = frame[y:y+h, x:x+w]
                            plate_text, confidence = self.extract_text_from_roi(roi)
                            
                            if plate_text and confidence > 0.4:
                                if plate_text not in seen_plates or confidence > seen_plates[plate_text]["confidence"]:
                                    seen_plates[plate_text] = {
                                        "plate_text": plate_text,
                                        "confidence": float(confidence),
                                        "frame_number": frame_count,
                                        "timestamp": frame_count / fps if fps > 0 else 0,
                                        "is_valid_format": False,
                                        "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                                    }
            
            cap.release()
            
            # Convert detections dict to list
            detections = list(seen_plates.values())
            
            # Sort by confidence (descending)
            detections.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "detections": detections,
                "total_frames": total_frames,
                "processed_frames": processed_count,
                "detection_time": time.time() - start_time,
                "status": "success" if detections else "no_detections",
                "error_message": None if detections else "No plates detected in video",
                "video_duration": video_duration
            }
        
        except Exception as e:
            print(f"Video Detection Error: {e}")
            return {
                "detections": [],
                "total_frames": 0,
                "processed_frames": 0,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": str(e),
                "video_duration": 0
            }

# Singleton instance
_plate_detection_service = None

def get_plate_detection_service(model_path: Optional[str] = None) -> PlateDetectionService:
    """Get singleton instance of PlateDetectionService"""
    global _plate_detection_service
    if _plate_detection_service is None:
        _plate_detection_service = PlateDetectionService(model_path=model_path)
    return _plate_detection_service
