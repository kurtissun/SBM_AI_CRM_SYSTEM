"""
Event Tracking & Behavioral Analytics Engine
"""
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
import numpy as np
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Standard event types for behavioral tracking"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    FORM_SUBMIT = "form_submit"
    DOWNLOAD = "download"
    VIDEO_PLAY = "video_play"
    VIDEO_COMPLETE = "video_complete"
    SEARCH = "search"
    PURCHASE = "purchase"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    WISHLIST_ADD = "wishlist_add"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"
    PROFILE_UPDATE = "profile_update"
    SOCIAL_SHARE = "social_share"
    REVIEW_SUBMIT = "review_submit"
    SUPPORT_TICKET = "support_ticket"
    PHONE_CALL = "phone_call"
    STORE_VISIT = "store_visit"
    PRODUCT_VIEW = "product_view"
    CATEGORY_VIEW = "category_view"
    CHECKOUT_START = "checkout_start"
    CHECKOUT_COMPLETE = "checkout_complete"
    SUBSCRIPTION = "subscription"
    CANCELLATION = "cancellation"
    CUSTOM = "custom"

class EventPriority(str, Enum):
    """Event processing priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnalyticsTimeframe(str, Enum):
    """Timeframe options for analytics"""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"
    YEAR = "365d"

# Database Models
class BehavioralEvent(Base):
    """Individual customer behavioral events"""
    __tablename__ = "behavioral_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True)
    
    # Event details
    event_type = Column(String, index=True, nullable=False)
    event_name = Column(String, index=True)
    event_category = Column(String, index=True)
    event_action = Column(String)
    event_label = Column(String)
    event_value = Column(Float)
    
    # Context
    page_url = Column(String)
    page_title = Column(String)
    referrer = Column(String)
    user_agent = Column(String)
    ip_address = Column(String)
    
    # Device and location
    device_type = Column(String)
    device_brand = Column(String)
    operating_system = Column(String)
    browser = Column(String)
    location_data = Column(JSON)
    
    # Campaign attribution
    utm_source = Column(String, index=True)
    utm_medium = Column(String, index=True)
    utm_campaign = Column(String, index=True)
    utm_content = Column(String)
    utm_term = Column(String)
    
    # Event metadata
    event_properties = Column(JSON, default={})
    custom_dimensions = Column(JSON, default={})
    
    # Processing
    priority = Column(String, default=EventPriority.MEDIUM.value)
    processed = Column(Boolean, default=False, index=True)
    processing_errors = Column(JSON, default=[])
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False, index=True)
    server_timestamp = Column(DateTime, default=datetime.now)
    processed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_customer_event_time', 'customer_id', 'event_timestamp'),
        Index('idx_session_time', 'session_id', 'event_timestamp'),
        Index('idx_event_type_time', 'event_type', 'event_timestamp'),
        Index('idx_unprocessed', 'processed', 'priority'),
    )

class CustomerSession(Base):
    """Customer session tracking"""
    __tablename__ = "customer_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True, nullable=False)
    
    # Session details
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, index=True)
    duration_seconds = Column(Integer)
    page_views = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    
    # Entry and exit
    landing_page = Column(String)
    exit_page = Column(String)
    referrer = Column(String)
    
    # Engagement metrics
    bounce_rate = Column(Boolean, default=False)
    engagement_score = Column(Float, default=0.0)
    conversion_events = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    
    # Technical details
    device_info = Column(JSON, default={})
    location_info = Column(JSON, default={})
    campaign_data = Column(JSON, default={})
    
    # Session analytics
    session_quality = Column(String)  # high, medium, low
    session_type = Column(String)     # new, returning, loyal
    
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    events = relationship("BehavioralEvent", backref="session", 
                         primaryjoin="CustomerSession.session_id == foreign(BehavioralEvent.session_id)")

class CustomerBehaviorProfile(Base):
    """Aggregated customer behavior profile"""
    __tablename__ = "customer_behavior_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, unique=True, index=True, nullable=False)
    
    # Engagement metrics
    total_events = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    total_page_views = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    
    # Behavioral patterns
    most_active_hour = Column(Integer)
    most_active_day = Column(String)
    preferred_device = Column(String)
    preferred_channel = Column(String)
    
    # Engagement scoring
    engagement_score = Column(Float, default=0.0)
    recency_score = Column(Float, default=0.0)
    frequency_score = Column(Float, default=0.0)
    monetary_score = Column(Float, default=0.0)
    
    # Behavioral segments
    behavior_segments = Column(JSON, default=[])
    customer_lifecycle_stage = Column(String)
    churn_risk_score = Column(Float, default=0.0)
    
    # Preferences and interests
    content_preferences = Column(JSON, default={})
    product_affinities = Column(JSON, default={})
    interaction_preferences = Column(JSON, default={})
    
    # Analytics metadata
    profile_completeness = Column(Float, default=0.0)
    data_quality_score = Column(Float, default=0.0)
    last_analysis_date = Column(DateTime)
    
    # Timestamps
    first_seen = Column(DateTime)
    last_seen = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class FunnelAnalysis(Base):
    """Funnel conversion analysis"""
    __tablename__ = "funnel_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    funnel_name = Column(String, nullable=False, index=True)
    funnel_steps = Column(JSON, nullable=False)  # Ordered list of event types
    
    # Analysis period
    analysis_date = Column(DateTime, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Funnel metrics
    total_users = Column(Integer, default=0)
    step_conversions = Column(JSON, default={})  # {step_index: {users: n, conversion_rate: %}}
    drop_off_points = Column(JSON, default={})
    average_time_to_convert = Column(Float, default=0.0)
    
    # Segmentation
    segment_id = Column(String, index=True)
    segment_filters = Column(JSON, default={})
    
    # Results
    overall_conversion_rate = Column(Float, default=0.0)
    bottleneck_step = Column(Integer)
    optimization_recommendations = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.now)

class CohortAnalysis(Base):
    """Customer cohort analysis"""
    __tablename__ = "cohort_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cohort_name = Column(String, nullable=False, index=True)
    cohort_type = Column(String, nullable=False)  # time_based, behavior_based, value_based
    
    # Cohort definition
    cohort_period = Column(String)  # weekly, monthly, quarterly
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    # Cohort data
    cohort_size = Column(Integer, default=0)
    retention_periods = Column(JSON, default={})  # {period: retention_rate}
    revenue_data = Column(JSON, default={})
    engagement_data = Column(JSON, default={})
    
    # Analysis metrics
    average_retention_rate = Column(Float, default=0.0)
    customer_lifetime_value = Column(Float, default=0.0)
    churn_rate_by_period = Column(JSON, default={})
    
    # Insights
    cohort_characteristics = Column(JSON, default={})
    performance_insights = Column(JSON, default=[])
    
    analysis_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

@dataclass
class EventIngestionResult:
    """Result of event ingestion"""
    success: bool
    event_id: str
    message: str
    processing_time: float
    validation_errors: List[str] = None

@dataclass
class BehaviorInsight:
    """Behavioral analysis insight"""
    insight_type: str
    title: str
    description: str
    confidence: float
    impact: str
    recommendations: List[str]
    supporting_data: Dict[str, Any]

class BehavioralAnalyticsEngine:
    """Comprehensive behavioral analytics and event tracking engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.processing_batch_size = 1000
        self.real_time_threshold_seconds = 30
        
        # Analytics configuration
        self.engagement_weights = {
            'recency': 0.3,
            'frequency': 0.3,
            'monetary': 0.2,
            'diversity': 0.2
        }
        
        # Event processing rules
        self.high_priority_events = {
            EventType.PURCHASE, EventType.SIGNUP, EventType.CANCELLATION,
            EventType.SUPPORT_TICKET, EventType.CHECKOUT_COMPLETE
        }
        
        self.conversion_events = {
            EventType.PURCHASE, EventType.SIGNUP, EventType.SUBSCRIPTION,
            EventType.CHECKOUT_COMPLETE, EventType.DOWNLOAD
        }
    
    async def ingest_event(self, event_data: Dict[str, Any]) -> EventIngestionResult:
        """Ingest and process a single behavioral event"""
        start_time = datetime.now()
        
        try:
            # Validate event data
            validation_errors = self._validate_event_data(event_data)
            if validation_errors:
                return EventIngestionResult(
                    success=False,
                    event_id="",
                    message="Event validation failed",
                    processing_time=0.0,
                    validation_errors=validation_errors
                )
            
            # Enrich event data
            enriched_data = await self._enrich_event_data(event_data)
            
            # Determine priority
            priority = self._determine_event_priority(enriched_data)
            
            # Create event record
            event = BehavioralEvent(
                customer_id=enriched_data["customer_id"],
                session_id=enriched_data.get("session_id"),
                event_type=enriched_data["event_type"],
                event_name=enriched_data.get("event_name"),
                event_category=enriched_data.get("event_category"),
                event_action=enriched_data.get("event_action"),
                event_label=enriched_data.get("event_label"),
                event_value=enriched_data.get("event_value"),
                page_url=enriched_data.get("page_url"),
                page_title=enriched_data.get("page_title"),
                referrer=enriched_data.get("referrer"),
                user_agent=enriched_data.get("user_agent"),
                ip_address=enriched_data.get("ip_address"),
                device_type=enriched_data.get("device_type"),
                device_brand=enriched_data.get("device_brand"),
                operating_system=enriched_data.get("operating_system"),
                browser=enriched_data.get("browser"),
                location_data=enriched_data.get("location_data", {}),
                utm_source=enriched_data.get("utm_source"),
                utm_medium=enriched_data.get("utm_medium"),
                utm_campaign=enriched_data.get("utm_campaign"),
                utm_content=enriched_data.get("utm_content"),
                utm_term=enriched_data.get("utm_term"),
                event_properties=enriched_data.get("properties", {}),
                custom_dimensions=enriched_data.get("custom_dimensions", {}),
                priority=priority,
                event_timestamp=enriched_data.get("timestamp", datetime.now())
            )
            
            self.db.add(event)
            self.db.flush()  # Get the ID
            
            # Update session if exists
            await self._update_session(enriched_data)
            
            # Real-time processing for high-priority events
            if priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
                await self._process_real_time_event(event)
            
            self.db.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EventIngestionResult(
                success=True,
                event_id=event.id,
                message="Event ingested successfully",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error ingesting event: {e}")
            self.db.rollback()
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return EventIngestionResult(
                success=False,
                event_id="",
                message=f"Event ingestion failed: {str(e)}",
                processing_time=processing_time
            )
    
    async def process_behavioral_analytics(self, customer_id: str = None,
                                         batch_size: int = None) -> Dict[str, Any]:
        """Process behavioral analytics for customers"""
        try:
            batch_size = batch_size or self.processing_batch_size
            
            # Get unprocessed events
            query = self.db.query(BehavioralEvent).filter(
                BehavioralEvent.processed == False
            )
            
            if customer_id:
                query = query.filter(BehavioralEvent.customer_id == customer_id)
            
            unprocessed_events = query.limit(batch_size).all()
            
            if not unprocessed_events:
                return {"message": "No events to process", "processed_count": 0}
            
            processed_count = 0
            error_count = 0
            
            # Group events by customer for batch processing
            customer_events = defaultdict(list)
            for event in unprocessed_events:
                customer_events[event.customer_id].append(event)
            
            # Process each customer's events
            for customer_id, events in customer_events.items():
                try:
                    await self._process_customer_events(customer_id, events)
                    
                    # Mark events as processed
                    for event in events:
                        event.processed = True
                        event.processed_at = datetime.now()
                    
                    processed_count += len(events)
                    
                except Exception as e:
                    logger.error(f"Error processing events for customer {customer_id}: {e}")
                    
                    # Mark events with errors
                    for event in events:
                        event.processing_errors.append({
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    error_count += len(events)
            
            self.db.commit()
            
            return {
                "processed_count": processed_count,
                "error_count": error_count,
                "customers_processed": len(customer_events),
                "processing_complete": len(unprocessed_events) < batch_size
            }
            
        except Exception as e:
            logger.error(f"Error in behavioral analytics processing: {e}")
            self.db.rollback()
            raise
    
    def get_customer_behavior_profile(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive behavioral profile for a customer"""
        try:
            # Get or create behavior profile
            profile = self.db.query(CustomerBehaviorProfile).filter(
                CustomerBehaviorProfile.customer_id == customer_id
            ).first()
            
            if not profile:
                # Create new profile
                profile = self._create_behavior_profile(customer_id)
            
            # Get recent events for real-time insights
            recent_events = self.db.query(BehavioralEvent).filter(
                BehavioralEvent.customer_id == customer_id,
                BehavioralEvent.event_timestamp >= datetime.now() - timedelta(days=30)
            ).order_by(BehavioralEvent.event_timestamp.desc()).limit(100).all()
            
            # Get recent sessions
            recent_sessions = self.db.query(CustomerSession).filter(
                CustomerSession.customer_id == customer_id,
                CustomerSession.start_time >= datetime.now() - timedelta(days=30)
            ).order_by(CustomerSession.start_time.desc()).limit(20).all()
            
            # Calculate real-time metrics
            real_time_metrics = self._calculate_real_time_metrics(recent_events, recent_sessions)
            
            # Generate behavioral insights
            insights = self._generate_behavioral_insights(profile, recent_events, recent_sessions)
            
            return {
                "customer_id": customer_id,
                "behavior_profile": {
                    "engagement_score": profile.engagement_score,
                    "recency_score": profile.recency_score,
                    "frequency_score": profile.frequency_score,
                    "monetary_score": profile.monetary_score,
                    "churn_risk_score": profile.churn_risk_score,
                    "lifecycle_stage": profile.customer_lifecycle_stage,
                    "behavior_segments": profile.behavior_segments,
                    "profile_completeness": profile.profile_completeness,
                    "data_quality_score": profile.data_quality_score
                },
                "activity_summary": {
                    "total_events": profile.total_events,
                    "total_sessions": profile.total_sessions,
                    "total_page_views": profile.total_page_views,
                    "avg_session_duration": profile.avg_session_duration,
                    "bounce_rate": profile.bounce_rate,
                    "first_seen": profile.first_seen.isoformat() if profile.first_seen else None,
                    "last_seen": profile.last_seen.isoformat() if profile.last_seen else None
                },
                "preferences": {
                    "most_active_hour": profile.most_active_hour,
                    "most_active_day": profile.most_active_day,
                    "preferred_device": profile.preferred_device,
                    "preferred_channel": profile.preferred_channel,
                    "content_preferences": profile.content_preferences,
                    "product_affinities": profile.product_affinities,
                    "interaction_preferences": profile.interaction_preferences
                },
                "real_time_metrics": real_time_metrics,
                "behavioral_insights": [asdict(insight) for insight in insights],
                "recent_activity": [
                    {
                        "event_type": event.event_type,
                        "event_name": event.event_name,
                        "timestamp": event.event_timestamp.isoformat(),
                        "page_url": event.page_url,
                        "device_type": event.device_type,
                        "utm_source": event.utm_source
                    } for event in recent_events[:10]
                ],
                "last_updated": profile.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting customer behavior profile: {e}")
            raise
    
    def create_funnel_analysis(self, funnel_config: Dict[str, Any]) -> str:
        """Create and execute funnel analysis"""
        try:
            funnel_name = funnel_config["name"]
            funnel_steps = funnel_config["steps"]  # List of event types
            period_start = funnel_config.get("start_date", datetime.now() - timedelta(days=30))
            period_end = funnel_config.get("end_date", datetime.now())
            segment_filters = funnel_config.get("segment_filters", {})
            
            # Execute funnel analysis
            funnel_results = self._execute_funnel_analysis(
                funnel_steps, period_start, period_end, segment_filters
            )
            
            # Create funnel analysis record
            funnel_analysis = FunnelAnalysis(
                funnel_name=funnel_name,
                funnel_steps=funnel_steps,
                analysis_date=datetime.now(),
                period_start=period_start,
                period_end=period_end,
                total_users=funnel_results["total_users"],
                step_conversions=funnel_results["step_conversions"],
                drop_off_points=funnel_results["drop_off_points"],
                average_time_to_convert=funnel_results["avg_time_to_convert"],
                segment_filters=segment_filters,
                overall_conversion_rate=funnel_results["overall_conversion_rate"],
                bottleneck_step=funnel_results["bottleneck_step"],
                optimization_recommendations=funnel_results["recommendations"]
            )
            
            self.db.add(funnel_analysis)
            self.db.commit()
            
            logger.info(f"Created funnel analysis: {funnel_name}")
            return funnel_analysis.id
            
        except Exception as e:
            logger.error(f"Error creating funnel analysis: {e}")
            self.db.rollback()
            raise
    
    def create_cohort_analysis(self, cohort_config: Dict[str, Any]) -> str:
        """Create and execute cohort analysis"""
        try:
            cohort_name = cohort_config["name"]
            cohort_type = cohort_config.get("type", "time_based")
            cohort_period = cohort_config.get("period", "monthly")
            period_start = cohort_config.get("start_date", datetime.now() - timedelta(days=365))
            period_end = cohort_config.get("end_date", datetime.now())
            
            # Execute cohort analysis
            cohort_results = self._execute_cohort_analysis(
                cohort_type, cohort_period, period_start, period_end
            )
            
            # Create cohort analysis record
            cohort_analysis = CohortAnalysis(
                cohort_name=cohort_name,
                cohort_type=cohort_type,
                cohort_period=cohort_period,
                period_start=period_start,
                period_end=period_end,
                cohort_size=cohort_results["cohort_size"],
                retention_periods=cohort_results["retention_data"],
                revenue_data=cohort_results["revenue_data"],
                engagement_data=cohort_results["engagement_data"],
                average_retention_rate=cohort_results["avg_retention_rate"],
                customer_lifetime_value=cohort_results["customer_ltv"],
                churn_rate_by_period=cohort_results["churn_rates"],
                cohort_characteristics=cohort_results["characteristics"],
                performance_insights=cohort_results["insights"]
            )
            
            self.db.add(cohort_analysis)
            self.db.commit()
            
            logger.info(f"Created cohort analysis: {cohort_name}")
            return cohort_analysis.id
            
        except Exception as e:
            logger.error(f"Error creating cohort analysis: {e}")
            self.db.rollback()
            raise
    
    def get_real_time_analytics(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.HOUR) -> Dict[str, Any]:
        """Get real-time behavioral analytics"""
        try:
            # Calculate time range
            timeframe_mapping = {
                AnalyticsTimeframe.HOUR: timedelta(hours=1),
                AnalyticsTimeframe.DAY: timedelta(days=1),
                AnalyticsTimeframe.WEEK: timedelta(days=7),
                AnalyticsTimeframe.MONTH: timedelta(days=30),
                AnalyticsTimeframe.QUARTER: timedelta(days=90),
                AnalyticsTimeframe.YEAR: timedelta(days=365)
            }
            
            end_time = datetime.now()
            start_time = end_time - timeframe_mapping[timeframe]
            
            # Get events in timeframe
            events = self.db.query(BehavioralEvent).filter(
                BehavioralEvent.event_timestamp.between(start_time, end_time)
            ).all()
            
            # Get sessions in timeframe
            sessions = self.db.query(CustomerSession).filter(
                CustomerSession.start_time.between(start_time, end_time)
            ).all()
            
            # Calculate metrics
            total_events = len(events)
            unique_customers = len(set(event.customer_id for event in events))
            total_sessions = len(sessions)
            
            # Event type distribution
            event_type_counts = Counter(event.event_type for event in events)
            
            # Device distribution
            device_counts = Counter(event.device_type for event in events if event.device_type)
            
            # Traffic sources
            source_counts = Counter(event.utm_source for event in events if event.utm_source)
            
            # Page performance
            page_views = [event for event in events if event.event_type == EventType.PAGE_VIEW]
            page_counts = Counter(event.page_url for event in page_views if event.page_url)
            
            # Conversion events
            conversions = [event for event in events if event.event_type in self.conversion_events]
            conversion_rate = (len(conversions) / max(1, unique_customers)) * 100
            
            # Session quality
            avg_session_duration = sum(
                session.duration_seconds or 0 for session in sessions
            ) / max(1, len(sessions))
            
            bounce_rate = sum(
                1 for session in sessions if session.bounce_rate
            ) / max(1, len(sessions)) * 100
            
            # Real-time insights
            insights = self._generate_real_time_insights(
                events, sessions, timeframe
            )
            
            return {
                "timeframe": timeframe,
                "analysis_period": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat()
                },
                "overview_metrics": {
                    "total_events": total_events,
                    "unique_customers": unique_customers,
                    "total_sessions": total_sessions,
                    "conversion_rate": conversion_rate,
                    "avg_session_duration": avg_session_duration,
                    "bounce_rate": bounce_rate,
                    "events_per_customer": total_events / max(1, unique_customers),
                    "sessions_per_customer": total_sessions / max(1, unique_customers)
                },
                "event_distribution": dict(event_type_counts.most_common(10)),
                "device_distribution": dict(device_counts.most_common(10)),
                "traffic_sources": dict(source_counts.most_common(10)),
                "top_pages": dict(page_counts.most_common(10)),
                "conversion_summary": {
                    "total_conversions": len(conversions),
                    "conversion_rate": conversion_rate,
                    "conversion_types": dict(Counter(
                        conv.event_type for conv in conversions
                    ))
                },
                "real_time_insights": insights,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time analytics: {e}")
            raise
    
    # Helper methods
    def _validate_event_data(self, event_data: Dict[str, Any]) -> List[str]:
        """Validate incoming event data"""
        errors = []
        
        required_fields = ["customer_id", "event_type"]
        for field in required_fields:
            if field not in event_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate event type
        if event_data.get("event_type") not in [e.value for e in EventType]:
            errors.append(f"Invalid event type: {event_data.get('event_type')}")
        
        # Validate customer_id format
        customer_id = event_data.get("customer_id")
        if customer_id and not isinstance(customer_id, str):
            errors.append("customer_id must be a string")
        
        return errors
    
    async def _enrich_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event data with additional context"""
        enriched = event_data.copy()
        
        # Generate session ID if not provided
        if "session_id" not in enriched:
            enriched["session_id"] = f"session_{uuid.uuid4()}"
        
        # Parse user agent if provided
        if "user_agent" in enriched:
            device_info = self._parse_user_agent(enriched["user_agent"])
            enriched.update(device_info)
        
        # Geolocate IP address
        if "ip_address" in enriched:
            location_data = await self._geolocate_ip(enriched["ip_address"])
            enriched["location_data"] = location_data
        
        # Extract UTM parameters from URL
        if "page_url" in enriched:
            utm_params = self._extract_utm_parameters(enriched["page_url"])
            enriched.update(utm_params)
        
        return enriched
    
    def _determine_event_priority(self, event_data: Dict[str, Any]) -> str:
        """Determine processing priority for event"""
        event_type = event_data.get("event_type")
        
        if event_type in [EventType.PURCHASE, EventType.CANCELLATION, EventType.SUPPORT_TICKET]:
            return EventPriority.CRITICAL.value
        elif event_type in self.high_priority_events:
            return EventPriority.HIGH.value
        elif event_type in self.conversion_events:
            return EventPriority.MEDIUM.value
        else:
            return EventPriority.LOW.value
    
    async def _update_session(self, event_data: Dict[str, Any]):
        """Update or create customer session"""
        try:
            session_id = event_data.get("session_id")
            customer_id = event_data["customer_id"]
            
            if not session_id:
                return
            
            # Get or create session
            session = self.db.query(CustomerSession).filter(
                CustomerSession.session_id == session_id
            ).first()
            
            if not session:
                session = CustomerSession(
                    session_id=session_id,
                    customer_id=customer_id,
                    start_time=event_data.get("timestamp", datetime.now()),
                    landing_page=event_data.get("page_url"),
                    referrer=event_data.get("referrer"),
                    device_info={
                        "device_type": event_data.get("device_type"),
                        "browser": event_data.get("browser"),
                        "operating_system": event_data.get("operating_system")
                    },
                    location_info=event_data.get("location_data", {}),
                    campaign_data={
                        "utm_source": event_data.get("utm_source"),
                        "utm_medium": event_data.get("utm_medium"),
                        "utm_campaign": event_data.get("utm_campaign")
                    }
                )
                self.db.add(session)
            
            # Update session metrics
            session.events_count += 1
            session.end_time = event_data.get("timestamp", datetime.now())
            
            if session.start_time and session.end_time:
                session.duration_seconds = int(
                    (session.end_time - session.start_time).total_seconds()
                )
            
            if event_data.get("event_type") == EventType.PAGE_VIEW:
                session.page_views += 1
                session.exit_page = event_data.get("page_url")
            
            if event_data.get("event_type") in self.conversion_events:
                session.conversion_events += 1
                session.revenue_generated += event_data.get("event_value", 0)
            
            # Calculate bounce rate (single page session)
            session.bounce_rate = (session.page_views <= 1 and session.duration_seconds < 30)
            
            # Calculate engagement score
            session.engagement_score = self._calculate_session_engagement_score(session)
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
    
    async def _process_real_time_event(self, event: BehavioralEvent):
        """Process high-priority events in real-time"""
        try:
            # Update customer behavior profile immediately
            await self._update_behavior_profile_real_time(event)
            
            # Trigger automation workflows if applicable
            await self._trigger_behavioral_automations(event)
            
            # Send real-time notifications
            await self._send_real_time_notifications(event)
            
        except Exception as e:
            logger.error(f"Error in real-time event processing: {e}")
    
    async def _process_customer_events(self, customer_id: str, events: List[BehavioralEvent]):
        """Process batch of events for a customer"""
        try:
            # Update or create behavior profile
            profile = self.db.query(CustomerBehaviorProfile).filter(
                CustomerBehaviorProfile.customer_id == customer_id
            ).first()
            
            if not profile:
                profile = self._create_behavior_profile(customer_id)
            
            # Process events to update profile
            self._update_profile_from_events(profile, events)
            
            # Calculate new scores
            self._recalculate_behavior_scores(profile, events)
            
            # Update timestamps
            profile.last_analysis_date = datetime.now()
            profile.updated_at = datetime.now()
            
            if events:
                profile.last_seen = max(event.event_timestamp for event in events)
                if not profile.first_seen:
                    profile.first_seen = min(event.event_timestamp for event in events)
            
        except Exception as e:
            logger.error(f"Error processing customer events for {customer_id}: {e}")
            raise
    
    def _create_behavior_profile(self, customer_id: str) -> CustomerBehaviorProfile:
        """Create new customer behavior profile"""
        profile = CustomerBehaviorProfile(
            customer_id=customer_id,
            customer_lifecycle_stage="new",
            created_at=datetime.now()
        )
        
        self.db.add(profile)
        self.db.flush()  # Get the ID
        
        return profile
    
    def _calculate_real_time_metrics(self, events: List[BehavioralEvent], 
                                   sessions: List[CustomerSession]) -> Dict[str, Any]:
        """Calculate real-time behavioral metrics"""
        try:
            if not events:
                return {"message": "No recent activity"}
            
            # Recent activity patterns
            event_timestamps = [event.event_timestamp for event in events]
            last_activity = max(event_timestamps) if event_timestamps else None
            
            # Engagement indicators
            page_views = len([e for e in events if e.event_type == EventType.PAGE_VIEW])
            interactions = len([e for e in events if e.event_type in [
                EventType.CLICK, EventType.FORM_SUBMIT, EventType.DOWNLOAD
            ]])
            
            # Session quality
            if sessions:
                avg_session_duration = sum(s.duration_seconds or 0 for s in sessions) / len(sessions)
                bounce_sessions = sum(1 for s in sessions if s.bounce_rate)
                bounce_rate = (bounce_sessions / len(sessions)) * 100
            else:
                avg_session_duration = 0
                bounce_rate = 0
            
            # Device and channel diversity
            unique_devices = len(set(e.device_type for e in events if e.device_type))
            unique_sources = len(set(e.utm_source for e in events if e.utm_source))
            
            return {
                "last_activity": last_activity.isoformat() if last_activity else None,
                "activity_intensity": len(events),
                "page_views": page_views,
                "interactions": interactions,
                "engagement_ratio": (interactions / max(1, page_views)) * 100,
                "avg_session_duration": avg_session_duration,
                "bounce_rate": bounce_rate,
                "channel_diversity": unique_sources,
                "device_diversity": unique_devices,
                "activity_trend": self._calculate_activity_trend(events)
            }
            
        except Exception as e:
            logger.error(f"Error calculating real-time metrics: {e}")
            return {"error": str(e)}
    
    def _generate_behavioral_insights(self, profile: CustomerBehaviorProfile,
                                    events: List[BehavioralEvent],
                                    sessions: List[CustomerSession]) -> List[BehaviorInsight]:
        """Generate actionable behavioral insights"""
        insights = []
        
        try:
            # Engagement insights
            if profile.engagement_score > 80:
                insights.append(BehaviorInsight(
                    insight_type="engagement",
                    title="High Engagement Customer",
                    description="This customer shows consistently high engagement across all touchpoints",
                    confidence=0.9,
                    impact="high",
                    recommendations=[
                        "Offer premium products or services",
                        "Invite to loyalty program",
                        "Request reviews or testimonials"
                    ],
                    supporting_data={"engagement_score": profile.engagement_score}
                ))
            elif profile.engagement_score < 30:
                insights.append(BehaviorInsight(
                    insight_type="engagement",
                    title="Low Engagement Risk",
                    description="Customer engagement has declined significantly",
                    confidence=0.8,
                    impact="high",
                    recommendations=[
                        "Launch re-engagement campaign",
                        "Offer personalized incentives",
                        "Review communication preferences"
                    ],
                    supporting_data={"engagement_score": profile.engagement_score}
                ))
            
            # Churn risk insights
            if profile.churn_risk_score > 70:
                insights.append(BehaviorInsight(
                    insight_type="churn_risk",
                    title="High Churn Risk",
                    description="Customer shows patterns indicating high likelihood of churn",
                    confidence=0.85,
                    impact="critical",
                    recommendations=[
                        "Immediate personal outreach",
                        "Offer retention incentive",
                        "Schedule satisfaction survey"
                    ],
                    supporting_data={"churn_risk_score": profile.churn_risk_score}
                ))
            
            # Behavioral pattern insights
            if events:
                recent_event_types = [e.event_type for e in events[-10:]]
                if recent_event_types.count(EventType.PRODUCT_VIEW) > 5:
                    insights.append(BehaviorInsight(
                        insight_type="behavior_pattern",
                        title="High Browse Intent",
                        description="Customer is actively browsing products",
                        confidence=0.75,
                        impact="medium",
                        recommendations=[
                            "Send targeted product recommendations",
                            "Offer limited-time discount",
                            "Provide comparison tools"
                        ],
                        supporting_data={"product_views": recent_event_types.count(EventType.PRODUCT_VIEW)}
                    ))
            
            # Session quality insights
            if sessions and len(sessions) >= 3:
                avg_duration = sum(s.duration_seconds or 0 for s in sessions) / len(sessions)
                if avg_duration > 300:  # More than 5 minutes
                    insights.append(BehaviorInsight(
                        insight_type="session_quality",
                        title="High Session Quality",
                        description="Customer spends significant time per session",
                        confidence=0.8,
                        impact="medium",
                        recommendations=[
                            "Provide in-depth content",
                            "Offer expert consultation",
                            "Share advanced features"
                        ],
                        supporting_data={"avg_session_duration": avg_duration}
                    ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating behavioral insights: {e}")
            return []
    
    # Additional helper methods would continue here...
    # (Due to length constraints, including key methods only)
    
    def _calculate_session_engagement_score(self, session: CustomerSession) -> float:
        """Calculate engagement score for a session"""
        try:
            score = 0.0
            
            # Duration score (0-40 points)
            if session.duration_seconds:
                duration_score = min(40, (session.duration_seconds / 300) * 40)  # Max at 5 minutes
                score += duration_score
            
            # Page views score (0-30 points)
            page_view_score = min(30, session.page_views * 5)
            score += page_view_score
            
            # Events score (0-20 points)
            event_score = min(20, session.events_count * 2)
            score += event_score
            
            # Conversion bonus (0-10 points)
            if session.conversion_events > 0:
                score += 10
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"Error calculating session engagement score: {e}")
            return 0.0
    
    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Parse user agent string for device information"""
        # Simplified user agent parsing - in production, use a proper library
        device_info = {
            "device_type": "desktop",
            "browser": "unknown",
            "operating_system": "unknown"
        }
        
        user_agent_lower = user_agent.lower()
        
        # Device type detection
        if any(mobile in user_agent_lower for mobile in ["mobile", "android", "iphone"]):
            device_info["device_type"] = "mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            device_info["device_type"] = "tablet"
        
        # Browser detection
        if "chrome" in user_agent_lower:
            device_info["browser"] = "chrome"
        elif "firefox" in user_agent_lower:
            device_info["browser"] = "firefox"
        elif "safari" in user_agent_lower:
            device_info["browser"] = "safari"
        elif "edge" in user_agent_lower:
            device_info["browser"] = "edge"
        
        # OS detection
        if "windows" in user_agent_lower:
            device_info["operating_system"] = "windows"
        elif "macintosh" in user_agent_lower or "mac os" in user_agent_lower:
            device_info["operating_system"] = "macos"
        elif "linux" in user_agent_lower:
            device_info["operating_system"] = "linux"
        elif "android" in user_agent_lower:
            device_info["operating_system"] = "android"
        elif "ios" in user_agent_lower or "iphone" in user_agent_lower:
            device_info["operating_system"] = "ios"
        
        return device_info
    
    async def _geolocate_ip(self, ip_address: str) -> Dict[str, Any]:
        """Geolocate IP address (simplified implementation)"""
        # In production, integrate with a geolocation service
        return {
            "country": "Unknown",
            "region": "Unknown", 
            "city": "Unknown",
            "latitude": None,
            "longitude": None
        }
    
    def _extract_utm_parameters(self, url: str) -> Dict[str, str]:
        """Extract UTM parameters from URL"""
        from urllib.parse import urlparse, parse_qs
        
        utm_params = {}
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            utm_fields = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]
            for field in utm_fields:
                if field in query_params:
                    utm_params[field] = query_params[field][0]
            
        except Exception as e:
            logger.error(f"Error extracting UTM parameters: {e}")
        
        return utm_params
    
    def _calculate_activity_trend(self, events: List[BehavioralEvent]) -> str:
        """Calculate activity trend from recent events"""
        try:
            if len(events) < 2:
                return "insufficient_data"
            
            # Split events into two halves by time
            sorted_events = sorted(events, key=lambda e: e.event_timestamp)
            mid_point = len(sorted_events) // 2
            
            first_half = sorted_events[:mid_point]
            second_half = sorted_events[mid_point:]
            
            first_half_rate = len(first_half) / max(1, len(first_half))
            second_half_rate = len(second_half) / max(1, len(second_half))
            
            if second_half_rate > first_half_rate * 1.2:
                return "increasing"
            elif second_half_rate < first_half_rate * 0.8:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating activity trend: {e}")
            return "unknown"