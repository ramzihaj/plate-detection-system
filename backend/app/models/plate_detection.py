from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict

class PlateDetection(Document):
    user_id: str
    image_path: str
    detected_plate: Optional[str] = None
    confidence: Optional[float] = None
    bounding_box: Optional[Dict[str, int]] = None  # {x, y, width, height}
    detection_time: float  # Time taken to detect in seconds
    status: str = "success"  # success, failed, processing
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = {}  # Additional info
    
    class Settings:
        name = "plate_detections"
        indexes = [
            "user_id",
            "created_at",
            "status",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "image_path": "/uploads/plates/image.jpg",
                "detected_plate": "ABC123",
                "confidence": 0.95,
                "bounding_box": {"x": 100, "y": 200, "width": 150, "height": 50},
                "detection_time": 0.5,
                "status": "success"
            }
        }
