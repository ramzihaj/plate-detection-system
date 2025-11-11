from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.core.security import get_current_user
from app.models.user import User
from app.models.plate_detection import PlateDetection

router = APIRouter()

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None

class UserStats(BaseModel):
    total_detections: int
    successful_detections: int
    failed_detections: int
    last_detection: Optional[str] = None

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    user = await User.get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }

@router.put("/profile")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user = await User.get(current_user["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    
    if profile_data.username is not None:
        # Check if username is already taken
        existing = await User.find_one(
            User.username == profile_data.username,
            User.id != user.id
        )
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = profile_data.username
    
    await user.save()
    
    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    }

@router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics"""
    user_id = current_user["id"]
    
    # Count total detections
    total = await PlateDetection.find(PlateDetection.user_id == user_id).count()
    
    # Count successful detections
    successful = await PlateDetection.find(
        PlateDetection.user_id == user_id,
        PlateDetection.status == "success"
    ).count()
    
    # Count failed detections
    failed = await PlateDetection.find(
        PlateDetection.user_id == user_id,
        PlateDetection.status == "failed"
    ).count()
    
    # Get last detection
    last_detection = await PlateDetection.find(
        PlateDetection.user_id == user_id
    ).sort("-created_at").first_or_none()
    
    return UserStats(
        total_detections=total,
        successful_detections=successful,
        failed_detections=failed,
        last_detection=last_detection.created_at.isoformat() if last_detection else None
    )
