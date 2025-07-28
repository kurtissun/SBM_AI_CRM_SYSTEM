"""
Advanced Dynamic Segmentation API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...segmentation.dynamic_engine import (
    DynamicSegmentationEngine,
    SegmentType,
    SegmentStatus,
    UpdateFrequency,
    CriteriaOperator,
    LogicalOperator
)

router = APIRouter()
logger = logging.getLogger(__name__)

class SegmentCriteriaRequest(BaseModel):
    field_name: str
    field_type: str = "customer"
    operator: str
    value: Any
    logical_operator: str = LogicalOperator.AND.value
    group_id: Optional[str] = None
    priority: int = 1
    is_dynamic: bool = False
    time_window_days: Optional[int] = None
    relative_date: bool = False

class DynamicSegmentRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    segment_type: str
    criteria: Dict[str, Any]
    ml_config: Dict[str, Any] = {}
    target_size: Optional[int] = None
    priority: int = 1
    tags: List[str] = []
    update_frequency: str = UpdateFrequency.DAILY.value
    auto_update: bool = True
    exclusion_rules: List[Dict[str, Any]] = []
    detailed_criteria: List[SegmentCriteriaRequest] = []

class PredictiveSegmentRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    target_behavior: str  # What to predict (e.g., "purchase", "churn")
    features: List[str] = []
    model_type: str = "random_forest"
    threshold: float = 0.7
    training_window_days: int = 90
    target_size: Optional[int] = None
    tags: List[str] = []
    update_frequency: str = UpdateFrequency.DAILY.value

class SegmentResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/segments", response_model=SegmentResponse)
async def create_dynamic_segment(
    request: DynamicSegmentRequest,
    current_user: dict = Depends(require_permission("manage_segments")),
    db: Session = Depends(get_db)
):
    """Create a new dynamic segment"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        
        segment_config = {
            "name": request.name,
            "description": request.description,
            "segment_type": request.segment_type,
            "criteria": request.criteria,
            "ml_config": request.ml_config,
            "target_size": request.target_size,
            "priority": request.priority,
            "tags": request.tags,
            "update_frequency": request.update_frequency,
            "auto_update": request.auto_update,
            "exclusion_rules": request.exclusion_rules,
            "created_by": current_user.get("username", "unknown")
        }
        
        # Add detailed criteria if provided
        if request.detailed_criteria:
            segment_config["detailed_criteria"] = [
                criteria.dict() for criteria in request.detailed_criteria
            ]
        
        segment_id = segmentation_engine.create_dynamic_segment(segment_config)
        
        return SegmentResponse(
            success=True,
            message="Dynamic segment created successfully",
            data={"segment_id": segment_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create segment: {str(e)}")

@router.post("/segments/predictive", response_model=SegmentResponse)
async def create_predictive_segment(
    request: PredictiveSegmentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("manage_segments")),
    db: Session = Depends(get_db)
):
    """Create a ML-powered predictive segment"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        
        config = {
            "name": request.name,
            "description": request.description,
            "target_behavior": request.target_behavior,
            "ml_config": {
                "features": request.features,
                "model_type": request.model_type,
                "threshold": request.threshold,
                "training_window_days": request.training_window_days
            },
            "target_size": request.target_size,
            "tags": request.tags,
            "update_frequency": request.update_frequency,
            "created_by": current_user.get("username", "unknown")
        }
        
        # Create predictive segment in background
        background_tasks.add_task(
            _create_predictive_segment_background,
            db, config
        )
        
        return SegmentResponse(
            success=True,
            message="Predictive segment creation started",
            data={"status": "processing"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create predictive segment: {str(e)}")

@router.get("/segments")
async def list_segments(
    segment_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_segments")),
    db: Session = Depends(get_db)
):
    """List dynamic segments with filtering"""
    try:
        from ...segmentation.dynamic_engine import DynamicSegment
        
        query = db.query(DynamicSegment)
        
        if segment_type:
            query = query.filter(DynamicSegment.segment_type == segment_type)
        
        if status:
            query = query.filter(DynamicSegment.status == status)
        
        if tags:
            # Filter by tags (simplified - would need proper JSON querying)
            tag_list = tags.split(",")
            # query = query.filter(DynamicSegment.tags.contains(tag_list))
        
        segments = query.order_by(DynamicSegment.created_at.desc()).offset(offset).limit(limit).all()
        
        segment_data = []
        for segment in segments:
            segment_data.append({
                "id": segment.id,
                "name": segment.name,
                "description": segment.description,
                "segment_type": segment.segment_type,
                "status": segment.status,
                "current_size": segment.current_size,
                "target_size": segment.target_size,
                "conversion_rate": segment.conversion_rate,
                "engagement_rate": segment.engagement_rate,
                "revenue_per_customer": segment.revenue_per_customer,
                "performance_score": segment.performance_score,
                "update_frequency": segment.update_frequency,
                "auto_update": segment.auto_update,
                "last_updated": segment.last_updated.isoformat() if segment.last_updated else None,
                "next_update": segment.next_update.isoformat() if segment.next_update else None,
                "tags": segment.tags,
                "created_at": segment.created_at.isoformat(),
                "created_by": segment.created_by
            })
        
        return {
            "segments": segment_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(segment_data)
            },
            "filters": {
                "segment_type": segment_type,
                "status": status,
                "tags": tags
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list segments: {str(e)}")

@router.get("/segments/{segment_id}")
async def get_segment_details(
    segment_id: str,
    current_user: dict = Depends(require_permission("view_segments")),
    db: Session = Depends(get_db)
):
    """Get detailed segment information"""
    try:
        from ...segmentation.dynamic_engine import DynamicSegment, SegmentCriteria
        
        segment = db.query(DynamicSegment).filter(DynamicSegment.id == segment_id).first()
        
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        # Get detailed criteria
        criteria = db.query(SegmentCriteria).filter(
            SegmentCriteria.segment_id == segment_id
        ).all()
        
        criteria_data = []
        for criterion in criteria:
            criteria_data.append({
                "id": criterion.id,
                "field_name": criterion.field_name,
                "field_type": criterion.field_type,
                "operator": criterion.operator,
                "value": criterion.value,
                "logical_operator": criterion.logical_operator,
                "group_id": criterion.group_id,
                "priority": criterion.priority,
                "is_dynamic": criterion.is_dynamic,
                "time_window_days": criterion.time_window_days,
                "relative_date": criterion.relative_date,
                "selectivity": criterion.selectivity,
                "execution_time_ms": criterion.execution_time_ms
            })
        
        return {
            "id": segment.id,
            "name": segment.name,
            "description": segment.description,
            "segment_type": segment.segment_type,
            "status": segment.status,
            "criteria": segment.criteria,
            "detailed_criteria": criteria_data,
            "ml_config": segment.ml_config,
            "current_size": segment.current_size,
            "target_size": segment.target_size,
            "priority": segment.priority,
            "tags": segment.tags,
            "performance_metrics": {
                "conversion_rate": segment.conversion_rate,
                "engagement_rate": segment.engagement_rate,
                "revenue_per_customer": segment.revenue_per_customer,
                "lifetime_value": segment.lifetime_value,
                "performance_score": segment.performance_score
            },
            "update_settings": {
                "update_frequency": segment.update_frequency,
                "auto_update": segment.auto_update,
                "last_updated": segment.last_updated.isoformat() if segment.last_updated else None,
                "next_update": segment.next_update.isoformat() if segment.next_update else None
            },
            "overlap_analysis": {
                "overlapping_segments": segment.overlapping_segments,
                "exclusion_rules": segment.exclusion_rules
            },
            "ab_testing": {
                "test_segments": segment.test_segments
            },
            "metadata": {
                "created_by": segment.created_by,
                "created_at": segment.created_at.isoformat(),
                "updated_at": segment.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segment details: {str(e)}")

@router.post("/segments/{segment_id}/execute")
async def execute_segmentation(
    segment_id: str,
    background_tasks: BackgroundTasks,
    execution_type: str = Query("manual", regex="^(manual|scheduled|incremental)$"),
    current_user: dict = Depends(require_permission("execute_segments")),
    db: Session = Depends(get_db)
):
    """Execute segmentation for a specific segment"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        
        # Execute segmentation in background
        background_tasks.add_task(
            _execute_segmentation_background,
            db, segment_id, execution_type
        )
        
        return {
            "success": True,
            "message": f"Segmentation execution started for segment {segment_id}",
            "execution_type": execution_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute segmentation: {str(e)}")

@router.get("/segments/{segment_id}/analytics")
async def get_segment_analytics(
    segment_id: str,
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a segment"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        analytics = segmentation_engine.get_segment_analytics(segment_id)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segment analytics: {str(e)}")

@router.get("/segments/{segment_id}/members")
async def get_segment_members(
    segment_id: str,
    active_only: bool = Query(True),
    include_performance: bool = Query(False),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_segments")),
    db: Session = Depends(get_db)
):
    """Get segment members with details"""
    try:
        from ...segmentation.dynamic_engine import SegmentMembership, DynamicSegment
        from ...core.database import Customer
        
        # Verify segment exists
        segment = db.query(DynamicSegment).filter(DynamicSegment.id == segment_id).first()
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        # Build query
        query = db.query(SegmentMembership, Customer).join(
            Customer, SegmentMembership.customer_id == Customer.customer_id
        ).filter(SegmentMembership.segment_id == segment_id)
        
        if active_only:
            query = query.filter(SegmentMembership.is_active == True)
        
        memberships = query.order_by(SegmentMembership.joined_at.desc()).offset(offset).limit(limit).all()
        
        member_data = []
        for membership, customer in memberships:
            member_info = {
                "customer_id": customer.customer_id,
                "membership": {
                    "joined_at": membership.joined_at.isoformat(),
                    "left_at": membership.left_at.isoformat() if membership.left_at else None,
                    "is_active": membership.is_active,
                    "entry_reason": membership.entry_reason,
                    "confidence_score": membership.confidence_score,
                    "segment_score": membership.segment_score
                },
                "customer_info": {
                    "age": customer.age,
                    "gender": customer.gender,
                    "total_spent": getattr(customer, 'total_spent', 0),
                    "segment_id": customer.segment_id,
                    "rating_id": customer.rating_id
                }
            }
            
            if include_performance:
                member_info["performance"] = {
                    "conversions": membership.conversions,
                    "revenue_generated": membership.revenue_generated,
                    "engagement_events": membership.engagement_events
                }
            
            member_data.append(member_info)
        
        return {
            "segment_id": segment_id,
            "segment_name": segment.name,
            "members": member_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(member_data)
            },
            "summary": {
                "total_active_members": segment.current_size,
                "showing_performance": include_performance
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segment members: {str(e)}")

@router.get("/customers/{customer_id}/segments")
async def get_customer_segments(
    customer_id: str,
    active_only: bool = Query(True),
    current_user: dict = Depends(require_permission("view_segments")),
    db: Session = Depends(get_db)
):
    """Get all segments for a specific customer"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        segments = segmentation_engine.get_customer_segments(customer_id, active_only)
        
        return {
            "customer_id": customer_id,
            "segments": segments,
            "total_segments": len(segments),
            "active_only": active_only
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get customer segments: {str(e)}")

@router.post("/segments/overlap-analysis")
async def analyze_segment_overlap(
    segment_ids: List[str],
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Analyze overlap between multiple segments"""
    try:
        if len(segment_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 segments required for overlap analysis")
        
        segmentation_engine = DynamicSegmentationEngine(db)
        overlap_analysis = segmentation_engine.analyze_segment_overlap(segment_ids)
        
        return overlap_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze segment overlap: {str(e)}")

@router.get("/segments/{segment_id}/executions")
async def get_segment_executions(
    segment_id: str,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_segments")),
    db: Session = Depends(get_db)
):
    """Get execution history for a segment"""
    try:
        from ...segmentation.dynamic_engine import SegmentExecution
        
        executions = db.query(SegmentExecution).filter(
            SegmentExecution.segment_id == segment_id
        ).order_by(SegmentExecution.started_at.desc()).offset(offset).limit(limit).all()
        
        execution_data = []
        for execution in executions:
            execution_data.append({
                "id": execution.id,
                "execution_type": execution.execution_type,
                "trigger": execution.trigger,
                "status": execution.status,
                "metrics": {
                    "customers_processed": execution.customers_processed,
                    "customers_added": execution.customers_added,
                    "customers_removed": execution.customers_removed,
                    "processing_time_seconds": execution.processing_time_seconds,
                    "quality_score": execution.quality_score
                },
                "size_changes": {
                    "before_size": execution.before_size,
                    "after_size": execution.after_size,
                    "net_change": (execution.after_size or 0) - (execution.before_size or 0)
                },
                "results": execution.execution_results,
                "errors": execution.error_messages,
                "warnings": execution.warnings,
                "timestamps": {
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
                }
            })
        
        return {
            "segment_id": segment_id,
            "executions": execution_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(execution_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segment executions: {str(e)}")

@router.put("/segments/{segment_id}/status")
async def update_segment_status(
    segment_id: str,
    status: str,
    current_user: dict = Depends(require_permission("manage_segments")),
    db: Session = Depends(get_db)
):
    """Update segment status"""
    try:
        from ...segmentation.dynamic_engine import DynamicSegment
        
        # Validate status
        if status not in [s.value for s in SegmentStatus]:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        segment = db.query(DynamicSegment).filter(DynamicSegment.id == segment_id).first()
        
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        old_status = segment.status
        segment.status = status
        segment.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Segment status updated from {old_status} to {status}",
            "segment_id": segment_id,
            "old_status": old_status,
            "new_status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update segment status: {str(e)}")

@router.get("/dashboard")
async def get_segmentation_dashboard(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive segmentation dashboard"""
    try:
        from ...segmentation.dynamic_engine import DynamicSegment, SegmentMembership, SegmentExecution
        from collections import defaultdict
        
        # Calculate time range
        time_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365)
        }
        
        end_time = datetime.now()
        start_time = end_time - time_mapping[timeframe]
        
        # Get segments
        segments = db.query(DynamicSegment).all()
        active_segments = [s for s in segments if s.status == SegmentStatus.ACTIVE.value]
        
        # Segment type distribution
        segment_types = defaultdict(int)
        for segment in active_segments:
            segment_types[segment.segment_type] += 1
        
        # Performance metrics
        total_members = sum(s.current_size or 0 for s in active_segments)
        avg_conversion_rate = sum(s.conversion_rate or 0 for s in active_segments) / max(1, len(active_segments))
        avg_engagement_rate = sum(s.engagement_rate or 0 for s in active_segments) / max(1, len(active_segments))
        total_revenue = sum((s.current_size or 0) * (s.revenue_per_customer or 0) for s in active_segments)
        
        # Recent executions
        recent_executions = db.query(SegmentExecution).filter(
            SegmentExecution.started_at >= start_time
        ).all()
        
        successful_executions = [e for e in recent_executions if e.status == "completed"]
        failed_executions = [e for e in recent_executions if e.status == "failed"]
        
        # Execution trends
        daily_executions = defaultdict(int)
        for execution in recent_executions:
            day = execution.started_at.date().isoformat()
            daily_executions[day] += 1
        
        # Top performing segments
        top_segments = sorted(
            active_segments,
            key=lambda s: (s.performance_score or 0),
            reverse=True
        )[:5]
        
        top_segment_data = []
        for segment in top_segments:
            top_segment_data.append({
                "id": segment.id,
                "name": segment.name,
                "type": segment.segment_type,
                "size": segment.current_size,
                "conversion_rate": segment.conversion_rate,
                "revenue_per_customer": segment.revenue_per_customer,
                "performance_score": segment.performance_score
            })
        
        # Segment size distribution
        size_distribution = {
            "small": len([s for s in active_segments if (s.current_size or 0) < 100]),
            "medium": len([s for s in active_segments if 100 <= (s.current_size or 0) < 1000]),
            "large": len([s for s in active_segments if (s.current_size or 0) >= 1000])
        }
        
        # Growth metrics
        new_segments = len([s for s in segments if s.created_at >= start_time])
        
        # Quality metrics
        avg_quality_score = sum(
            e.quality_score for e in successful_executions if e.quality_score
        ) / max(1, len([e for e in successful_executions if e.quality_score]))
        
        return {
            "timeframe": timeframe,
            "analysis_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "overview_metrics": {
                "total_segments": len(segments),
                "active_segments": len(active_segments),
                "total_members": total_members,
                "avg_conversion_rate": avg_conversion_rate,
                "avg_engagement_rate": avg_engagement_rate,
                "total_revenue": total_revenue,
                "new_segments": new_segments
            },
            "segment_distribution": {
                "by_type": dict(segment_types),
                "by_size": size_distribution,
                "by_status": {
                    "active": len([s for s in segments if s.status == SegmentStatus.ACTIVE.value]),
                    "inactive": len([s for s in segments if s.status == SegmentStatus.INACTIVE.value]),
                    "draft": len([s for s in segments if s.status == SegmentStatus.DRAFT.value]),
                    "processing": len([s for s in segments if s.status == SegmentStatus.PROCESSING.value])
                }
            },
            "execution_metrics": {
                "total_executions": len(recent_executions),
                "successful_executions": len(successful_executions),
                "failed_executions": len(failed_executions),
                "success_rate": (len(successful_executions) / max(1, len(recent_executions))) * 100,
                "avg_processing_time": sum(
                    e.processing_time_seconds for e in successful_executions if e.processing_time_seconds
                ) / max(1, len([e for e in successful_executions if e.processing_time_seconds])),
                "avg_quality_score": avg_quality_score
            },
            "performance_trends": {
                "daily_executions": dict(daily_executions),
                "top_performing_segments": top_segment_data
            },
            "insights": _generate_dashboard_insights(
                segments, recent_executions, avg_conversion_rate, avg_quality_score
            ),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get segmentation dashboard: {str(e)}")

@router.get("/segment-types")
async def get_segment_types(
    current_user: dict = Depends(get_current_user)
):
    """Get available segment types and their configurations"""
    return {
        "segment_types": [
            {
                "id": SegmentType.STATIC.value,
                "name": "Static",
                "description": "Fixed criteria that don't change automatically",
                "supports_ml": False,
                "update_frequency": ["manual"],
                "use_cases": ["One-time campaigns", "Fixed customer lists"]
            },
            {
                "id": SegmentType.DYNAMIC.value,
                "name": "Dynamic",
                "description": "Automatically updates based on changing criteria",
                "supports_ml": False,
                "update_frequency": ["real_time", "hourly", "daily", "weekly"],
                "use_cases": ["Behavioral targeting", "Engagement-based segments"]
            },
            {
                "id": SegmentType.PREDICTIVE.value,
                "name": "Predictive",
                "description": "ML-powered segments predicting future behavior",
                "supports_ml": True,
                "update_frequency": ["daily", "weekly", "monthly"],
                "use_cases": ["Churn prediction", "Purchase propensity", "Lifetime value"]
            },
            {
                "id": SegmentType.BEHAVIORAL.value,
                "name": "Behavioral",
                "description": "Based on customer behavior patterns and interactions",
                "supports_ml": True,
                "update_frequency": ["real_time", "hourly", "daily"],
                "use_cases": ["Engagement scoring", "Activity-based targeting"]
            },
            {
                "id": SegmentType.RFM.value,
                "name": "RFM",
                "description": "Recency, Frequency, Monetary value analysis",
                "supports_ml": False,
                "update_frequency": ["daily", "weekly", "monthly"],
                "use_cases": ["Customer value segmentation", "Retention strategies"]
            },
            {
                "id": SegmentType.DEMOGRAPHIC.value,
                "name": "Demographic",
                "description": "Based on customer demographic attributes",
                "supports_ml": False,
                "update_frequency": ["daily", "weekly"],
                "use_cases": ["Age-based targeting", "Geographic segmentation"]
            }
        ],
        "criteria_operators": [
            {
                "id": CriteriaOperator.EQUALS.value,
                "name": "Equals",
                "description": "Exact match",
                "data_types": ["string", "number", "boolean"]
            },
            {
                "id": CriteriaOperator.GREATER_THAN.value,
                "name": "Greater Than",
                "description": "Value is greater than specified",
                "data_types": ["number", "date"]
            },
            {
                "id": CriteriaOperator.LESS_THAN.value,
                "name": "Less Than",
                "description": "Value is less than specified",
                "data_types": ["number", "date"]
            },
            {
                "id": CriteriaOperator.IN.value,
                "name": "In List",
                "description": "Value is in specified list",
                "data_types": ["string", "number"]
            },
            {
                "id": CriteriaOperator.CONTAINS.value,
                "name": "Contains",
                "description": "String contains specified text",
                "data_types": ["string"]
            },
            {
                "id": CriteriaOperator.BETWEEN.value,
                "name": "Between",
                "description": "Value is between two specified values",
                "data_types": ["number", "date"]
            }
        ],
        "update_frequencies": [
            {
                "id": UpdateFrequency.REAL_TIME.value,
                "name": "Real-time",
                "description": "Updates immediately when criteria change"
            },
            {
                "id": UpdateFrequency.HOURLY.value,
                "name": "Hourly",
                "description": "Updates every hour"
            },
            {
                "id": UpdateFrequency.DAILY.value,
                "name": "Daily",
                "description": "Updates once per day"
            },
            {
                "id": UpdateFrequency.WEEKLY.value,
                "name": "Weekly",
                "description": "Updates once per week"
            },
            {
                "id": UpdateFrequency.MONTHLY.value,
                "name": "Monthly",
                "description": "Updates once per month"
            },
            {
                "id": UpdateFrequency.MANUAL.value,
                "name": "Manual",
                "description": "Updates only when manually triggered"
            }
        ]
    }

# Background tasks
async def _create_predictive_segment_background(db: Session, config: Dict[str, Any]):
    """Background task to create predictive segment"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        await segmentation_engine.create_predictive_segment(config)
    except Exception as e:
        logger.error(f"Background predictive segment creation failed: {e}")

async def _execute_segmentation_background(db: Session, segment_id: str, execution_type: str):
    """Background task to execute segmentation"""
    try:
        segmentation_engine = DynamicSegmentationEngine(db)
        await segmentation_engine.execute_segmentation(segment_id, execution_type)
    except Exception as e:
        logger.error(f"Background segmentation execution failed: {e}")

# Helper functions
def _generate_dashboard_insights(segments: List, executions: List, avg_conversion: float, avg_quality: float) -> List[str]:
    """Generate insights for segmentation dashboard"""
    insights = []
    
    try:
        active_segments = [s for s in segments if s.status == "active"]
        
        # Performance insights
        if avg_conversion > 10:
            insights.append("High conversion rates across segments indicate effective targeting")
        elif avg_conversion < 2:
            insights.append("Low conversion rates suggest need for segment refinement")
        
        # Quality insights
        if avg_quality > 80:
            insights.append("High segment quality scores indicate well-defined criteria")
        elif avg_quality < 60:
            insights.append("Consider reviewing segment criteria for better quality")
        
        # Size insights
        small_segments = len([s for s in active_segments if (s.current_size or 0) < 50])
        if small_segments > len(active_segments) * 0.3:
            insights.append("Many segments are small - consider consolidation or broader criteria")
        
        # Execution insights
        recent_failures = len([e for e in executions if e.status == "failed"])
        if recent_failures > len(executions) * 0.1:
            insights.append("High execution failure rate - check segment configurations")
        
        # Growth insights
        if not insights:
            insights.append("Segmentation system is operating within normal parameters")
        
        return insights[:5]  # Limit to top 5 insights
        
    except Exception as e:
        logger.error(f"Error generating dashboard insights: {e}")
        return ["Unable to generate insights at this time"]