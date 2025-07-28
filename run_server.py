#!/usr/bin/env python3
"""
Simple server startup script for SBM AI CRM System
"""
import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic_settings', 'sqlalchemy', 
        'psycopg2', 'redis', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are available")
    return True

def check_environment():
    """Check if environment is properly configured"""
    env_file = project_root / '.env'
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Please create .env file with required configuration")
        return False
    
    print("✅ Environment configuration found")
    return True

def create_directories():
    """Create required directories"""
    directories = [
        'logs',
        'models/ml_models', 
        'models/cv_models',
        'data/face_database',
        'data/processed',
        'data/reports/daily_reports',
        'data/reports/weekly_reports', 
        'data/reports/monthly_reports'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Required directories created")

def main():
    """Main startup function"""
    print("🚀 Starting SBM AI CRM System...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("=" * 50)
    print("🎉 Starting FastAPI server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔗 Admin Interface: http://localhost:8000/")
    print("🔐 Demo Login: admin / admin123")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        from backend.api.main import app
        
        uvicorn.run(
            "backend.api.main:app",
            host="0.0.0.0",
            port=8080,
            reload=False,  # Disable reload for stability
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()