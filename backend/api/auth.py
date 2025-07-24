"""
Authentication and authorization utilities for FastAPI
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..core.security import security_manager, rate_limiter
from ..core.database import get_db

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    roles: List[str] = ["user"]

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime]

async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Authenticate user and return user info
    """
    try:
        # Verify JWT token
        payload = security_manager.verify_token(credentials.credentials)
        
        # Rate limiting check
        user_id = payload.get("sub")
        if not rate_limiter.is_allowed(user_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "email": payload.get("email"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_permission(permission: str):
    """
    Decorator to require specific permission
    """
    async def permission_checker(current_user: Dict = Depends(authenticate_user)):
        user_permissions = current_user.get("permissions", [])
        user_roles = current_user.get("roles", [])
        
        # Admin role has all permissions
        if "admin" in user_roles:
            return current_user
        
        # Check specific permission
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return permission_checker

def require_role(role: str):
    """
    Decorator to require specific role
    """
    async def role_checker(current_user: Dict = Depends(authenticate_user)):
        user_roles = current_user.get("roles", [])
        
        if role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        
        return current_user
    
    return role_checker

async def login_user(login_data: LoginRequest) -> TokenResponse:
    """
    Login user and return JWT token
    """
    try:
        # Demo authentication - replace with real user database
        valid_users = {
            "admin": {
                "password": "admin123",
                "email": "admin@sbm.com",
                "roles": ["admin"],
                "permissions": ["read", "write", "admin", "manage_users", "manage_campaigns"]
            },
            "marketing_manager": {
                "password": "marketing123", 
                "email": "marketing@sbm.com",
                "roles": ["marketing_manager"],
                "permissions": ["read", "write", "manage_campaigns", "view_analytics"]
            },
            "analyst": {
                "password": "analyst123",
                "email": "analyst@sbm.com", 
                "roles": ["analyst"],
                "permissions": ["read", "view_analytics", "generate_reports"]
            },
            "viewer": {
                "password": "viewer123",
                "email": "viewer@sbm.com",
                "roles": ["viewer"], 
                "permissions": ["read"]
            }
        }
        
        user_data = valid_users.get(login_data.username)
        
        if not user_data or user_data["password"] != login_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create token payload
        token_data = {
            "sub": login_data.username,
            "username": login_data.username,
            "email": user_data["email"],
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
            "login_time": datetime.now().isoformat()
        }
        
        # Generate token
        token = security_manager.create_access_token(token_data)
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=security_manager.access_token_expire_minutes * 60,
            user_info={
                "username": login_data.username,
                "email": user_data["email"],
                "roles": user_data["roles"],
                "permissions": user_data["permissions"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login process failed"
        )

async def logout_user(current_user: Dict = Depends(authenticate_user)) -> Dict:
    """
    Logout user (in a real implementation, would invalidate token)
    """
    return {
        "message": "Logged out successfully",
        "user": current_user["username"],
        "logged_out_at": datetime.now().isoformat()
    }

async def refresh_token(current_user: Dict = Depends(authenticate_user)) -> TokenResponse:
    """
    Refresh user token
    """
    try:
        # Create new token with updated timestamp
        token_data = {
            "sub": current_user["user_id"],
            "username": current_user["username"],
            "email": current_user.get("email"),
            "roles": current_user["roles"],
            "permissions": current_user["permissions"],
            "refresh_time": datetime.now().isoformat()
        }
        
        new_token = security_manager.create_access_token(token_data)
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer", 
            expires_in=security_manager.access_token_expire_minutes * 60,
            user_info={
                "username": current_user["username"],
                "email": current_user.get("email"),
                "roles": current_user["roles"],
                "permissions": current_user["permissions"]
            }
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

async def get_current_user_info(current_user: Dict = Depends(authenticate_user)) -> UserResponse:
    """
    Get current user information
    """
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email=current_user.get("email", ""),
        roles=current_user["roles"],
        permissions=current_user["permissions"],
        created_at=datetime.now(),  # Would come from database
        last_login=datetime.now()   # Would come from database
    )

async def change_password(
    old_password: str,
    new_password: str,
    current_user: Dict = Depends(authenticate_user)
) -> Dict:
    """
    Change user password
    """
    # In a real implementation, would verify old password and update in database
    return {
        "message": "Password changed successfully",
        "user": current_user["username"],
        "changed_at": datetime.now().isoformat()
    }

# Permission decorators for common actions
require_admin = require_role("admin")
require_marketing = require_role("marketing_manager") 
require_analyst = require_role("analyst")

require_read = require_permission("read")
require_write = require_permission("write")
require_manage_campaigns = require_permission("manage_campaigns")
require_view_analytics = require_permission("view_analytics")
require_generate_reports = require_permission("generate_reports")