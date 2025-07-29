#!/usr/bin/env python3
"""
SBM AI CRM System - Enterprise Edition Complete Server
Unified launcher with comprehensive health checks and all 22 engines
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

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'numpy',
        'pandas',
        'sklearn',  # scikit-learn imports as 'sklearn'
        'networkx',
        'anthropic',
        'aiohttp',
        'websockets',
        'redis',
        'psycopg2'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"Missing required dependencies: {', '.join(missing)}")
        logger.error("Please install with: pip install -r backend/requirements.txt")
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
        'ai_engine.insight_generator',
        'ai_engine.hyper_personalization',
        'ai_engine.generative_analytics',
        'ai_engine.local_llm_segmentation',
        'ai_engine.campaign_advisor'
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
        'analytics.financial_engine',
        'analytics.behavioral_engine'
    ]
    
    analytics_success = 0
    for engine in analytics_engines:
        try:
            __import__(engine)
            analytics_success += 1
        except Exception as e:
            logger.warning(f"⚠️  Analytics engine {engine} unavailable: {e}")
    
    logger.info(f"✅ Analytics Engines: {analytics_success}/{len(analytics_engines)} operational")
    
    # Test enterprise features
    enterprise_features = [
        'cdp.unified_profile',
        'experiments.ab_testing',
        'revenue.attribution_engine',
        'notifications.alert_engine',
        'segmentation.dynamic_engine',
        'webhooks.webhook_engine',
        'reporting.chart_engine',
        'monitoring.realtime_engine'
    ]
    
    enterprise_success = 0
    for feature in enterprise_features:
        try:
            __import__(feature)
            enterprise_success += 1
        except Exception as e:
            logger.warning(f"⚠️  Enterprise feature {feature} unavailable: {e}")
    
    logger.info(f"✅ Enterprise Features: {enterprise_success}/{len(enterprise_features)} operational")
    
    # System ready check
    total_success = ai_success + analytics_success + enterprise_success
    total_engines = len(ai_engines) + len(analytics_engines) + len(enterprise_features)
    
    if total_success >= total_engines * 0.8:  # 80% threshold
        logger.info("🎉 System health check PASSED - Ready for production!")
        return True
    else:
        logger.warning("⚠️  System health check PARTIAL - Some features may be limited")
        return True  # Allow startup but with warnings

def check_environment():
    """Check if environment is properly configured"""
    env_file = project_root / '.env'
    if not env_file.exists():
        logger.warning("⚠️  .env file not found - using default configuration")
    
    logger.info("✅ Environment configuration ready")
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
    """Main server startup function"""
    print("🚀 SBM AI CRM System - Enterprise Edition")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # System health check
    if not check_system_health():
        logger.error("❌ System health check failed")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"🌐 Starting server on http://{host}:{port}")
    logger.info("📊 Available features:")
    features = [
        "360° Customer Data Platform (CDP)",
        "A/B Testing Framework", 
        "Multi-Touch Revenue Attribution",
        "Real-time Behavioral Analytics",
        "Advanced AI Segmentation",
        "Predictive Customer Analytics (CLV, Churn)",
        "Customer Journey Mapping",
        "Network Social Intelligence",
        "Financial Analytics & Forecasting",
        "Real-time Monitoring & Alerts",
        "Webhook Integration System",
        "18+ Chart Types for Visualization",
        "Campaign Intelligence & Optimization",
        "Hyper-Personalization Engine",
        "Conversational AI Assistant",
        "Generative Analytics Reports",
        "Local LLM Segmentation",
        "Dynamic Segmentation Engine",
        "WebSocket Live Updates",
        "Enterprise Security & Auth",
        "Automated Workflow Engine",
        "Advanced Reporting System"
    ]
    
    for i, feature in enumerate(features, 1):
        logger.info(f"   {i:2d}. {feature}")
    
    print("\n🎯 Server starting... Press CTRL+C to stop")
    print("=" * 60)
    print("📚 API Documentation: http://localhost:8080/docs")  
    print("🔗 Interactive API: http://localhost:8080/redoc")
    print("🔧 Health Check: http://localhost:8080/health")
    print("📊 System Status: http://localhost:8080/api/system/status")
    print("💬 WebSocket Live Feed: ws://localhost:8080/ws/live-feed")
    print("💬 Admin AI Chat: ws://localhost:8080/ws/admin-chat")
    print("=" * 60)
    
    # Start the server
    try:
        # Import the FastAPI app
        from backend.api.main import app
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,  # Disable reload for production stability
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        logger.info("🔄 Attempting alternative startup method...")
        try:
            # Alternative: module string
            uvicorn.run(
                "backend.api.main:app",
                host=host,
                port=port,
                reload=False,
                log_level="info"
            )
        except Exception as e2:
            logger.error(f"❌ Alternative startup also failed: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()