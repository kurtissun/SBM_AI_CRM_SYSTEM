"""
Security and authentication management
"""
import hashlib
import secrets
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import jwt
import bcrypt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from .database import cache
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class SecurityManager:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = 30  # Refresh tokens last 30 days
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create shorter JWT access token"""
        # Minimize payload for shorter tokens
        minimal_data = {
            "sub": data.get("sub"),
            "usr": data.get("username"),  # Shortened field names
            "rol": data.get("roles", []),
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "typ": "acc"  # Shortened type
        }
        
        encoded_jwt = jwt.encode(minimal_data, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create shorter JWT refresh token"""
        # Even more minimal payload for refresh tokens
        minimal_data = {
            "sub": data.get("sub"),
            "usr": data.get("username"),
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "typ": "ref"  # Shortened type
        }
        
        encoded_jwt = jwt.encode(minimal_data, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Generate new access token from valid refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if payload.get("typ") != "ref":  # Updated to use shortened field
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Create new access token with user data from refresh token
            new_data = {
                "sub": payload.get("sub"),
                "username": payload.get("usr"),  # Map back to full field name
                "roles": payload.get("rol", [])
            }
            return self.create_access_token(new_data)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh token"
            )
    
    def generate_api_key(self) -> str:
        """Generate shorter, user-friendly API key"""
        # Generate 8-character alphanumeric key (easier to copy-paste)
        import string
        alphabet = string.ascii_uppercase + string.digits
        # Remove confusing characters
        alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
        return ''.join(secrets.choice(alphabet) for _ in range(8))
    
    def store_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Store session data in cache and return session ID"""
        session_id = secrets.token_urlsafe(16)
        cache_key = f"session:{session_id}"
        cache.set(cache_key, session_data, ttl=self.refresh_token_expire_days * 24 * 3600)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from cache"""
        cache_key = f"session:{session_id}"
        return cache.get(cache_key)
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate session"""
        cache_key = f"session:{session_id}"
        return cache.delete(cache_key)
    
    def hash_data(self, data: str) -> str:
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()

# Global security instance
security_manager = SecurityManager()

# Enhanced dependency for protected routes with session support
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to get current authenticated user with session persistence"""
    try:
        # Try to verify the token
        payload = security_manager.verify_token(credentials.credentials)
        username = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Map shortened fields back to full user info
        user_info = {
            "user_id": username,
            "username": payload.get("usr", username),  # Use shortened field
            "roles": payload.get("rol", []),  # Use shortened field
            "permissions": _get_permissions_for_roles(payload.get("rol", [])),
            "payload": payload
        }
        
        # Store session info in request state for persistence
        request.state.user = user_info
        
        return user_info
        
    except HTTPException as e:
        # If token is expired, check if we can auto-refresh
        if "Token expired" in str(e.detail):
            # Look for refresh token in cookies or headers
            refresh_token = request.cookies.get("refresh_token") or request.headers.get("X-Refresh-Token")
            
            if refresh_token:
                try:
                    # Try to refresh the access token
                    new_access_token = security_manager.refresh_access_token(refresh_token)
                    new_payload = security_manager.verify_token(new_access_token)
                    username = new_payload.get("sub")
                    
                    if username:
                        # Map back to full user info
                        user_info = {
                            "user_id": username,
                            "username": new_payload.get("usr", username),
                            "roles": new_payload.get("rol", []),
                            "permissions": _get_permissions_for_roles(new_payload.get("rol", [])),
                            "payload": new_payload
                        }
                        
                        # Store the new token info
                        request.state.user = user_info
                        request.state.new_access_token = new_access_token  # For response headers
                        
                        return user_info
                        
                except Exception:
                    pass  # Fall through to unauthorized
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - please log in again"
        )

def _get_permissions_for_roles(roles: List[str]) -> List[str]:
    """Map roles to permissions"""
    role_permissions = {
        "admin": ["read", "write", "admin", "manage_users", "manage_campaigns"],
        "marketing_manager": ["read", "write", "manage_campaigns", "view_analytics"],
        "analyst": ["read", "view_analytics", "generate_reports"],
        "viewer": ["read"]
    }
    
    permissions = set()
    for role in roles:
        permissions.update(role_permissions.get(role, []))
    
    return list(permissions)

# Optional dependency for routes that can work with or without auth
async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
):
    """Optional authentication - returns None if not authenticated"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = datetime.utcnow()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if (now - req_time).seconds < self.time_window
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False

rate_limiter = RateLimiter()

# Data privacy functions
class PrivacyManager:
    @staticmethod
    def anonymize_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive customer data"""
        anonymized = data.copy()
        
        # Remove or hash PII
        sensitive_fields = ['customer_id', 'member_name', 'email', 'phone']
        for field in sensitive_fields:
            if field in anonymized:
                if field == 'customer_id':
                    anonymized[field] = security_manager.hash_data(str(anonymized[field]))
                else:
                    del anonymized[field]
        
        return anonymized
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data for storage"""
        # Implementation would use proper encryption library
        return security_manager.hash_data(data)

privacy_manager = PrivacyManager()