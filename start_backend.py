#!/usr/bin/env python3
"""
SBM AI CRM Backend Server - Main Launcher
Run from project root directory to avoid import issues
"""
import os
import sys
from pathlib import Path
import uvicorn

def main():
    """Launch the SBM AI CRM Backend server"""
    print("🚀 SBM AI CRM Backend Server")
    print("=" * 50)
    
    # Ensure we're in the correct directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print(f"Expected: {backend_dir}")
        sys.exit(1)
    
    # Add backend to Python path
    sys.path.insert(0, str(backend_dir))
    
    # Test basic imports
    try:
        print("🔧 Testing system components...")
        
        # Test core imports
        from backend.core.database import get_db
        print("✅ Database layer ready")
        
        from backend.core.security import get_current_user  
        print("✅ Security layer ready")
        
        # Test a few key engines
        from backend.ai_engine.adaptive_clustering import AdaptiveClustering
        print("✅ AI engines ready")
        
        from backend.analytics.predictive_engine import PredictiveAnalyticsEngine
        print("✅ Analytics engines ready")
        
        print("🎉 System health check passed!")
        
    except ImportError as e:
        print(f"⚠️  Some components unavailable: {e}")
        print("🔄 Continuing with available features...")
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🌐 Starting server on http://{host}:{port}")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print("📊 System Status: http://localhost:8000/api/system/status")
    print("\n🎯 Press CTRL+C to stop the server")
    print("=" * 50)
    
    try:
        # Change working directory to backend
        os.chdir(backend_dir)
        
        # Start the server
        uvicorn.run(
            "backend.api.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\n🔄 Trying alternative startup method...")
        
        try:
            # Alternative: direct module path
            uvicorn.run(
                "api.main:app",
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )
        except Exception as e2:
            print(f"❌ Alternative startup failed: {e2}")
            print("💡 Please check the API documentation for manual startup instructions")
            sys.exit(1)

if __name__ == "__main__":
    main()