"""
Event Tracking & Behavioral Analytics API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict
import logging

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...analytics.behavioral_engine import (
    BehavioralAnalyticsEngine,
    EventType,
    EventPriority,
    AnalyticsTimeframe
)

router = APIRouter()
logger = logging.getLogger(__name__)

class EventIngestionRequest(BaseModel):
    customer_id: str
    event_type: str
    event_name: Optional[str] = None
    event_category: Optional[str] = None
    event_action: Optional[str] = None
    event_label: Optional[str] = None
    event_value: Optional[float] = None
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    properties: Dict[str, Any] = {}
    custom_dimensions: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None

class FunnelAnalysisRequest(BaseModel):
    name: str
    steps: List[str]  # List of event types
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    segment_filters: Dict[str, Any] = {}

class CohortAnalysisRequest(BaseModel):
    name: str
    type: str = "time_based"  # time_based, behavior_based, value_based
    period: str = "monthly"   # weekly, monthly, quarterly
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class AnalyticsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/events/ingest", response_model=AnalyticsResponse)
async def ingest_event(
    request: EventIngestionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest a behavioral event for processing"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        
        # Convert request to event data
        event_data = {
            "customer_id": request.customer_id,
            "event_type": request.event_type,
            "event_name": request.event_name,
            "event_category": request.event_category,
            "event_action": request.event_action,
            "event_label": request.event_label,
            "event_value": request.event_value,
            "session_id": request.session_id,
            "page_url": request.page_url,
            "page_title": request.page_title,
            "referrer": request.referrer,
            "user_agent": request.user_agent,
            "ip_address": request.ip_address,
            "properties": request.properties,
            "custom_dimensions": request.custom_dimensions,
            "timestamp": request.timestamp or datetime.now()
        }
        
        # Ingest event
        result = await analytics_engine.ingest_event(event_data)
        
        # Schedule background processing for batch analytics
        if result.success:
            background_tasks.add_task(
                _process_customer_analytics_background,
                db, request.customer_id
            )
        
        return AnalyticsResponse(
            success=result.success,
            message=result.message,
            data={
                "event_id": result.event_id,
                "processing_time": result.processing_time,
                "validation_errors": result.validation_errors
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event ingestion failed: {str(e)}")

@router.post("/events/batch-ingest")
async def batch_ingest_events(
    events: List[EventIngestionRequest],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest multiple events in batch"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        
        results = []
        customer_ids = set()
        
        for event_request in events:
            event_data = {
                "customer_id": event_request.customer_id,
                "event_type": event_request.event_type,
                "event_name": event_request.event_name,
                "event_category": event_request.event_category,
                "event_action": event_request.event_action,
                "event_label": event_request.event_label,
                "event_value": event_request.event_value,
                "session_id": event_request.session_id,
                "page_url": event_request.page_url,
                "page_title": event_request.page_title,
                "referrer": event_request.referrer,
                "user_agent": event_request.user_agent,
                "ip_address": event_request.ip_address,
                "properties": event_request.properties,
                "custom_dimensions": event_request.custom_dimensions,
                "timestamp": event_request.timestamp or datetime.now()
            }
            
            result = await analytics_engine.ingest_event(event_data)
            results.append({
                "event_id": result.event_id,
                "success": result.success,
                "message": result.message
            })
            
            if result.success:
                customer_ids.add(event_request.customer_id)
        
        # Schedule background processing for affected customers
        for customer_id in customer_ids:
            background_tasks.add_task(
                _process_customer_analytics_background,
                db, customer_id
            )
        
        successful_ingestions = sum(1 for r in results if r["success"])
        
        return {
            "total_events": len(events),
            "successful_ingestions": successful_ingestions,
            "failed_ingestions": len(events) - successful_ingestions,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")

@router.get("/customers/{customer_id}/behavior-profile")
async def get_customer_behavior_profile(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive behavioral profile for a customer"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        profile = analytics_engine.get_customer_behavior_profile(customer_id)
        
        return profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get behavior profile: {str(e)}")

@router.post("/analytics/process")
async def process_behavioral_analytics(
    customer_id: Optional[str] = None,
    batch_size: Optional[int] = Query(1000, le=5000),
    current_user: dict = Depends(require_permission("manage_analytics")),
    db: Session = Depends(get_db)
):
    """Process pending behavioral analytics"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        
        result = await analytics_engine.process_behavioral_analytics(
            customer_id=customer_id,
            batch_size=batch_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics processing failed: {str(e)}")

@router.get("/analytics/real-time")
async def get_real_time_analytics(
    timeframe: AnalyticsTimeframe = Query(AnalyticsTimeframe.HOUR),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get real-time behavioral analytics"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        analytics = analytics_engine.get_real_time_analytics(timeframe)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time analytics failed: {str(e)}")

@router.post("/funnel/create", response_model=AnalyticsResponse)
async def create_funnel_analysis(
    request: FunnelAnalysisRequest,
    current_user: dict = Depends(require_permission("create_analytics")),
    db: Session = Depends(get_db)
):
    """Create and execute funnel analysis"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        
        funnel_config = {
            "name": request.name,
            "steps": request.steps,
            "start_date": request.start_date or datetime.now() - timedelta(days=30),
            "end_date": request.end_date or datetime.now(),
            "segment_filters": request.segment_filters
        }
        
        funnel_id = analytics_engine.create_funnel_analysis(funnel_config)
        
        return AnalyticsResponse(
            success=True,
            message="Funnel analysis created successfully",
            data={"funnel_id": funnel_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Funnel analysis creation failed: {str(e)}")

@router.get("/funnel/{funnel_id}")
async def get_funnel_analysis(
    funnel_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get funnel analysis results"""
    try:
        from ...analytics.behavioral_engine import FunnelAnalysis
        
        funnel = db.query(FunnelAnalysis).filter(
            FunnelAnalysis.id == funnel_id
        ).first()
        
        if not funnel:
            raise HTTPException(status_code=404, detail="Funnel analysis not found")
        
        return {
            "funnel_id": funnel.id,
            "funnel_name": funnel.funnel_name,
            "funnel_steps": funnel.funnel_steps,
            "analysis_period": {
                "start_date": funnel.period_start.isoformat(),
                "end_date": funnel.period_end.isoformat(),
                "analysis_date": funnel.analysis_date.isoformat()
            },
            "metrics": {
                "total_users": funnel.total_users,
                "overall_conversion_rate": funnel.overall_conversion_rate,
                "average_time_to_convert": funnel.average_time_to_convert,
                "bottleneck_step": funnel.bottleneck_step
            },
            "step_analysis": funnel.step_conversions,
            "drop_off_analysis": funnel.drop_off_points,
            "segment_filters": funnel.segment_filters,
            "recommendations": funnel.optimization_recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get funnel analysis: {str(e)}")

@router.post("/cohort/create", response_model=AnalyticsResponse)
async def create_cohort_analysis(
    request: CohortAnalysisRequest,
    current_user: dict = Depends(require_permission("create_analytics")),
    db: Session = Depends(get_db)
):
    """Create and execute cohort analysis"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        
        cohort_config = {
            "name": request.name,
            "type": request.type,
            "period": request.period,
            "start_date": request.start_date or datetime.now() - timedelta(days=365),
            "end_date": request.end_date or datetime.now()
        }
        
        cohort_id = analytics_engine.create_cohort_analysis(cohort_config)
        
        return AnalyticsResponse(
            success=True,
            message="Cohort analysis created successfully",
            data={"cohort_id": cohort_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cohort analysis creation failed: {str(e)}")

@router.get("/cohort/{cohort_id}")
async def get_cohort_analysis(
    cohort_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cohort analysis results"""
    try:
        from ...analytics.behavioral_engine import CohortAnalysis
        
        cohort = db.query(CohortAnalysis).filter(
            CohortAnalysis.id == cohort_id
        ).first()
        
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort analysis not found")
        
        return {
            "cohort_id": cohort.id,
            "cohort_name": cohort.cohort_name,
            "cohort_type": cohort.cohort_type,
            "cohort_period": cohort.cohort_period,
            "analysis_period": {
                "start_date": cohort.period_start.isoformat(),
                "end_date": cohort.period_end.isoformat(),
                "analysis_date": cohort.analysis_date.isoformat()
            },
            "cohort_metrics": {
                "cohort_size": cohort.cohort_size,
                "average_retention_rate": cohort.average_retention_rate,
                "customer_lifetime_value": cohort.customer_lifetime_value
            },
            "retention_analysis": cohort.retention_periods,
            "revenue_analysis": cohort.revenue_data,
            "engagement_analysis": cohort.engagement_data,
            "churn_analysis": cohort.churn_rate_by_period,
            "cohort_characteristics": cohort.cohort_characteristics,
            "insights": cohort.performance_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cohort analysis: {str(e)}")

@router.get("/dashboard/behavioral")
async def get_behavioral_analytics_dashboard(
    timeframe: str = Query("30d", regex="^(1d|7d|30d|90d)$"),
    segment_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive behavioral analytics dashboard"""
    try:
        from ...analytics.behavioral_engine import BehavioralEvent, CustomerSession, CustomerBehaviorProfile
        
        # Calculate time range
        time_mapping = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
        
        end_time = datetime.now()
        start_time = end_time - time_mapping[timeframe]
        
        # Get events in timeframe
        events_query = db.query(BehavioralEvent).filter(
            BehavioralEvent.event_timestamp.between(start_time, end_time)
        )
        
        # Apply segment filter if provided
        if segment_id:
            # Get customers in segment
            from ...core.database import Customer
            segment_customers = db.query(Customer.customer_id).filter(
                Customer.segment_id == segment_id
            ).subquery()
            
            events_query = events_query.filter(
                BehavioralEvent.customer_id.in_(segment_customers)
            )
        
        events = events_query.all()
        
        # Get sessions in timeframe
        sessions_query = db.query(CustomerSession).filter(
            CustomerSession.start_time.between(start_time, end_time)
        )
        
        if segment_id:
            sessions_query = sessions_query.filter(
                CustomerSession.customer_id.in_(segment_customers)
            )
        
        sessions = sessions_query.all()
        
        # Calculate overview metrics
        total_events = len(events)
        unique_customers = len(set(event.customer_id for event in events))
        total_sessions = len(sessions)
        
        # Event metrics
        page_views = len([e for e in events if e.event_type == EventType.PAGE_VIEW])
        conversions = len([e for e in events if e.event_type in [
            EventType.PURCHASE, EventType.SIGNUP, EventType.SUBSCRIPTION
        ]])
        
        # Session metrics
        avg_session_duration = sum(
            session.duration_seconds or 0 for session in sessions
        ) / max(1, len(sessions))
        
        bounce_sessions = sum(1 for session in sessions if session.bounce_rate)
        bounce_rate = (bounce_sessions / max(1, len(sessions))) * 100
        
        # Engagement analysis
        high_engagement_sessions = sum(
            1 for session in sessions if session.engagement_score > 70
        )
        
        # Event type distribution
        from collections import Counter
        event_type_counts = Counter(event.event_type for event in events)
        
        # Device analysis
        device_counts = Counter(event.device_type for event in events if event.device_type)
        
        # Traffic source analysis
        source_counts = Counter(event.utm_source for event in events if event.utm_source)
        
        # Time-based analysis
        daily_events = defaultdict(int)
        daily_customers = defaultdict(set)
        
        for event in events:
            day = event.event_timestamp.date().isoformat()
            daily_events[day] += 1
            daily_customers[day].add(event.customer_id)
        
        # Convert sets to counts
        daily_customer_counts = {day: len(customers) for day, customers in daily_customers.items()}
        
        # Top pages
        page_views_events = [e for e in events if e.event_type == EventType.PAGE_VIEW]
        page_counts = Counter(event.page_url for event in page_views_events if event.page_url)
        
        # Behavioral insights
        insights = []
        
        # Engagement insights
        if total_sessions > 0:
            high_engagement_rate = (high_engagement_sessions / total_sessions) * 100
            if high_engagement_rate > 30:
                insights.append("High engagement rate indicates effective content strategy")
            elif high_engagement_rate < 10:
                insights.append("Low engagement rate suggests need for content optimization")
        
        # Conversion insights
        if unique_customers > 0:
            conversion_rate = (conversions / unique_customers) * 100
            if conversion_rate > 5:
                insights.append("Strong conversion performance across behavioral touchpoints")
            elif conversion_rate < 1:
                insights.append("Low conversion rate indicates optimization opportunities")
        
        # Session quality insights
        if bounce_rate > 70:
            insights.append("High bounce rate suggests landing page optimization needed")
        elif bounce_rate < 30:
            insights.append("Low bounce rate indicates strong content engagement")
        
        return {
            "timeframe": timeframe,
            "analysis_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "segment_filter": segment_id,
            "overview_metrics": {
                "total_events": total_events,
                "unique_customers": unique_customers,
                "total_sessions": total_sessions,
                "page_views": page_views,
                "conversions": conversions,
                "conversion_rate": (conversions / max(1, unique_customers)) * 100,
                "avg_session_duration": avg_session_duration,
                "bounce_rate": bounce_rate,
                "high_engagement_rate": (high_engagement_sessions / max(1, total_sessions)) * 100
            },
            "event_analysis": {
                "event_type_distribution": dict(event_type_counts.most_common(10)),
                "events_per_customer": total_events / max(1, unique_customers),
                "events_per_session": total_events / max(1, total_sessions)
            },
            "audience_analysis": {
                "device_distribution": dict(device_counts.most_common(10)),
                "traffic_sources": dict(source_counts.most_common(10)),
                "customer_segments": _get_behavioral_segments(events, sessions)
            },
            "content_performance": {
                "top_pages": dict(page_counts.most_common(10)),
                "avg_page_views_per_session": page_views / max(1, total_sessions)
            },
            "time_series_data": {
                "daily_events": dict(daily_events),
                "daily_customers": daily_customer_counts,
                "activity_trend": _calculate_trend(list(daily_events.values()))
            },
            "behavioral_insights": insights,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@router.get("/events/types")
async def get_available_event_types(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available event types for tracking"""
    return {
        "event_types": [
            {
                "value": event_type.value,
                "label": event_type.value.replace("_", " ").title(),
                "category": _get_event_category(event_type),
                "description": _get_event_description(event_type)
            }
            for event_type in EventType
        ],
        "priority_levels": [
            {
                "value": priority.value,
                "label": priority.value.title(),
                "description": _get_priority_description(priority)
            }
            for priority in EventPriority
        ],
        "analytics_timeframes": [
            {
                "value": timeframe.value,
                "label": _get_timeframe_label(timeframe)
            }
            for timeframe in AnalyticsTimeframe
        ]
    }

@router.get("/sessions/{customer_id}")
async def get_customer_sessions(
    customer_id: str,
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get customer session history"""
    try:
        from ...analytics.behavioral_engine import CustomerSession
        
        sessions = db.query(CustomerSession).filter(
            CustomerSession.customer_id == customer_id
        ).order_by(CustomerSession.start_time.desc()).offset(offset).limit(limit).all()
        
        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "duration_seconds": session.duration_seconds,
                "page_views": session.page_views,
                "events_count": session.events_count,
                "landing_page": session.landing_page,
                "exit_page": session.exit_page,
                "referrer": session.referrer,
                "engagement_score": session.engagement_score,
                "conversion_events": session.conversion_events,
                "revenue_generated": session.revenue_generated,
                "bounce_rate": session.bounce_rate,
                "session_quality": session.session_quality,
                "session_type": session.session_type,
                "device_info": session.device_info,
                "location_info": session.location_info,
                "campaign_data": session.campaign_data
            })
        
        return {
            "customer_id": customer_id,
            "sessions": session_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_sessions": len(session_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get customer sessions: {str(e)}")

# Background tasks
async def _process_customer_analytics_background(db: Session, customer_id: str):
    """Background task to process customer analytics"""
    try:
        analytics_engine = BehavioralAnalyticsEngine(db)
        await analytics_engine.process_behavioral_analytics(customer_id=customer_id, batch_size=100)
    except Exception as e:
        logger.error(f"Background analytics processing failed for {customer_id}: {e}")

# Helper functions
def _get_behavioral_segments(events: List, sessions: List) -> Dict[str, int]:
    """Analyze behavioral segments from events and sessions"""
    try:
        segments = {
            "high_engagement": 0,
            "medium_engagement": 0,
            "low_engagement": 0,
            "new_visitors": 0,
            "returning_visitors": 0,
            "converters": 0
        }
        
        # Analyze by customer
        customer_metrics = defaultdict(lambda: {
            "events": 0,
            "sessions": 0,
            "conversions": 0,
            "is_new": True
        })
        
        for event in events:
            customer_id = event.customer_id
            customer_metrics[customer_id]["events"] += 1
            
            if event.event_type in [EventType.PURCHASE, EventType.SIGNUP, EventType.SUBSCRIPTION]:
                customer_metrics[customer_id]["conversions"] += 1
        
        for session in sessions:
            customer_id = session.customer_id
            customer_metrics[customer_id]["sessions"] += 1
            
            if session.session_type in ["returning", "loyal"]:
                customer_metrics[customer_id]["is_new"] = False
        
        # Classify customers
        for customer_id, metrics in customer_metrics.items():
            # Engagement classification
            if metrics["events"] > 20 or metrics["sessions"] > 5:
                segments["high_engagement"] += 1
            elif metrics["events"] > 5 or metrics["sessions"] > 2:
                segments["medium_engagement"] += 1
            else:
                segments["low_engagement"] += 1
            
            # Visitor type
            if metrics["is_new"]:
                segments["new_visitors"] += 1
            else:
                segments["returning_visitors"] += 1
            
            # Converters
            if metrics["conversions"] > 0:
                segments["converters"] += 1
        
        return segments
        
    except Exception as e:
        logger.error(f"Error analyzing behavioral segments: {e}")
        return {}

def _calculate_trend(values: List[int]) -> str:
    """Calculate trend direction from time series values"""
    try:
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
            
    except Exception:
        return "unknown"

def _get_event_category(event_type: EventType) -> str:
    """Get category for event type"""
    categories = {
        EventType.PAGE_VIEW: "navigation",
        EventType.CLICK: "interaction",
        EventType.FORM_SUBMIT: "interaction",
        EventType.DOWNLOAD: "conversion",
        EventType.VIDEO_PLAY: "engagement",
        EventType.VIDEO_COMPLETE: "engagement",
        EventType.SEARCH: "interaction",
        EventType.PURCHASE: "conversion",
        EventType.ADD_TO_CART: "commerce",
        EventType.REMOVE_FROM_CART: "commerce",
        EventType.WISHLIST_ADD: "commerce",
        EventType.EMAIL_OPEN: "communication",
        EventType.EMAIL_CLICK: "communication",
        EventType.LOGIN: "authentication",
        EventType.LOGOUT: "authentication",
        EventType.SIGNUP: "conversion",
        EventType.PROFILE_UPDATE: "account",
        EventType.SOCIAL_SHARE: "engagement",
        EventType.REVIEW_SUBMIT: "engagement",
        EventType.SUPPORT_TICKET: "support",
        EventType.PHONE_CALL: "support",
        EventType.STORE_VISIT: "offline",
        EventType.PRODUCT_VIEW: "commerce",
        EventType.CATEGORY_VIEW: "commerce",
        EventType.CHECKOUT_START: "commerce",
        EventType.CHECKOUT_COMPLETE: "conversion",
        EventType.SUBSCRIPTION: "conversion",
        EventType.CANCELLATION: "account",
        EventType.CUSTOM: "custom"
    }
    return categories.get(event_type, "other")

def _get_event_description(event_type: EventType) -> str:
    """Get description for event type"""
    descriptions = {
        EventType.PAGE_VIEW: "User views a page on the website",
        EventType.CLICK: "User clicks on an element",
        EventType.FORM_SUBMIT: "User submits a form",
        EventType.DOWNLOAD: "User downloads a file or resource",
        EventType.VIDEO_PLAY: "User starts playing a video",
        EventType.VIDEO_COMPLETE: "User completes watching a video",
        EventType.SEARCH: "User performs a search",
        EventType.PURCHASE: "User completes a purchase",
        EventType.ADD_TO_CART: "User adds item to shopping cart",
        EventType.REMOVE_FROM_CART: "User removes item from cart",
        EventType.WISHLIST_ADD: "User adds item to wishlist",
        EventType.EMAIL_OPEN: "User opens an email",
        EventType.EMAIL_CLICK: "User clicks link in email",
        EventType.LOGIN: "User logs into account",
        EventType.LOGOUT: "User logs out of account",
        EventType.SIGNUP: "User creates new account",
        EventType.PROFILE_UPDATE: "User updates profile information",
        EventType.SOCIAL_SHARE: "User shares content on social media",
        EventType.REVIEW_SUBMIT: "User submits a product review",
        EventType.SUPPORT_TICKET: "User creates support ticket",
        EventType.PHONE_CALL: "User makes or receives phone call",
        EventType.STORE_VISIT: "User visits physical store",
        EventType.PRODUCT_VIEW: "User views product details",
        EventType.CATEGORY_VIEW: "User browses product category",
        EventType.CHECKOUT_START: "User begins checkout process",
        EventType.CHECKOUT_COMPLETE: "User completes checkout",
        EventType.SUBSCRIPTION: "User subscribes to service",
        EventType.CANCELLATION: "User cancels subscription",
        EventType.CUSTOM: "Custom event defined by organization"
    }
    return descriptions.get(event_type, "Custom event")

def _get_priority_description(priority: EventPriority) -> str:
    """Get description for priority level"""
    descriptions = {
        EventPriority.LOW: "Standard events processed in batch",
        EventPriority.MEDIUM: "Important events with moderate urgency",
        EventPriority.HIGH: "Critical events requiring quick processing",
        EventPriority.CRITICAL: "Urgent events requiring immediate processing"
    }
    return descriptions.get(priority, "Standard priority")

def _get_timeframe_label(timeframe: AnalyticsTimeframe) -> str:
    """Get label for timeframe"""
    labels = {
        AnalyticsTimeframe.HOUR: "Last Hour",
        AnalyticsTimeframe.DAY: "Last 24 Hours",
        AnalyticsTimeframe.WEEK: "Last 7 Days",
        AnalyticsTimeframe.MONTH: "Last 30 Days",
        AnalyticsTimeframe.QUARTER: "Last 90 Days",
        AnalyticsTimeframe.YEAR: "Last 365 Days"
    }
    return labels.get(timeframe, "Custom Timeframe")