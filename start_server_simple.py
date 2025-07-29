#!/usr/bin/env python3
"""
Simple SBM AI CRM Server Launcher - Fixed for localhost connectivity
"""
import sys
import os
import logging
import uvicorn
from pathlib import Path

# Add project root and backend to Python path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start the server on localhost:8080"""
    print("🚀 SBM AI CRM System - Starting on localhost:8080")
    print("=" * 60)
    
    try:
        # Import the FastAPI app
        from backend.api.main import app
        
        # Start server on localhost (not 0.0.0.0) for local development
        uvicorn.run(
            app,
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0
            port=8080,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        logger.info("🔄 Trying alternative method...")
        try:
            uvicorn.run(
                "backend.api.main:app",
                host="127.0.0.1",
                port=8080,
                reload=False,
                log_level="info"
            )
        except Exception as e2:
            logger.error(f"❌ Alternative startup also failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()