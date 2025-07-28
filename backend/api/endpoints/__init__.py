
"""API endpoint modules."""

# Import all routers for easy access
try:
    from . import customers, campaigns, analytics, reports, chat, personalization
    __all__ = [
        "customers",
        "campaigns", 
        "analytics",
        "reports",
        "chat",
        "personalization"
    ]
except ImportError:
    # Allow graceful degradation if some modules are missing
    __all__ = []
