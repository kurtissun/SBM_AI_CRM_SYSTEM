"""API layer components and utilities."""

try:
    from .auth import authenticate_user, require_permission, require_role
    __all__ = [
        "authenticate_user",
        "require_permission", 
        "require_role"
    ]
except ImportError:
    # Fallback for import issues
    __all__ = []
