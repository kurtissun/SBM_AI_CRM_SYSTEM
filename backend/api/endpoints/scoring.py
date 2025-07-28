"""
Lead Scoring and Qualification API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...leads.scoring_engine import LeadScoringEngine, ScoreType, LeadStatus, LeadQuality

router = APIRouter()

class ScoreCustomerRequest(BaseModel):
    customer_id: str
    score_type: Optional[ScoreType] = None

class QualifyLeadRequest(BaseModel):
    customer_id: str
    threshold: Optional[float] = 70.0

class ScoreResponse(BaseModel):
    success: bool
    customer_id: str
    score_result: Optional[Dict[str, Any]] = None
    message: str

@router.post("/score", response_model=ScoreResponse)
async def calculate_customer_score(
    request: ScoreCustomerRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate lead score for a customer"""
    try:
        scoring_engine = LeadScoringEngine(db)
        score_result = scoring_engine.calculate_lead_score(
            customer_id=request.customer_id,
            score_type=request.score_type
        )
        
        return ScoreResponse(
            success=True,
            customer_id=request.customer_id,
            score_result=score_result,
            message="Score calculated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")

@router.post("/qualify")
async def qualify_lead(
    request: QualifyLeadRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Qualify a lead based on score and criteria"""
    try:
        scoring_engine = LeadScoringEngine(db)
        qualification_result = scoring_engine.qualify_lead(
            customer_id=request.customer_id,
            threshold=request.threshold
        )
        
        return qualification_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to qualify lead: {str(e)}")

@router.get("/insights/{customer_id}")
async def get_lead_insights(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive lead insights and analytics"""
    try:
        scoring_engine = LeadScoringEngine(db)
        insights = scoring_engine.get_lead_insights(customer_id)
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lead insights: {str(e)}")

@router.get("/segment/{segment_id}/analysis")
async def get_segment_scoring_analysis(
    segment_id: int,
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Analyze lead scoring patterns for a customer segment"""
    try:
        scoring_engine = LeadScoringEngine(db)
        analysis = scoring_engine.get_segment_scoring_analysis(segment_id)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze segment scoring: {str(e)}")

@router.get("/dashboard")
async def get_scoring_dashboard(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get lead scoring dashboard overview"""
    try:
        from ...leads.scoring_engine import LeadScore, LeadQualification
        
        # Score distribution
        recent_scores = db.query(LeadScore).filter(
            LeadScore.score_type == ScoreType.COMPOSITE.value,
            LeadScore.calculated_at >= datetime.now() - timedelta(days=30)
        ).all()
        
        if recent_scores:
            scores = [s.score_value for s in recent_scores]
            avg_score = sum(scores) / len(scores)
            
            score_distribution = {
                "90-100": len([s for s in scores if s >= 90]),
                "80-89": len([s for s in scores if 80 <= s < 90]),
                "70-79": len([s for s in scores if 70 <= s < 80]),
                "60-69": len([s for s in scores if 60 <= s < 70]),
                "50-59": len([s for s in scores if 50 <= s < 60]),
                "0-49": len([s for s in scores if s < 50])
            }
        else:
            avg_score = 0
            score_distribution = {}
        
        # Qualification distribution
        qualifications = db.query(LeadQualification).all()
        
        status_distribution = {}
        quality_distribution = {}
        
        for qual in qualifications:
            status_distribution[qual.lead_status] = status_distribution.get(qual.lead_status, 0) + 1
            quality_distribution[qual.lead_quality] = quality_distribution.get(qual.lead_quality, 0) + 1
        
        # High potential leads
        high_potential = len([s for s in scores if s >= 80]) if recent_scores else 0
        qualified_leads = status_distribution.get(LeadStatus.MQL.value, 0) + status_distribution.get(LeadStatus.SQL.value, 0)
        
        # Conversion funnel
        funnel_metrics = {
            "total_leads": len(recent_scores),
            "warm_leads": len([s for s in scores if s >= 50]) if recent_scores else 0,
            "qualified_leads": qualified_leads,
            "hot_leads": high_potential,
            "conversion_rate": (qualified_leads / len(recent_scores) * 100) if recent_scores else 0
        }
        
        return {
            "summary_metrics": {
                "total_scored_customers": len(recent_scores),
                "average_score": avg_score,
                "high_potential_leads": high_potential,
                "qualified_leads": qualified_leads,
                "qualification_rate": (qualified_leads / len(recent_scores) * 100) if recent_scores else 0
            },
            "score_distribution": score_distribution,
            "status_distribution": status_distribution,
            "quality_distribution": quality_distribution,
            "conversion_funnel": funnel_metrics,
            "trends": _calculate_scoring_trends(db),
            "recommendations": _generate_scoring_dashboard_recommendations(
                avg_score, qualified_leads, len(recent_scores)
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scoring dashboard: {str(e)}")

@router.get("/leaderboard")
async def get_lead_leaderboard(
    limit: int = Query(50, le=500),
    score_threshold: float = Query(0, ge=0, le=100),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get top leads leaderboard by score"""
    try:
        from ...leads.scoring_engine import LeadScore
        from ...core.database import Customer
        
        # Get recent high-scoring leads
        top_leads = db.query(LeadScore, Customer).join(
            Customer, LeadScore.customer_id == Customer.customer_id
        ).filter(
            LeadScore.score_type == ScoreType.COMPOSITE.value,
            LeadScore.score_value >= score_threshold,
            LeadScore.calculated_at >= datetime.now() - timedelta(days=30)
        ).order_by(LeadScore.score_value.desc()).limit(limit).all()
        
        leaderboard = []
        for lead_score, customer in top_leads:
            leaderboard.append({
                "rank": len(leaderboard) + 1,
                "customer_id": customer.customer_id,
                "score": lead_score.score_value,
                "score_factors": lead_score.score_factors,
                "customer_info": {
                    "age": customer.age,
                    "gender": customer.gender,
                    "segment_id": customer.segment_id,
                    "rating_id": customer.rating_id
                },
                "calculated_at": lead_score.calculated_at.isoformat()
            })
        
        return {
            "leaderboard": leaderboard,
            "total_entries": len(leaderboard),
            "score_threshold": score_threshold,
            "date_range": "Last 30 days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")

@router.get("/analytics/scoring-performance")
async def get_scoring_performance_analytics(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get detailed scoring performance analytics"""
    try:
        from ...leads.scoring_engine import LeadScore, ScoringEvent
        
        # Calculate time range
        time_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        # Get scoring activity
        scoring_events = db.query(ScoringEvent).filter(
            ScoringEvent.timestamp >= start_date
        ).all()
        
        # Analyze scoring patterns
        daily_scores = {}
        score_changes = []
        
        for event in scoring_events:
            day = event.timestamp.date().isoformat()
            daily_scores[day] = daily_scores.get(day, 0) + 1
            if event.score_change:
                score_changes.append(event.score_change)
        
        # Model performance metrics
        recent_scores = db.query(LeadScore).filter(
            LeadScore.calculated_at >= start_date,
            LeadScore.score_type == ScoreType.COMPOSITE.value
        ).all()
        
        if recent_scores:
            scores = [s.score_value for s in recent_scores]
            score_variance = np.var(scores) if len(scores) > 1 else 0
            
            # Score stability (lower variance = more stable)
            stability_score = max(0, 100 - score_variance)
        else:
            scores = []
            stability_score = 0
        
        return {
            "time_range": time_range,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "days_analyzed": (datetime.now() - start_date).days
            },
            "scoring_activity": {
                "total_scores_calculated": len(recent_scores),
                "total_scoring_events": len(scoring_events),
                "daily_scoring_activity": daily_scores,
                "average_daily_scores": len(recent_scores) / max(1, (datetime.now() - start_date).days)
            },
            "score_dynamics": {
                "score_changes": len(score_changes),
                "average_score_change": sum(score_changes) / len(score_changes) if score_changes else 0,
                "positive_changes": len([c for c in score_changes if c > 0]),
                "negative_changes": len([c for c in score_changes if c < 0])
            },
            "model_performance": {
                "score_stability": stability_score,
                "score_variance": score_variance,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "score_range": {
                    "min": min(scores) if scores else 0,
                    "max": max(scores) if scores else 0
                }
            },
            "insights": _generate_performance_insights(daily_scores, score_changes, stability_score)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")

# Helper functions
def _calculate_scoring_trends(db: Session) -> Dict[str, Any]:
    """Calculate scoring trends over time"""
    try:
        from ...leads.scoring_engine import LeadScore
        
        # Get scores from last 60 days to calculate trend
        recent_scores = db.query(LeadScore).filter(
            LeadScore.score_type == ScoreType.COMPOSITE.value,
            LeadScore.calculated_at >= datetime.now() - timedelta(days=60)
        ).order_by(LeadScore.calculated_at).all()
        
        if len(recent_scores) < 2:
            return {"trend": "insufficient_data"}
        
        # Split into two periods
        mid_point = len(recent_scores) // 2
        older_scores = recent_scores[:mid_point]
        newer_scores = recent_scores[mid_point:]
        
        older_avg = sum(s.score_value for s in older_scores) / len(older_scores)
        newer_avg = sum(s.score_value for s in newer_scores) / len(newer_scores)
        
        trend_direction = "improving" if newer_avg > older_avg else "declining" if newer_avg < older_avg else "stable"
        trend_magnitude = abs(newer_avg - older_avg)
        
        return {
            "trend": trend_direction,
            "magnitude": trend_magnitude,
            "older_period_avg": older_avg,
            "newer_period_avg": newer_avg,
            "change_percentage": ((newer_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating scoring trends: {e}")
        return {"trend": "error", "message": str(e)}

def _generate_scoring_dashboard_recommendations(avg_score: float, qualified_leads: int, 
                                              total_leads: int) -> List[str]:
    """Generate recommendations for scoring dashboard"""
    recommendations = []
    
    if total_leads == 0:
        recommendations.append("Start calculating lead scores to build scoring insights")
        return recommendations
    
    if avg_score < 50:
        recommendations.append("Low average score - review scoring criteria and lead quality")
    
    qualification_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
    if qualification_rate < 20:
        recommendations.append("Low qualification rate - optimize lead nurturing processes")
    elif qualification_rate > 80:
        recommendations.append("High qualification rate - consider raising qualification thresholds")
    
    if qualified_leads < 10:
        recommendations.append("Focus on generating more qualified leads through targeted campaigns")
    
    return recommendations

def _generate_performance_insights(daily_scores: Dict[str, int], score_changes: List[float], 
                                 stability_score: float) -> List[str]:
    """Generate insights from performance analytics"""
    insights = []
    
    if not daily_scores:
        insights.append("No scoring activity detected in the selected period")
        return insights
    
    # Activity patterns
    max_daily_scores = max(daily_scores.values()) if daily_scores else 0
    avg_daily_scores = sum(daily_scores.values()) / len(daily_scores) if daily_scores else 0
    
    if max_daily_scores > avg_daily_scores * 2:
        insights.append("Scoring activity shows significant daily variation")
    
    # Score change patterns
    if score_changes:
        positive_changes = len([c for c in score_changes if c > 0])
        negative_changes = len([c for c in score_changes if c < 0])
        
        if positive_changes > negative_changes * 2:
            insights.append("Predominantly positive score changes indicate improving lead quality")
        elif negative_changes > positive_changes * 2:
            insights.append("High number of negative score changes - investigate lead quality issues")
    
    # Stability insights
    if stability_score > 80:
        insights.append("High score stability indicates consistent scoring model performance")
    elif stability_score < 50:
        insights.append("Low score stability suggests model needs calibration")
    
    return insights