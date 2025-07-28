#!/usr/bin/env python3
"""
Marketing Campaign Advisor API Endpoints
Provides AI-powered campaign guidance and recommendations
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime

from ...core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Request Models
class CampaignAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="Campaign description or question", min_length=10, max_length=2000)
    target_segment: Optional[str] = Field(None, description="Specific customer segment to target")
    campaign_type: Optional[str] = Field(None, description="Type of campaign (launch, promotion, engagement, etc.)")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., '100k-500k RMB')")

class QuickCampaignRequest(BaseModel):
    campaign_goal: str = Field(..., description="Primary campaign goal")
    target_audience: str = Field(..., description="Target audience description")
    budget: Optional[str] = Field(None, description="Available budget")

# Initialize campaign advisor lazily to avoid blocking route registration
def get_campaign_advisor():
    """Get campaign advisor instance (lazy initialization)"""
    if not hasattr(get_campaign_advisor, '_instance'):
        from ...ai_engine.campaign_advisor import CampaignAdvisor
        get_campaign_advisor._instance = CampaignAdvisor()
    return get_campaign_advisor._instance

@router.get("/health")
async def campaign_advisor_health_check():
    """🏥 Campaign Advisor Health Check"""
    try:
        return {
            "status": "healthy",
            "service": "Campaign Advisor",
            "features": [
                "AI-powered campaign analysis",
                "Customer database insights",
                "Super Brand Mall Shanghai context",
                "Template recommendations",
                "Quick guidance generation"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Campaign advisor health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/analyze")
async def analyze_campaign_opportunity(
    request: CampaignAnalysisRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🤖 AI-Powered Campaign Analysis for Super Brand Mall Shanghai
    
    Analyzes your campaign ideas using customer database insights and provides:
    - Target audience recommendations based on actual customer data
    - Specific store partnerships at Super Brand Mall Shanghai  
    - Budget allocation strategies
    - Implementation guidance with actionable steps
    """
    logger.info(f"👤 {current_user.get('username')} requesting AI campaign analysis")
    logger.info(f"📝 Prompt: {request.prompt[:100]}...")
    
    try:
        # Validate inputs
        if len(request.prompt.strip()) < 10:
            raise HTTPException(status_code=400, detail="Prompt too short - please provide more details")
        
        # Perform AI-powered campaign analysis
        campaign_advisor = get_campaign_advisor()
        analysis_result = campaign_advisor.analyze_campaign_opportunity(
            prompt=request.prompt,
            target_segment=request.target_segment,
            campaign_type=request.campaign_type,
            budget_range=request.budget_range
        )
        
        # Check for errors in analysis
        if 'error' in analysis_result:
            logger.warning(f"Campaign analysis had issues: {analysis_result['error']}")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "user": current_user.get('username'),
            "generated_at": datetime.now().isoformat(),
            "note": "AI-powered recommendations based on your actual customer database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI campaign analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/quick-guidance")
async def get_quick_campaign_guidance(
    request: QuickCampaignRequest,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    ⚡ Quick Campaign Guidance
    
    Get rapid campaign recommendations for simple scenarios.
    Ideal for quick decisions and initial planning.
    """
    logger.info(f"👤 {current_user.get('username')} requesting quick campaign guidance")
    
    try:
        # Create a structured prompt for quick analysis
        quick_prompt = f"""
        Campaign Goal: {request.campaign_goal}
        Target Audience: {request.target_audience}
        Budget: {request.budget or 'Not specified'}
        
        Please provide quick guidance for a marketing campaign at Super Brand Mall Shanghai.
        """
        
        # Use the main analysis function with simplified parameters
        campaign_advisor = get_campaign_advisor()
        result = campaign_advisor.analyze_campaign_opportunity(
            prompt=quick_prompt,
            campaign_type="quick_guidance"
        )
        
        return {
            "status": "success",
            "quick_guidance": result.get('campaign_analysis', {}),
            "customer_insights": result.get('customer_insights', {}),
            "note": "Quick guidance based on limited input - use /analyze for detailed recommendations",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Quick guidance failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick guidance failed: {str(e)}")

@router.get("/mall-context")
async def get_mall_context(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🏢 Super Brand Mall Shanghai Context
    
    Comprehensive information about the mall, tenants, and target demographics
    to inform your campaign planning decisions.
    """
    logger.info(f"👤 {current_user.get('username')} requesting mall context")
    
    try:
        campaign_advisor = get_campaign_advisor()
        mall_context = campaign_advisor._get_mall_context()
        
        return {
            "status": "success",
            "mall_context": mall_context,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Mall context retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mall context retrieval failed: {str(e)}")

@router.get("/customer-insights")
async def get_current_customer_insights(
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365)
) -> Dict[str, Any]:
    """
    📊 Live Customer Database Insights
    
    Real-time analysis of customer behavior, spending patterns, demographics,
    and store preferences to inform campaign targeting decisions.
    """
    logger.info(f"👤 {current_user.get('username')} requesting customer insights for {days} days")
    
    try:
        # Get customer insights from database
        campaign_advisor = get_campaign_advisor()
        insights = campaign_advisor._analyze_customer_database()
        
        return {
            "status": "success",
            "customer_insights": insights,
            "analysis_period_days": days,
            "note": "Live data from your customer database - updated automatically",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Customer insights retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Customer insights retrieval failed: {str(e)}")

@router.get("/templates")
async def get_campaign_templates(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📋 Pre-built Campaign Templates
    
    Ready-to-use campaign templates for common scenarios at Super Brand Mall Shanghai.
    Templates can be customized using the AI analysis endpoint.
    """
    logger.info(f"👤 {current_user.get('username')} requesting campaign templates")
    
    try:
        campaign_advisor = get_campaign_advisor()
        templates = campaign_advisor.get_campaign_templates()
        
        return {
            "status": "success",
            "templates": templates,
            "description": "Pre-built campaign templates for Super Brand Mall Shanghai",
            "usage_note": "These templates can be customized using the /analyze endpoint",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Template retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Template retrieval failed: {str(e)}")