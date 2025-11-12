from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List, Optional, Dict
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from app.core.security import get_current_user
from app.core.config import settings
from app.models.plate_detection import PlateDetection
from app.services.plate_detection_service import get_plate_detection_service

router = APIRouter()

class DetectionResponse(BaseModel):
    id: str
    detected_plate: Optional[str] = None
    confidence: Optional[float] = None
    bounding_box: Optional[Dict] = None
    detection_time: float
    status: str
    image_url: str
    created_at: str

class DetectionHistory(BaseModel):
    detections: List[DetectionResponse]
    total: int
    page: int
    page_size: int

@router.post("/detect", response_model=DetectionResponse)
async def detect_plate(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Detect license plate in uploaded image"""
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, "plates", unique_filename)
    
    # Save uploaded file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Perform plate detection
    detection_service = get_plate_detection_service()
    result = detection_service.detect_plate(file_path)
    
    # Create detection record
    detection = PlateDetection(
        user_id=current_user["id"],
        image_path=f"/uploads/plates/{unique_filename}",
        detected_plate=result["detected_plate"],
        confidence=result["confidence"],
        bounding_box=result["bounding_box"],
        detection_time=result["detection_time"],
        status=result["status"],
        error_message=result.get("error_message")
    )
    await detection.insert()
    
    return DetectionResponse(
        id=str(detection.id),
        detected_plate=detection.detected_plate,
        confidence=detection.confidence,
        bounding_box=detection.bounding_box,
        detection_time=detection.detection_time,
        status=detection.status,
        image_url=detection.image_path,
        created_at=detection.created_at.isoformat()
    )

@router.get("/history", response_model=DetectionHistory)
async def get_detection_history(
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's detection history"""
    
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    
    skip = (page - 1) * page_size
    
    # Get total count
    total = await PlateDetection.find(
        PlateDetection.user_id == current_user["id"]
    ).count()
    
    # Get detections
    detections = await PlateDetection.find(
        PlateDetection.user_id == current_user["id"]
    ).sort("-created_at").skip(skip).limit(page_size).to_list()
    
    detection_list = [
        DetectionResponse(
            id=str(d.id),
            detected_plate=d.detected_plate,
            confidence=d.confidence,
            bounding_box=d.bounding_box,
            detection_time=d.detection_time,
            status=d.status,
            image_url=d.image_path,
            created_at=d.created_at.isoformat()
        )
        for d in detections
    ]
    
    return DetectionHistory(
        detections=detection_list,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific detection details"""
    
    detection = await PlateDetection.get(detection_id)
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    
    # Check if user owns this detection
    if detection.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return DetectionResponse(
        id=str(detection.id),
        detected_plate=detection.detected_plate,
        confidence=detection.confidence,
        bounding_box=detection.bounding_box,
        detection_time=detection.detection_time,
        status=detection.status,
        image_url=detection.image_path,
        created_at=detection.created_at.isoformat()
    )

@router.delete("/{detection_id}")
async def delete_detection(
    detection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a detection"""
    
    detection = await PlateDetection.get(detection_id)
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    
    # Check if user owns this detection
    if detection.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete image file
    try:
        image_path = detection.image_path.lstrip("/")
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        print(f"Failed to delete image file: {e}")
    
    # Delete detection record
    await detection.delete()
    
    return {"message": "Detection deleted successfully"}
