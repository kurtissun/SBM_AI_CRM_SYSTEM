#!/usr/bin/env python3
"""
Test server on port 8081 to diagnose connectivity issues
"""
import sys
import uvicorn
from pathlib import Path

# Add project root and backend to Python path
project_root = Path(__file__).parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

def main():
    """Start the server on port 8081 for testing"""
    print("🧪 Testing SBM AI CRM on port 8081...")
    
    try:
        from backend.api.main import app
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8081,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Test server failed: {e}")

if __name__ == "__main__":
    main()