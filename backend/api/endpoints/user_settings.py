"""
User Settings Management Endpoint
Handles user profile updates, theme preferences, and customization options
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import base64
import logging

from core.database import get_db, User
from core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class UserUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    custom_background: Optional[str] = None  # Base64 encoded image
    profile_picture: Optional[str] = None  # Base64 encoded image

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str]
    profile_picture: Optional[str]
    theme: str
    custom_background: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@router.get("/profile", response_model=UserResponse, tags=["User Settings"])
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile and settings"""
    try:
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        
        if not user:
            # Create user if doesn't exist (for backward compatibility)
            user = User(
                username=current_user.get("username"),
                email=current_user.get("email", f"{current_user.get('username')}@sbm.com"),
                display_name=current_user.get("name", current_user.get("username")),
                hashed_password="legacy_user",
                theme="dark"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            profile_picture=user.profile_picture,
            theme=user.theme,
            custom_background=user.custom_background,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile", response_model=UserResponse, tags=["User Settings"])
async def update_user_profile(
    user_update: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile and settings"""
    try:
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        
        if not user:
            # Create user if doesn't exist
            user = User(
                username=current_user.get("username"),
                email=current_user.get("email", f"{current_user.get('username')}@sbm.com"),
                display_name=current_user.get("name", current_user.get("username")),
                hashed_password="legacy_user",
                theme="dark"
            )
            db.add(user)
            db.flush()  # Flush to get the ID
        
        # Update user fields
        if user_update.display_name is not None:
            user.display_name = user_update.display_name
        
        if user_update.email is not None:
            user.email = user_update.email
        
        if user_update.theme is not None:
            user.theme = user_update.theme
        
        if user_update.custom_background is not None:
            # Validate base64 if it's an image
            if user_update.custom_background.startswith('data:image'):
                user.custom_background = user_update.custom_background
            elif user_update.custom_background.startswith('linear-gradient'):
                user.custom_background = user_update.custom_background
            else:
                raise HTTPException(status_code=400, detail="Invalid background format")
        
        if user_update.profile_picture is not None:
            # Validate base64 image
            if user_update.profile_picture.startswith('data:image'):
                user.profile_picture = user_update.profile_picture
            else:
                raise HTTPException(status_code=400, detail="Invalid profile picture format")
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            profile_picture=user.profile_picture,
            theme=user.theme,
            custom_background=user.custom_background,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profile-picture", tags=["User Settings"])
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file and convert to base64
        file_content = await file.read()
        base64_image = base64.b64encode(file_content).decode('utf-8')
        data_uri = f"data:{file.content_type};base64,{base64_image}"
        
        # Update user profile picture
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.profile_picture = data_uri
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return JSONResponse(content={
            "message": "Profile picture updated successfully",
            "profile_picture": data_uri
        })
        
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/background", tags=["User Settings"])
async def upload_custom_background(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload custom background image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file and convert to base64
        file_content = await file.read()
        base64_image = base64.b64encode(file_content).decode('utf-8')
        data_uri = f"data:{file.content_type};base64,{base64_image}"
        
        # Update user background
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.custom_background = data_uri
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return JSONResponse(content={
            "message": "Custom background updated successfully",
            "custom_background": data_uri
        })
        
    except Exception as e:
        logger.error(f"Error uploading custom background: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/profile-picture", tags=["User Settings"])
async def remove_profile_picture(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove profile picture"""
    try:
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.profile_picture = None
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return JSONResponse(content={
            "message": "Profile picture removed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error removing profile picture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/background", tags=["User Settings"])
async def remove_custom_background(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove custom background"""
    try:
        user = db.query(User).filter(User.username == current_user.get("username")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.custom_background = None
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return JSONResponse(content={
            "message": "Custom background removed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error removing custom background: {e}")
        raise HTTPException(status_code=500, detail=str(e))