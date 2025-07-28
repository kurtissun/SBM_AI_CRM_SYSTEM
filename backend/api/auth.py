"""
Authentication and authorization utilities for FastAPI
"""
from fastapi import HTTPException, status, Depends, APIRouter, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.security import security_manager, rate_limiter
from core.database import get_db

router = APIRouter()

logger = logging.getLogger(__name__)

# Security schemes
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_info: Dict

class RefreshRequest(BaseModel):
    refresh_token: str

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

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: LoginRequest, response: Response) -> TokenResponse:
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
        
        # Generate access and refresh tokens
        access_token = security_manager.create_access_token(token_data)
        refresh_token = security_manager.create_refresh_token(token_data)
        
        # Store session
        session_id = security_manager.store_session(login_data.username, {
            "username": login_data.username,
            "login_time": datetime.now().isoformat(),
            "user_agent": response.headers.get("user-agent", ""),
            "roles": user_data["roles"],
            "permissions": user_data["permissions"]
        })
        
        # Set secure cookies for refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        response.set_cookie(
            key="session_id", 
            value=session_id,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": security_manager.access_token_expire_minutes * 60,
            "user_info": {
                "username": login_data.username,
                "email": user_data["email"],
                "roles": user_data["roles"],
                "permissions": user_data["permissions"],
                "session_id": session_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login process failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_data: RefreshRequest, response: Response) -> TokenResponse:
    """Refresh access token using refresh token"""
    try:
        new_access_token = security_manager.refresh_access_token(refresh_data.refresh_token)
        payload = security_manager.verify_token(new_access_token)
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_data.refresh_token,  # Keep same refresh token
            "token_type": "bearer",
            "expires_in": security_manager.access_token_expire_minutes * 60,
            "user_info": {
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout_user(request: Request, response: Response, current_user: Dict = Depends(authenticate_user)) -> Dict:
    """Logout user and invalidate session"""
    try:
        # Invalidate session
        session_id = request.cookies.get("session_id")
        if session_id:
            security_manager.invalidate_session(session_id)
        
        # Clear cookies
        response.delete_cookie("refresh_token")
        response.delete_cookie("session_id")
        
        return {
            "message": "Logged out successfully",
            "user": current_user["username"],
            "logged_out_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "message": "Logout completed (with errors)",
            "user": current_user.get("username", "unknown"),
            "logged_out_at": datetime.now().isoformat()
        }

@router.get("/me")
async def get_current_user_info(current_user: Dict = Depends(authenticate_user)) -> UserResponse:
    """Get current user information"""
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email=current_user.get("email", ""),
        roles=current_user["roles"],
        permissions=current_user["permissions"],
        created_at=datetime.now(),  # Would come from database
        last_login=datetime.now()   # Would come from database
    )

@router.post("/generate-api-key")
async def generate_api_key(current_user: Dict = Depends(authenticate_user)) -> Dict:
    """Generate a new short API key for the user"""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to generate API keys"
        )
    
    api_key = security_manager.generate_api_key()
    
    return {
        "api_key": api_key,
        "generated_for": current_user["username"],
        "generated_at": datetime.now().isoformat(),
        "expires_in": "Never (until manually revoked)",
        "note": "Keep this key secure - it won't be shown again"
    }

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Dict = Depends(authenticate_user)
) -> Dict:
    """Change user password"""
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