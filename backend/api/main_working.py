"""
SBM AI CRM Backend - Working Version with Progressive Loading
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uvicorn
import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session

# Add backend directory to path for absolute imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Core imports (required)
try:
    from core.config import settings
    from core.database import init_database, get_db, Customer, Campaign, Segment
    print("✅ Core database imports successful")
except Exception as e:
    print(f"❌ Core imports failed: {e}")
    # Fallback settings
    class Settings:
        LOG_LEVEL = "INFO"
        SECRET_KEY = "fallback-secret-key"
        DATABASE_URL = "sqlite:///./sbm_crm.db"
    settings = Settings()
    def init_database(): pass
    def get_db(): yield None

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for engines
engines = {
    "clustering": None,
    "personalization": None,
    "insights": None,
    "campaign_intel": None,
    "predictive": None,
    "journey": None,
    "network": None,
    "financial": None,
    "behavioral": None,
    "cdp": None,
    "ab_testing": None,
    "attribution": None,
    "notifications": None,
    "segmentation": None,
    "webhooks": None,
    "charts": None,
    "monitoring": None
}

def safe_import_and_init(module_path, class_name, engine_key, db):
    """Safely import and initialize an engine"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        engine_class = getattr(module, class_name)
        engines[engine_key] = engine_class(db)
        logger.info(f"✅ {engine_key} engine initialized")
        return True
    except Exception as e:
        logger.warning(f"⚠️  {engine_key} engine failed to initialize: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with progressive engine loading"""
    logger.info("🚀 SBM AI CRM Backend starting up...")
    
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization issue: {e}")
    
    # Progressive engine initialization
    try:
        db = next(get_db()) if get_db else None
        if db:
            # Try to load each engine individually
            engine_configs = [
                ("ai_engine.adaptive_clustering", "AdaptiveClustering", "clustering"),
                ("ai_engine.hyper_personalization", "HyperPersonalizationEngine", "personalization"),
                ("ai_engine.insight_generator", "IntelligentInsightGenerator", "insights"),
                ("ai_engine.campaign_intelligence", "CampaignIntelligence", "campaign_intel"),
                ("analytics.predictive_engine", "PredictiveAnalyticsEngine", "predictive"),
                ("analytics.journey_engine", "JourneyAnalyticsEngine", "journey"),
                ("analytics.network_engine", "NetworkAnalyticsEngine", "network"),
                ("analytics.financial_engine", "FinancialAnalyticsEngine", "financial"),
                ("analytics.behavioral_engine", "BehavioralAnalyticsEngine", "behavioral"),
            ]
            
            loaded_count = 0
            for module_path, class_name, engine_key in engine_configs:
                if safe_import_and_init(module_path, class_name, engine_key, db):
                    loaded_count += 1
            
            logger.info(f"✅ {loaded_count}/{len(engine_configs)} engines loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Engine initialization failed: {e}")
        logger.warning("⚠️  Running in limited mode")
    
    yield
    
    # Shutdown
    logger.info("🛑 SBM AI CRM Backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="SBM AI CRM Backend - Working Edition",
    description="AI-powered CRM with progressive engine loading",
    version="2.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ==================== HEALTH & STATUS ENDPOINTS ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check with engine status"""
    operational_count = sum(1 for engine in engines.values() if engine is not None)
    
    return {
        "status": "healthy" if operational_count > 5 else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.1",
        "engines_operational": f"{operational_count}/{len(engines)}",
        "engine_status": {k: v is not None for k, v in engines.items()}
    }

@app.get("/api/system/status", tags=["System"])
async def system_status(db: Session = Depends(get_db)):
    """System status with real metrics"""
    try:
        # Get basic metrics if database is available
        metrics = {}
        if db:
            try:
                total_customers = db.query(Customer).count()
                total_campaigns = db.query(Campaign).count()
                total_segments = db.query(Segment).count()
                metrics = {
                    "customers": {"total": total_customers},
                    "campaigns": {"total": total_campaigns},
                    "segments": {"total": total_segments}
                }
            except:
                metrics = {"note": "Database tables not ready"}
        
        operational_count = sum(1 for engine in engines.values() if engine is not None)
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "engines": {
                "operational": operational_count,
                "total": len(engines)
            }
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {"status": "error", "message": str(e)}

# ==================== CUSTOMER ENDPOINTS ====================

@app.get("/api/customers", tags=["Customers"])
async def get_customers(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get customers with optional AI insights"""
    try:
        if not db:
            return {"customers": [], "total": 0, "message": "Database not available"}
        
        customers = db.query(Customer).offset(offset).limit(limit).all()
        total = db.query(Customer).count()
        
        # Add AI insights if available
        insights = None
        if engines["insights"]:
            try:
                insights = engines["insights"].generate_insights(
                    analysis_type="customer_overview",
                    time_period=30
                )
            except:
                pass
        
        return {
            "customers": [
                {
                    "id": c.customer_id,
                    "name": getattr(c, 'name', 'N/A'),
                    "email": getattr(c, 'email', 'N/A'),
                    "age": c.age,
                    "gender": c.gender,
                    "location": c.location,
                    "total_spent": getattr(c, 'total_spent', 0),
                    "created_at": c.created_at
                } for c in customers
            ],
            "total": total,
            "insights": insights,
            "ai_available": engines["insights"] is not None
        }
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", tags=["Customers"])
async def get_customer_360_view(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive customer view"""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        profile_data = {
            "basic_info": {
                "id": customer.customer_id,
                "name": getattr(customer, 'name', 'N/A'),
                "email": getattr(customer, 'email', 'N/A'),
                "age": customer.age,
                "gender": customer.gender,
                "location": customer.location
            },
            "financial_metrics": {
                "total_spent": getattr(customer, 'total_spent', 0),
                "purchase_frequency": getattr(customer, 'purchase_frequency', 0)
            }
        }
        
        # Add predictions if available
        if engines["predictive"]:
            try:
                profile_data["predictions"] = {
                    "clv": engines["predictive"].predict_customer_lifetime_value(customer_id),
                    "churn_risk": engines["predictive"].predict_churn_probability(customer_id)
                }
            except:
                profile_data["predictions"] = {"note": "Predictions not available"}
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer 360 view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CAMPAIGN ENDPOINTS ====================

@app.get("/api/campaigns", tags=["Campaigns"])
async def get_campaigns(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get campaigns with optional AI insights"""
    try:
        if not db:
            return {"campaigns": [], "total": 0, "message": "Database not available"}
        
        campaigns = db.query(Campaign).limit(limit).all()
        total = db.query(Campaign).count()
        
        return {
            "campaigns": [
                {
                    "id": getattr(c, 'campaign_id', str(c.id)),
                    "name": c.name,
                    "status": c.status,
                    "budget": c.budget,
                    "created_at": c.created_at
                } for c in campaigns
            ],
            "total": total,
            "ai_available": engines["campaign_intel"] is not None
        }
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_analytics_dashboard(time_period: int = 30):
    """Get basic analytics dashboard"""
    try:
        dashboard_data = {
            "time_period": f"Last {time_period} days",
            "live_metrics": {
                "active_users": 0,
                "revenue_today": 0,
                "conversion_rate": 0
            },
            "engines_status": {
                "financial": engines["financial"] is not None,
                "behavioral": engines["behavioral"] is not None,
                "predictive": engines["predictive"] is not None
            }
        }
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} was not found",
            "documentation": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# ==================== ROOT ENDPOINT ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    operational_count = sum(1 for engine in engines.values() if engine is not None)
    
    return {
        "name": "SBM AI CRM Backend - Working Edition",
        "version": "2.0.1",
        "status": "operational",
        "engines_loaded": f"{operational_count}/{len(engines)}",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "key_endpoints": {
            "health": "/health",
            "system_status": "/api/system/status",
            "customers": "/api/customers",
            "campaigns": "/api/campaigns",
            "analytics": "/api/analytics/dashboard"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_working:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )