#!/usr/bin/env python3
"""
SBM AI CRM Server - Production Ready
"""
import sys
import os
import logging
from pathlib import Path

# Add project root and backend to Python path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

# Import uvicorn at the end to ensure path is set
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start the SBM AI CRM System"""
    print("🚀 SBM AI CRM System - Enterprise Edition")
    print("=" * 60)
    print("🌐 Starting server...")
    print("📊 Access API docs at: http://localhost:8080/docs")
    print("💬 Admin chat test page available")
    print("=" * 60)
    
    try:
        # Import the app 
        from backend.api.main import app
        
        # Start server
        uvicorn.run(
            app,
            host="localhost",
            port=8080,
            log_level="info",
            access_log=True,
            reload=False
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        logger.info("🔄 Trying alternative startup...")
        try:
            uvicorn.run(
                "backend.api.main:app",
                host="localhost", 
                port=8080,
                log_level="info"
            )
        except Exception as e2:
            logger.error(f"❌ Startup failed: {e2}")

if __name__ == "__main__":
    main()