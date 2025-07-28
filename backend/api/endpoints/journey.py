"""
Customer Journey and Lifecycle API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...journey.lifecycle_manager import CustomerLifecycleManager, TouchpointType, LifecycleStage

router = APIRouter()

class TrackTouchpointRequest(BaseModel):
    customer_id: str
    touchpoint_type: TouchpointType
    metadata: Optional[Dict[str, Any]] = {}

class TouchpointResponse(BaseModel):
    success: bool
    touchpoint_id: Optional[int] = None
    message: str

@router.post("/touchpoints/track", response_model=TouchpointResponse)
async def track_customer_touchpoint(
    request: TrackTouchpointRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track a customer touchpoint"""
    try:
        lifecycle_manager = CustomerLifecycleManager(db)
        
        touchpoint = lifecycle_manager.track_touchpoint(
            customer_id=request.customer_id,
            touchpoint_type=request.touchpoint_type,
            metadata=request.metadata
        )
        
        return TouchpointResponse(
            success=True,
            touchpoint_id=touchpoint.id,
            message="Touchpoint tracked successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track touchpoint: {str(e)}")

@router.get("/journey/{customer_id}")
async def get_customer_journey(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive journey analytics for a customer"""
    try:
        lifecycle_manager = CustomerLifecycleManager(db)
        journey_analytics = lifecycle_manager.get_journey_analytics(customer_id)
        
        return journey_analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get journey analytics: {str(e)}")

@router.get("/journey/{customer_id}/predict-next-stage")
async def predict_next_lifecycle_stage(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict the next lifecycle stage for a customer"""
    try:
        lifecycle_manager = CustomerLifecycleManager(db)
        prediction = lifecycle_manager.predict_next_stage(customer_id)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to predict next stage: {str(e)}")

@router.get("/segment/{segment_id}/journey-patterns")
async def get_segment_journey_patterns(
    segment_id: int,
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Analyze journey patterns for a customer segment"""
    try:
        lifecycle_manager = CustomerLifecycleManager(db)
        patterns = lifecycle_manager.get_segment_journey_patterns(segment_id)
        
        return patterns
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze segment patterns: {str(e)}")

@router.get("/analytics/journey-overview")
async def get_journey_overview(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get overall journey analytics overview"""
    try:
        # Get stage distribution across all customers
        from ...journey.lifecycle_manager import CustomerJourney
        
        stage_counts = {}
        for stage in LifecycleStage:
            count = db.query(CustomerJourney).filter(
                CustomerJourney.current_stage == stage.value
            ).count()
            stage_counts[stage.value] = count
        
        total_customers = sum(stage_counts.values())
        
        # Calculate health metrics
        if total_customers > 0:
            journeys = db.query(CustomerJourney).all()
            avg_health_score = sum(j.health_score for j in journeys) / len(journeys)
            high_risk_count = len([j for j in journeys if j.risk_score > 70])
            high_momentum_count = len([j for j in journeys if j.momentum_score > 50])
        else:
            avg_health_score = 0
            high_risk_count = 0
            high_momentum_count = 0
        
        return {
            "total_customers_tracked": total_customers,
            "stage_distribution": stage_counts,
            "stage_percentages": {
                stage: (count / total_customers * 100) if total_customers > 0 else 0
                for stage, count in stage_counts.items()
            },
            "health_metrics": {
                "average_health_score": avg_health_score,
                "high_risk_customers": high_risk_count,
                "high_momentum_customers": high_momentum_count,
                "health_percentage": (avg_health_score / 100) * 100 if avg_health_score else 0
            },
            "recommendations": _generate_journey_overview_recommendations(stage_counts, avg_health_score)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get journey overview: {str(e)}")

def _generate_journey_overview_recommendations(stage_counts: Dict[str, int], 
                                             avg_health_score: float) -> List[str]:
    """Generate recommendations based on journey overview"""
    recommendations = []
    total = sum(stage_counts.values())
    
    if total == 0:
        return ["Start tracking customer touchpoints to build journey analytics"]
    
    # Check for bottlenecks
    consideration_pct = (stage_counts.get(LifecycleStage.CONSIDERATION.value, 0) / total) * 100
    if consideration_pct > 40:
        recommendations.append("High consideration stage accumulation - optimize conversion tactics")
    
    # Check for dormancy
    dormant_pct = (stage_counts.get(LifecycleStage.DORMANT.value, 0) / total) * 100
    if dormant_pct > 20:
        recommendations.append("High dormancy rate - implement reactivation campaigns")
    
    # Check health score
    if avg_health_score < 50:
        recommendations.append("Low average health score - increase engagement frequency")
    
    # Check advocacy
    advocacy_pct = (stage_counts.get(LifecycleStage.ADVOCACY.value, 0) / total) * 100
    if advocacy_pct < 10:
        recommendations.append("Low advocacy rate - implement referral programs")
    
    return recommendations