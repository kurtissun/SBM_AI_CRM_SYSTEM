"""
SBM Configuration Management API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.security import get_current_user, require_permission
from ...core.sbm_config import sbm_config, SBMGoal, SBMFocus

router = APIRouter()

class UpdateGoalsRequest(BaseModel):
    goals: List[SBMGoal]

class UpdateFocusAreasRequest(BaseModel):
    focus_areas: List[SBMFocus]

class UpdateAIPreferencesRequest(BaseModel):
    preferences: Dict[str, Any]

@router.get("/config")
async def get_sbm_configuration(
    current_user: dict = Depends(require_permission("admin"))
):
    """
    Get current SBM business configuration
    """
    try:
        config = sbm_config.get_config()
        return {
            "configuration": config.dict(),
            "ai_context": sbm_config.get_ai_context()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@router.get("/config/goals")
async def get_business_goals(
    priority: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get business goals with optional filtering
    """
    try:
        if priority:
            goals = sbm_config.get_goals_by_priority(priority)
        elif category:
            goals = sbm_config.get_goals_by_category(category)
        else:
            goals = sbm_config.config.goals
        
        return {
            "goals": [g.dict() for g in goals],
            "performance_summary": sbm_config._calculate_performance_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get goals: {str(e)}")

@router.put("/config/goals")
async def update_business_goals(
    request: UpdateGoalsRequest,
    current_user: dict = Depends(require_permission("admin"))
):
    """
    Update business goals (admin only)
    """
    try:
        sbm_config.update_goals(request.goals)
        return {
            "message": "Goals updated successfully",
            "updated_count": len(request.goals),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update goals: {str(e)}")

@router.get("/config/focus-areas")
async def get_focus_areas(
    segment_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get business focus areas
    """
    try:
        if segment_id is not None:
            focus_areas = sbm_config.get_focus_areas_for_segment(segment_id)
        else:
            focus_areas = sbm_config.config.focus_areas
        
        return {
            "focus_areas": [f.dict() for f in focus_areas],
            "total": len(focus_areas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get focus areas: {str(e)}")

@router.put("/config/focus-areas")
async def update_focus_areas(
    request: UpdateFocusAreasRequest,
    current_user: dict = Depends(require_permission("admin"))
):
    """
    Update business focus areas (admin only)
    """
    try:
        sbm_config.update_focus_areas(request.focus_areas)
        return {
            "message": "Focus areas updated successfully",
            "updated_count": len(request.focus_areas),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update focus areas: {str(e)}")

@router.get("/config/ai-preferences")
async def get_ai_preferences(
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI assistant preferences
    """
    try:
        return {
            "preferences": sbm_config.config.ai_preferences,
            "response_styles": ["professional_friendly", "formal", "casual", "technical"],
            "risk_levels": ["conservative", "moderate", "aggressive"],
            "innovation_levels": ["low", "medium", "high"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI preferences: {str(e)}")

@router.put("/config/ai-preferences")
async def update_ai_preferences(
    request: UpdateAIPreferencesRequest,
    current_user: dict = Depends(require_permission("admin"))
):
    """
    Update AI assistant preferences (admin only)
    """
    try:
        sbm_config.update_ai_preferences(request.preferences)
        return {
            "message": "AI preferences updated successfully",
            "updated_preferences": request.preferences,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update AI preferences: {str(e)}")

@router.get("/config/performance")
async def get_goal_performance(
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed goal performance metrics
    """
    try:
        goals = sbm_config.config.goals
        performance_details = []
        
        for goal in goals:
            progress = (goal.current_value / goal.target_value * 100) if goal.target_value else 0
            status = "on_track" if progress >= 80 else "needs_attention" if progress >= 50 else "at_risk"
            
            performance_details.append({
                "goal_id": goal.goal_id,
                "name": goal.name,
                "priority": goal.priority,
                "progress_percentage": progress,
                "status": status,
                "current_value": goal.current_value,
                "target_value": goal.target_value,
                "gap": goal.target_value - goal.current_value if goal.target_value and goal.current_value else None,
                "timeline": goal.timeline,
                "kpis": goal.kpis
            })
        
        # Sort by priority and progress
        performance_details.sort(key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}[x["priority"]], 
            -x["progress_percentage"]
        ))
        
        summary = sbm_config._calculate_performance_summary()
        
        return {
            "performance_summary": summary,
            "goal_details": performance_details,
            "recommendations": _generate_performance_recommendations(performance_details)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")

def _generate_performance_recommendations(performance_details: List[Dict]) -> List[str]:
    """Generate recommendations based on performance"""
    recommendations = []
    
    # Check for at-risk goals
    at_risk = [g for g in performance_details if g["status"] == "at_risk"]
    if at_risk:
        recommendations.append(f"Urgent attention needed for {len(at_risk)} at-risk goals")
    
    # Check high priority goals
    high_priority_behind = [g for g in performance_details 
                           if g["priority"] == "high" and g["progress_percentage"] < 80]
    if high_priority_behind:
        recommendations.append(f"Accelerate efforts on {len(high_priority_behind)} high-priority goals")
    
    # General recommendations
    avg_progress = sum(g["progress_percentage"] for g in performance_details) / len(performance_details) if performance_details else 0
    if avg_progress < 70:
        recommendations.append("Consider reallocating resources to improve overall goal achievement")
    elif avg_progress > 90:
        recommendations.append("Excellent progress! Consider setting more ambitious targets")
    
    return recommendations