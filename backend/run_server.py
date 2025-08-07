#!/usr/bin/env python3
"""
Simple SBM AI CRM Backend Server Launcher
Direct uvicorn startup without complex import validation
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Launch the server directly with uvicorn"""
    print("🚀 SBM AI CRM Backend - Quick Launch")
    print("=" * 50)
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 4000))
    
    print(f"🌐 Starting server on http://{host}:{port}")
    print("📚 API Documentation: http://localhost:4000/docs")
    print("🔧 System Status: http://localhost:4000/api/system/status")
    print("\n🎯 Press CTRL+C to stop the server")
    print("=" * 50)
    
    # Import and run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install uvicorn fastapi")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()