import cv2
import numpy as np
import easyocr
from typing import Optional, Tuple, Dict
import time
from PIL import Image
import os

class PlateDetectionService:
    """Service for detecting and recognizing license plates"""
    
    def __init__(self):
        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'], gpu=False)
        
        # Cascade classifier for plate detection (optional)
        # You can download haarcascade_russian_plate_number.xml from OpenCV repo
        self.plate_cascade = None
        cascade_path = "haarcascade_russian_plate_number.xml"
        if os.path.exists(cascade_path):
            self.plate_cascade = cv2.CascadeClassifier(cascade_path)
    
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
        Main method to detect and recognize license plate
        
        Returns:
            dict with keys: detected_plate, confidence, bounding_box, detection_time, status
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
                    "error_message": "Could not read image"
                }
            
            # Try cascade classifier first (if available)
            if self.plate_cascade is not None:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(plates) > 0:
                    x, y, w, h = plates[0]
                    bounding_box = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                else:
                    # Fallback to contour detection
                    result = self.detect_plate_contours(image)
                    if result:
                        x, y, w, h = result
                        bounding_box = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                    else:
                        bounding_box = None
            else:
                # Use contour detection
                result = self.detect_plate_contours(image)
                if result:
                    x, y, w, h = result
                    bounding_box = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
                else:
                    bounding_box = None
            
            # Extract ROI and perform OCR
            if bounding_box:
                x, y, w, h = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
                roi = image[y:y+h, x:x+w]
                
                plate_text, confidence = self.extract_text_from_roi(roi)
                
                if plate_text:
                    return {
                        "detected_plate": plate_text,
                        "confidence": confidence,
                        "bounding_box": bounding_box,
                        "detection_time": time.time() - start_time,
                        "status": "success",
                        "error_message": None
                    }
            
            # If no plate detected, try OCR on entire image
            plate_text, confidence = self.extract_text_from_roi(image)
            
            if plate_text:
                return {
                    "detected_plate": plate_text,
                    "confidence": confidence,
                    "bounding_box": None,
                    "detection_time": time.time() - start_time,
                    "status": "success",
                    "error_message": None
                }
            
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": "No plate detected"
            }
        
        except Exception as e:
            return {
                "detected_plate": None,
                "confidence": 0.0,
                "bounding_box": None,
                "detection_time": time.time() - start_time,
                "status": "failed",
                "error_message": str(e)
            }

# Singleton instance
_plate_detection_service = None

def get_plate_detection_service() -> PlateDetectionService:
    """Get singleton instance of PlateDetectionService"""
    global _plate_detection_service
    if _plate_detection_service is None:
        _plate_detection_service = PlateDetectionService()
    return _plate_detection_service
