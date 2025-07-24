
"""API endpoint modules."""

# Import all routers for easy access
from . import customers, campaigns, analytics, reports, chat, personalization

__all__ = [
    "customers",
    "campaigns", 
    "analytics",
    "reports",
    "chat",
    "personalization"
]
