#!/usr/bin/env python3
"""
SBM AI CRM Backend Server Startup Script
Production-ready launcher with comprehensive health checks
"""
import sys
import os
import uvicorn
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'numpy',
        'pandas',
        'scikit-learn',
        'networkx',
        'anthropic',
        'aiohttp',
        'websockets'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"Missing required dependencies: {', '.join(missing)}")
        logger.error("Please install with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies available")
    return True

def check_system_health():
    """Perform comprehensive system health check"""
    logger.info("🔧 Performing system health check...")
    
    # Test core system components
    try:
        from core.database import get_db
        from core.security import get_current_user
        from core.config import settings
        logger.info("✅ Core systems operational")
    except Exception as e:
        logger.error(f"❌ Core system failed: {e}")
        return False
    
    # Test AI engines
    ai_engines = [
        'ai_engine.adaptive_clustering',
        'ai_engine.campaign_intelligence',
        'ai_engine.conversational_ai',
        'ai_engine.insight_generator'
    ]
    
    ai_success = 0
    for engine in ai_engines:
        try:
            __import__(engine)
            ai_success += 1
        except Exception as e:
            logger.warning(f"⚠️  AI engine {engine} unavailable: {e}")
    
    logger.info(f"✅ AI Engines: {ai_success}/{len(ai_engines)} operational")
    
    # Test analytics engines
    analytics_engines = [
        'analytics.predictive_engine',
        'analytics.journey_engine',
        'analytics.network_engine',
        'analytics.financial_engine'
    ]
    
    analytics_success = 0
    for engine in analytics_engines:
        try:
            __import__(engine)
            analytics_success += 1
        except Exception as e:
            logger.warning(f"⚠️  Analytics engine {engine} unavailable: {e}")
    
    logger.info(f"✅ Analytics Engines: {analytics_success}/{len(analytics_engines)} operational")
    
    # System ready check
    total_success = ai_success + analytics_success
    total_engines = len(ai_engines) + len(analytics_engines)
    
    if total_success >= total_engines * 0.8:  # 80% threshold
        logger.info("🎉 System health check PASSED - Ready for production!")
        return True
    else:
        logger.warning("⚠️  System health check PARTIAL - Some features may be limited")
        return True  # Allow startup but with warnings

def main():
    """Main server startup function"""
    print("🚀 SBM AI CRM Backend Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # System health check
    if not check_system_health():
        logger.error("❌ System health check failed")
        sys.exit(1)
    
    # Import and start the FastAPI app
    try:
        from api.main import app
        logger.info("✅ FastAPI application loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load FastAPI application: {e}")
        sys.exit(1)
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"🌐 Starting server on http://{host}:{port}")
    logger.info("📊 Available features:")
    features = [
        "Customer Data Platform (CDP)",
        "A/B Testing Framework", 
        "Multi-Touch Revenue Attribution",
        "Real-time Behavioral Analytics",
        "Advanced AI Segmentation",
        "Predictive Customer Analytics",
        "Customer Journey Mapping",
        "Network Social Intelligence",
        "Financial Analytics & Forecasting",
        "Real-time Monitoring & Alerts",
        "Webhook Integration",
        "18+ Chart Types for Frontend"
    ]
    
    for i, feature in enumerate(features, 1):
        logger.info(f"   {i:2d}. {feature}")
    
    print("\n🎯 Server starting... Press CTRL+C to stop")
    
    # Start the server
    try:
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()