"""
Revenue Attribution Engine for Multi-Touch Attribution Analysis
"""
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
import numpy as np
from dataclasses import dataclass
from collections import defaultdict
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class AttributionModel(str, Enum):
    """Attribution model types"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    CUSTOM = "custom"

class TouchpointType(str, Enum):
    """Customer touchpoint types"""
    PAID_SEARCH = "paid_search"
    ORGANIC_SEARCH = "organic_search"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    DIRECT = "direct"
    REFERRAL = "referral"
    DISPLAY_AD = "display_ad"
    AFFILIATE = "affiliate"
    OFFLINE = "offline"
    RETARGETING = "retargeting"

class ConversionType(str, Enum):
    """Types of conversions to track"""
    PURCHASE = "purchase"
    LEAD = "lead"
    SIGNUP = "signup"
    DOWNLOAD = "download"
    SUBSCRIPTION = "subscription"
    TRIAL = "trial"
    DEMO_REQUEST = "demo_request"

# Database Models
class RevenueAttribution(Base):
    """Revenue attribution records"""
    __tablename__ = "revenue_attributions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, index=True)
    conversion_id = Column(String, index=True)
    conversion_type = Column(String, nullable=False)
    conversion_value = Column(Float, nullable=False)
    conversion_date = Column(DateTime, nullable=False, index=True)
    
    # Attribution analysis
    attribution_model = Column(String, nullable=False)
    touchpoints_analyzed = Column(Integer, default=0)
    attribution_window_days = Column(Integer, default=30)
    attribution_data = Column(JSON, default={})  # Detailed attribution breakdown
    
    # Revenue breakdown
    revenue_breakdown = Column(JSON, default={})  # Revenue by touchpoint/campaign
    primary_attribution = Column(JSON, default={})  # Main attributed touchpoint
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    touchpoints = relationship("AttributionTouchpoint", back_populates="attribution")

class AttributionTouchpoint(Base):
    """Individual touchpoints in customer journey"""
    __tablename__ = "attribution_touchpoints"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attribution_id = Column(String, ForeignKey("revenue_attributions.id"), index=True)
    customer_id = Column(String, index=True)
    
    # Touchpoint details
    touchpoint_type = Column(String, nullable=False)
    channel = Column(String)
    campaign_id = Column(String, index=True)
    campaign_name = Column(String)
    source = Column(String)
    medium = Column(String)
    content = Column(String)
    
    # Attribution values
    attributed_revenue = Column(Float, default=0.0)
    attribution_percentage = Column(Float, default=0.0)
    attribution_weight = Column(Float, default=0.0)
    
    # Timing
    touchpoint_timestamp = Column(DateTime, nullable=False, index=True)
    days_before_conversion = Column(Integer)
    position_in_journey = Column(Integer)  # 1st, 2nd, 3rd touchpoint, etc.
    
    # Touchpoint metadata
    touchpoint_data = Column(JSON, default={})
    
    # Relationships
    attribution = relationship("RevenueAttribution", back_populates="touchpoints")
    
    __table_args__ = (
        Index('idx_customer_timestamp', 'customer_id', 'touchpoint_timestamp'),
        Index('idx_campaign_attribution', 'campaign_id', 'attributed_revenue'),
    )

class AttributionModel(Base):
    """Custom attribution model configurations"""
    __tablename__ = "attribution_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    model_type = Column(String, nullable=False)
    description = Column(Text)
    
    # Model configuration
    model_config = Column(JSON, default={})  # Model-specific parameters
    attribution_window_days = Column(Integer, default=30)
    lookback_window_days = Column(Integer, default=90)
    
    # Weights and rules
    touchpoint_weights = Column(JSON, default={})  # Weight by touchpoint type
    position_weights = Column(JSON, default={})    # Weight by position in journey
    time_decay_rate = Column(Float, default=0.5)   # For time-decay models
    
    # Model performance
    accuracy_score = Column(Float)
    last_trained = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

@dataclass
class AttributionResult:
    """Result of attribution analysis"""
    conversion_id: str
    customer_id: str
    total_revenue: float
    attribution_model: str
    touchpoint_attributions: List[Dict[str, Any]]
    model_confidence: float
    journey_summary: Dict[str, Any]

@dataclass
class ChannelPerformance:
    """Channel performance metrics"""
    channel: str
    total_revenue: float
    attributed_conversions: int
    avg_attribution_percentage: float
    first_touch_revenue: float
    last_touch_revenue: float
    assisted_revenue: float

class RevenueAttributionEngine:
    """Comprehensive revenue attribution analysis engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.default_attribution_window = 30  # days
        self.default_lookback_window = 90    # days
        
        # Standard attribution model weights
        self.attribution_models = {
            AttributionModel.FIRST_TOUCH.value: {"first": 1.0},
            AttributionModel.LAST_TOUCH.value: {"last": 1.0},
            AttributionModel.LINEAR.value: {"equal_weight": True},
            AttributionModel.TIME_DECAY.value: {"decay_rate": 0.5},
            AttributionModel.POSITION_BASED.value: {"first": 0.4, "last": 0.4, "middle": 0.2}
        }
    
    def analyze_conversion_attribution(self, customer_id: str, conversion_data: Dict[str, Any],
                                     attribution_model: str = "linear",
                                     attribution_window_days: int = None) -> AttributionResult:
        """Analyze revenue attribution for a conversion"""
        try:
            window_days = attribution_window_days or self.default_attribution_window
            conversion_date = conversion_data.get("conversion_date", datetime.now())
            conversion_value = float(conversion_data.get("value", 0))
            conversion_type = conversion_data.get("type", ConversionType.PURCHASE)
            
            # Get customer touchpoints within attribution window
            touchpoints = self._get_customer_touchpoints(
                customer_id, conversion_date, window_days
            )
            
            if not touchpoints:
                logger.warning(f"No touchpoints found for customer {customer_id} within {window_days} days")
                return self._create_direct_attribution(customer_id, conversion_data)
            
            # Apply attribution model
            attributed_touchpoints = self._apply_attribution_model(
                touchpoints, conversion_value, attribution_model
            )
            
            # Create attribution record
            attribution_id = self._create_attribution_record(
                customer_id, conversion_data, attributed_touchpoints, attribution_model, window_days
            )
            
            # Calculate model confidence
            confidence = self._calculate_attribution_confidence(touchpoints, attribution_model)
            
            # Generate journey summary
            journey_summary = self._generate_journey_summary(touchpoints, conversion_value)
            
            return AttributionResult(
                conversion_id=conversion_data.get("id", str(uuid.uuid4())),
                customer_id=customer_id,
                total_revenue=conversion_value,
                attribution_model=attribution_model,
                touchpoint_attributions=attributed_touchpoints,
                model_confidence=confidence,
                journey_summary=journey_summary
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversion attribution: {e}")
            raise
    
    def get_campaign_attribution_report(self, campaign_id: str, 
                                      start_date: datetime = None,
                                      end_date: datetime = None) -> Dict[str, Any]:
        """Get comprehensive attribution report for a campaign"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Get campaign touchpoints
            campaign_touchpoints = self.db.query(AttributionTouchpoint).filter(
                AttributionTouchpoint.campaign_id == campaign_id,
                AttributionTouchpoint.touchpoint_timestamp.between(start_date, end_date)
            ).all()
            
            if not campaign_touchpoints:
                return {
                    "campaign_id": campaign_id,
                    "error": "No attribution data found for campaign"
                }
            
            # Calculate metrics
            total_attributed_revenue = sum(t.attributed_revenue for t in campaign_touchpoints)
            unique_conversions = len(set(t.attribution_id for t in campaign_touchpoints))
            
            # Attribution model breakdown
            model_breakdown = defaultdict(lambda: {"revenue": 0, "conversions": 0})
            for touchpoint in campaign_touchpoints:
                attribution = self.db.query(RevenueAttribution).filter(
                    RevenueAttribution.id == touchpoint.attribution_id
                ).first()
                if attribution:
                    model_breakdown[attribution.attribution_model]["revenue"] += touchpoint.attributed_revenue
                    model_breakdown[attribution.attribution_model]["conversions"] += 1
            
            # Touchpoint position analysis
            position_analysis = self._analyze_touchpoint_positions(campaign_touchpoints)
            
            # Time-based analysis
            time_analysis = self._analyze_attribution_over_time(campaign_touchpoints, start_date, end_date)
            
            # ROI calculation
            campaign_cost = self._get_campaign_cost(campaign_id, start_date, end_date)
            roi = ((total_attributed_revenue - campaign_cost) / campaign_cost * 100) if campaign_cost > 0 else 0
            
            return {
                "campaign_id": campaign_id,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary_metrics": {
                    "total_attributed_revenue": total_attributed_revenue,
                    "unique_conversions": unique_conversions,
                    "average_conversion_value": total_attributed_revenue / max(1, unique_conversions),
                    "campaign_cost": campaign_cost,
                    "roi_percentage": roi,
                    "revenue_per_touchpoint": total_attributed_revenue / len(campaign_touchpoints)
                },
                "attribution_model_breakdown": dict(model_breakdown),
                "position_analysis": position_analysis,
                "time_series_analysis": time_analysis,
                "touchpoint_details": [
                    {
                        "touchpoint_id": t.id,
                        "customer_id": t.customer_id,
                        "attributed_revenue": t.attributed_revenue,
                        "attribution_percentage": t.attribution_percentage,
                        "position_in_journey": t.position_in_journey,
                        "days_before_conversion": t.days_before_conversion,
                        "touchpoint_type": t.touchpoint_type,
                        "timestamp": t.touchpoint_timestamp.isoformat()
                    } for t in campaign_touchpoints[:100]  # Limit for performance
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating campaign attribution report: {e}")
            raise
    
    def get_channel_performance_analysis(self, start_date: datetime = None,
                                       end_date: datetime = None) -> List[ChannelPerformance]:
        """Analyze performance across all marketing channels"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Get all touchpoints in period
            touchpoints = self.db.query(AttributionTouchpoint).filter(
                AttributionTouchpoint.touchpoint_timestamp.between(start_date, end_date)
            ).all()
            
            # Group by channel
            channel_data = defaultdict(lambda: {
                "total_revenue": 0,
                "conversions": set(),
                "attribution_percentages": [],
                "first_touch_revenue": 0,
                "last_touch_revenue": 0,
                "assisted_revenue": 0,
                "touchpoint_count": 0
            })
            
            for touchpoint in touchpoints:
                channel = touchpoint.channel or touchpoint.touchpoint_type
                data = channel_data[channel]
                
                data["total_revenue"] += touchpoint.attributed_revenue
                data["conversions"].add(touchpoint.attribution_id)
                data["attribution_percentages"].append(touchpoint.attribution_percentage)
                data["touchpoint_count"] += 1
                
                # Position-based analysis
                if touchpoint.position_in_journey == 1:
                    data["first_touch_revenue"] += touchpoint.attributed_revenue
                elif touchpoint.position_in_journey == self._get_journey_length(touchpoint.attribution_id):
                    data["last_touch_revenue"] += touchpoint.attributed_revenue
                else:
                    data["assisted_revenue"] += touchpoint.attributed_revenue
            
            # Convert to ChannelPerformance objects
            channel_performances = []
            for channel, data in channel_data.items():
                avg_attribution = (
                    sum(data["attribution_percentages"]) / len(data["attribution_percentages"])
                    if data["attribution_percentages"] else 0
                )
                
                channel_performances.append(ChannelPerformance(
                    channel=channel,
                    total_revenue=data["total_revenue"],
                    attributed_conversions=len(data["conversions"]),
                    avg_attribution_percentage=avg_attribution,
                    first_touch_revenue=data["first_touch_revenue"],
                    last_touch_revenue=data["last_touch_revenue"],
                    assisted_revenue=data["assisted_revenue"]
                ))
            
            # Sort by total revenue
            return sorted(channel_performances, key=lambda x: x.total_revenue, reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing channel performance: {e}")
            raise
    
    def create_custom_attribution_model(self, model_config: Dict[str, Any]) -> str:
        """Create a custom attribution model"""
        try:
            model = AttributionModel(
                name=model_config["name"],
                model_type=model_config.get("type", AttributionModel.CUSTOM),
                description=model_config.get("description", ""),
                model_config=model_config.get("config", {}),
                attribution_window_days=model_config.get("attribution_window_days", 30),
                lookback_window_days=model_config.get("lookback_window_days", 90),
                touchpoint_weights=model_config.get("touchpoint_weights", {}),
                position_weights=model_config.get("position_weights", {}),
                time_decay_rate=model_config.get("time_decay_rate", 0.5)
            )
            
            self.db.add(model)
            self.db.commit()
            
            logger.info(f"Created custom attribution model: {model.name}")
            return model.id
            
        except Exception as e:
            logger.error(f"Error creating custom attribution model: {e}")
            self.db.rollback()
            raise
    
    def get_attribution_insights(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive attribution insights and recommendations"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=timeframe_days)
            
            # Get attribution data
            attributions = self.db.query(RevenueAttribution).filter(
                RevenueAttribution.conversion_date.between(start_date, end_date)
            ).all()
            
            if not attributions:
                return {"error": "No attribution data found for the specified timeframe"}
            
            # Model comparison
            model_performance = self._compare_attribution_models(attributions)
            
            # Journey analysis
            journey_insights = self._analyze_customer_journeys(attributions)
            
            # Revenue insights
            revenue_insights = self._analyze_revenue_patterns(attributions)
            
            # Optimization recommendations
            recommendations = self._generate_attribution_recommendations(
                model_performance, journey_insights, revenue_insights
            )
            
            return {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_analyzed": timeframe_days
                },
                "summary": {
                    "total_conversions": len(attributions),
                    "total_attributed_revenue": sum(a.conversion_value for a in attributions),
                    "average_conversion_value": sum(a.conversion_value for a in attributions) / len(attributions),
                    "unique_customers": len(set(a.customer_id for a in attributions))
                },
                "model_performance": model_performance,
                "journey_insights": journey_insights,
                "revenue_insights": revenue_insights,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting attribution insights: {e}")
            raise
    
    # Helper methods
    def _get_customer_touchpoints(self, customer_id: str, conversion_date: datetime,
                                 window_days: int) -> List[Dict[str, Any]]:
        """Get customer touchpoints within attribution window"""
        try:
            # This would integrate with the Customer Data Platform to get touchpoint data
            # For now, we'll simulate touchpoint data structure
            window_start = conversion_date - timedelta(days=window_days)
            
            # In a real implementation, this would query the CDP events
            # Here we'll create a mock structure that matches expected touchpoint format
            touchpoints = []
            
            # Query customer events from CDP (simulated)
            from cdp.unified_profile import CustomerEvent
            events = self.db.query(CustomerEvent).filter(
                CustomerEvent.profile_id == customer_id,
                CustomerEvent.timestamp.between(window_start, conversion_date)
            ).order_by(CustomerEvent.timestamp).all()
            
            for i, event in enumerate(events, 1):
                if event.event_type in ["page_view", "email_click", "ad_click", "social_click"]:
                    touchpoint_type = self._map_event_to_touchpoint_type(event.event_type, event.event_data)
                    
                    touchpoints.append({
                        "id": event.id,
                        "type": touchpoint_type,
                        "timestamp": event.timestamp,
                        "channel": event.event_data.get("channel", "unknown"),
                        "campaign_id": event.event_data.get("campaign_id"),
                        "campaign_name": event.event_data.get("campaign_name"),
                        "source": event.event_data.get("source"),
                        "medium": event.event_data.get("medium"),
                        "position": i,
                        "days_before_conversion": (conversion_date - event.timestamp).days,
                        "data": event.event_data
                    })
            
            return touchpoints
            
        except Exception as e:
            logger.error(f"Error getting customer touchpoints: {e}")
            return []
    
    def _apply_attribution_model(self, touchpoints: List[Dict[str, Any]], 
                               conversion_value: float, model_type: str) -> List[Dict[str, Any]]:
        """Apply attribution model to distribute conversion value"""
        try:
            if not touchpoints:
                return []
            
            attributed_touchpoints = []
            
            if model_type == AttributionModel.FIRST_TOUCH:
                # 100% to first touchpoint
                for i, touchpoint in enumerate(touchpoints):
                    attribution_percentage = 100.0 if i == 0 else 0.0
                    attributed_revenue = conversion_value if i == 0 else 0.0
                    
                    attributed_touchpoints.append({
                        **touchpoint,
                        "attributed_revenue": attributed_revenue,
                        "attribution_percentage": attribution_percentage,
                        "attribution_weight": 1.0 if i == 0 else 0.0
                    })
            
            elif model_type == AttributionModel.LAST_TOUCH:
                # 100% to last touchpoint
                for i, touchpoint in enumerate(touchpoints):
                    attribution_percentage = 100.0 if i == len(touchpoints) - 1 else 0.0
                    attributed_revenue = conversion_value if i == len(touchpoints) - 1 else 0.0
                    
                    attributed_touchpoints.append({
                        **touchpoint,
                        "attributed_revenue": attributed_revenue,
                        "attribution_percentage": attribution_percentage,
                        "attribution_weight": 1.0 if i == len(touchpoints) - 1 else 0.0
                    })
            
            elif model_type == "linear":
                # Equal distribution across all touchpoints
                weight_per_touchpoint = 1.0 / len(touchpoints)
                revenue_per_touchpoint = conversion_value / len(touchpoints)
                attribution_percentage = 100.0 / len(touchpoints)
                
                for touchpoint in touchpoints:
                    attributed_touchpoints.append({
                        **touchpoint,
                        "attributed_revenue": revenue_per_touchpoint,
                        "attribution_percentage": attribution_percentage,
                        "attribution_weight": weight_per_touchpoint
                    })
            
            elif model_type == AttributionModel.TIME_DECAY:
                # More weight to touchpoints closer to conversion
                weights = []
                decay_rate = 0.5
                
                for touchpoint in touchpoints:
                    days_before = touchpoint["days_before_conversion"]
                    weight = decay_rate ** days_before
                    weights.append(weight)
                
                total_weight = sum(weights)
                
                for i, touchpoint in enumerate(touchpoints):
                    weight = weights[i] / total_weight
                    attributed_revenue = conversion_value * weight
                    attribution_percentage = weight * 100
                    
                    attributed_touchpoints.append({
                        **touchpoint,
                        "attributed_revenue": attributed_revenue,
                        "attribution_percentage": attribution_percentage,
                        "attribution_weight": weight
                    })
            
            elif model_type == AttributionModel.POSITION_BASED:
                # 40% first, 40% last, 20% middle (distributed equally)
                for i, touchpoint in enumerate(touchpoints):
                    if len(touchpoints) == 1:
                        weight = 1.0
                    elif i == 0:  # First touchpoint
                        weight = 0.4
                    elif i == len(touchpoints) - 1:  # Last touchpoint
                        weight = 0.4
                    else:  # Middle touchpoints
                        middle_count = len(touchpoints) - 2
                        weight = 0.2 / middle_count if middle_count > 0 else 0
                    
                    attributed_revenue = conversion_value * weight
                    attribution_percentage = weight * 100
                    
                    attributed_touchpoints.append({
                        **touchpoint,
                        "attributed_revenue": attributed_revenue,
                        "attribution_percentage": attribution_percentage,
                        "attribution_weight": weight
                    })
            
            else:
                # Default to linear for unknown models
                return self._apply_attribution_model(touchpoints, conversion_value, "linear")
            
            return attributed_touchpoints
            
        except Exception as e:
            logger.error(f"Error applying attribution model: {e}")
            raise
    
    def _create_attribution_record(self, customer_id: str, conversion_data: Dict[str, Any],
                                 attributed_touchpoints: List[Dict[str, Any]], 
                                 attribution_model: str, window_days: int) -> str:
        """Create attribution record in database"""
        try:
            # Create main attribution record
            attribution = RevenueAttribution(
                customer_id=customer_id,
                conversion_id=conversion_data.get("id", str(uuid.uuid4())),
                conversion_type=conversion_data.get("type", ConversionType.PURCHASE),
                conversion_value=float(conversion_data.get("value", 0)),
                conversion_date=conversion_data.get("conversion_date", datetime.now()),
                attribution_model=attribution_model,
                touchpoints_analyzed=len(attributed_touchpoints),
                attribution_window_days=window_days,
                attribution_data={
                    "total_touchpoints": len(attributed_touchpoints),
                    "model_applied": attribution_model,
                    "conversion_metadata": conversion_data
                },
                revenue_breakdown={
                    tp["type"]: tp["attributed_revenue"] 
                    for tp in attributed_touchpoints
                },
                primary_attribution={
                    "touchpoint_id": max(attributed_touchpoints, key=lambda x: x["attributed_revenue"])["id"],
                    "attribution_percentage": max(tp["attribution_percentage"] for tp in attributed_touchpoints)
                } if attributed_touchpoints else {}
            )
            
            self.db.add(attribution)
            self.db.flush()  # Get the ID
            
            # Create touchpoint records
            for touchpoint in attributed_touchpoints:
                attribution_touchpoint = AttributionTouchpoint(
                    attribution_id=attribution.id,
                    customer_id=customer_id,
                    touchpoint_type=touchpoint["type"],
                    channel=touchpoint.get("channel"),
                    campaign_id=touchpoint.get("campaign_id"),
                    campaign_name=touchpoint.get("campaign_name"),
                    source=touchpoint.get("source"),
                    medium=touchpoint.get("medium"),
                    attributed_revenue=touchpoint["attributed_revenue"],
                    attribution_percentage=touchpoint["attribution_percentage"],
                    attribution_weight=touchpoint["attribution_weight"],
                    touchpoint_timestamp=touchpoint["timestamp"],
                    days_before_conversion=touchpoint["days_before_conversion"],
                    position_in_journey=touchpoint["position"],
                    touchpoint_data=touchpoint.get("data", {})
                )
                self.db.add(attribution_touchpoint)
            
            self.db.commit()
            return attribution.id
            
        except Exception as e:
            logger.error(f"Error creating attribution record: {e}")
            self.db.rollback()
            raise
    
    def _create_direct_attribution(self, customer_id: str, conversion_data: Dict[str, Any]) -> AttributionResult:
        """Create direct attribution when no touchpoints found"""
        return AttributionResult(
            conversion_id=conversion_data.get("id", str(uuid.uuid4())),
            customer_id=customer_id,
            total_revenue=float(conversion_data.get("value", 0)),
            attribution_model="direct",
            touchpoint_attributions=[{
                "type": TouchpointType.DIRECT,
                "attributed_revenue": float(conversion_data.get("value", 0)),
                "attribution_percentage": 100.0,
                "attribution_weight": 1.0
            }],
            model_confidence=1.0,
            journey_summary={
                "touchpoint_count": 0,
                "journey_length_days": 0,
                "conversion_type": "direct"
            }
        )
    
    def _map_event_to_touchpoint_type(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Map customer event to touchpoint type"""
        mapping = {
            "page_view": TouchpointType.ORGANIC_SEARCH,
            "email_click": TouchpointType.EMAIL,
            "ad_click": TouchpointType.PAID_SEARCH,
            "social_click": TouchpointType.SOCIAL_MEDIA
        }
        
        # Check event data for more specific mapping
        if event_data.get("source") == "google":
            return TouchpointType.PAID_SEARCH if event_data.get("medium") == "cpc" else TouchpointType.ORGANIC_SEARCH
        elif event_data.get("source") in ["facebook", "twitter", "instagram"]:
            return TouchpointType.SOCIAL_MEDIA
        
        return mapping.get(event_type, TouchpointType.DIRECT)
    
    def _calculate_attribution_confidence(self, touchpoints: List[Dict[str, Any]], 
                                        model_type: str) -> float:
        """Calculate confidence score for attribution model"""
        try:
            if not touchpoints:
                return 0.0
            
            # Base confidence factors
            touchpoint_count = len(touchpoints)
            journey_length = max(tp["days_before_conversion"] for tp in touchpoints) if touchpoints else 0
            
            # Confidence decreases with very short or very long journeys
            if touchpoint_count == 1:
                confidence = 0.9  # High confidence for single touchpoint
            elif touchpoint_count <= 3:
                confidence = 0.8
            elif touchpoint_count <= 7:
                confidence = 0.7
            else:
                confidence = 0.6  # Lower confidence for complex journeys
            
            # Adjust for journey length
            if journey_length > 60:  # Very long journey
                confidence *= 0.8
            elif journey_length < 1:  # Same-day conversion
                confidence *= 0.9
            
            # Model-specific adjustments
            if model_type == AttributionModel.DATA_DRIVEN:
                confidence += 0.1  # Higher confidence for data-driven models
            elif model_type in [AttributionModel.FIRST_TOUCH, AttributionModel.LAST_TOUCH]:
                confidence *= 0.85  # Lower confidence for single-touch models
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating attribution confidence: {e}")
            return 0.5
    
    def _generate_journey_summary(self, touchpoints: List[Dict[str, Any]], 
                                conversion_value: float) -> Dict[str, Any]:
        """Generate summary of customer journey"""
        try:
            if not touchpoints:
                return {"touchpoint_count": 0}
            
            journey_length_days = max(tp["days_before_conversion"] for tp in touchpoints)
            unique_channels = len(set(tp.get("channel", "unknown") for tp in touchpoints))
            unique_campaigns = len(set(tp.get("campaign_id") for tp in touchpoints if tp.get("campaign_id")))
            
            # Channel sequence
            channel_sequence = [tp.get("channel", tp["type"]) for tp in touchpoints]
            
            # Time between touchpoints
            if len(touchpoints) > 1:
                time_gaps = []
                for i in range(1, len(touchpoints)):
                    gap = touchpoints[i]["days_before_conversion"] - touchpoints[i-1]["days_before_conversion"]
                    time_gaps.append(abs(gap))
                avg_time_between_touchpoints = sum(time_gaps) / len(time_gaps)
            else:
                avg_time_between_touchpoints = 0
            
            return {
                "touchpoint_count": len(touchpoints),
                "journey_length_days": journey_length_days,
                "unique_channels": unique_channels,
                "unique_campaigns": unique_campaigns,
                "channel_sequence": channel_sequence,
                "avg_time_between_touchpoints": avg_time_between_touchpoints,
                "conversion_value": conversion_value,
                "journey_complexity": "simple" if len(touchpoints) <= 2 else "moderate" if len(touchpoints) <= 5 else "complex"
            }
            
        except Exception as e:
            logger.error(f"Error generating journey summary: {e}")
            return {"error": str(e)}
    
    def _compare_attribution_models(self, attributions: List[RevenueAttribution]) -> Dict[str, Any]:
        """Compare performance of different attribution models"""
        try:
            model_stats = defaultdict(lambda: {
                "conversions": 0,
                "total_revenue": 0,
                "avg_revenue": 0,
                "touchpoints_analyzed": 0
            })
            
            for attribution in attributions:
                model = attribution.attribution_model
                model_stats[model]["conversions"] += 1
                model_stats[model]["total_revenue"] += attribution.conversion_value
                model_stats[model]["touchpoints_analyzed"] += attribution.touchpoints_analyzed
            
            # Calculate averages
            for model, stats in model_stats.items():
                stats["avg_revenue"] = stats["total_revenue"] / max(1, stats["conversions"])
                stats["avg_touchpoints"] = stats["touchpoints_analyzed"] / max(1, stats["conversions"])
            
            return dict(model_stats)
            
        except Exception as e:
            logger.error(f"Error comparing attribution models: {e}")
            return {}
    
    def _analyze_customer_journeys(self, attributions: List[RevenueAttribution]) -> Dict[str, Any]:
        """Analyze customer journey patterns"""
        try:
            journey_lengths = []
            touchpoint_counts = []
            
            for attribution in attributions:
                touchpoints = self.db.query(AttributionTouchpoint).filter(
                    AttributionTouchpoint.attribution_id == attribution.id
                ).all()
                
                if touchpoints:
                    journey_length = max(tp.days_before_conversion for tp in touchpoints)
                    journey_lengths.append(journey_length)
                    touchpoint_counts.append(len(touchpoints))
            
            return {
                "avg_journey_length_days": sum(journey_lengths) / len(journey_lengths) if journey_lengths else 0,
                "avg_touchpoints_per_journey": sum(touchpoint_counts) / len(touchpoint_counts) if touchpoint_counts else 0,
                "journey_length_distribution": {
                    "same_day": len([l for l in journey_lengths if l == 0]),
                    "1-7_days": len([l for l in journey_lengths if 1 <= l <= 7]),
                    "8-30_days": len([l for l in journey_lengths if 8 <= l <= 30]),
                    "31+_days": len([l for l in journey_lengths if l > 30])
                },
                "touchpoint_distribution": {
                    "single_touch": len([c for c in touchpoint_counts if c == 1]),
                    "2-3_touches": len([c for c in touchpoint_counts if 2 <= c <= 3]),
                    "4-7_touches": len([c for c in touchpoint_counts if 4 <= c <= 7]),
                    "8+_touches": len([c for c in touchpoint_counts if c >= 8])
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing customer journeys: {e}")
            return {}
    
    def _analyze_revenue_patterns(self, attributions: List[RevenueAttribution]) -> Dict[str, Any]:
        """Analyze revenue attribution patterns"""
        try:
            conversion_values = [a.conversion_value for a in attributions]
            
            return {
                "total_revenue": sum(conversion_values),
                "avg_conversion_value": sum(conversion_values) / len(conversion_values),
                "median_conversion_value": np.median(conversion_values),
                "revenue_distribution": {
                    "0-100": len([v for v in conversion_values if v <= 100]),
                    "101-500": len([v for v in conversion_values if 101 <= v <= 500]),
                    "501-1000": len([v for v in conversion_values if 501 <= v <= 1000]),
                    "1000+": len([v for v in conversion_values if v > 1000])
                },
                "high_value_conversions": len([v for v in conversion_values if v > np.percentile(conversion_values, 90)]),
                "conversion_value_variance": np.var(conversion_values)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing revenue patterns: {e}")
            return {}
    
    def _generate_attribution_recommendations(self, model_performance: Dict[str, Any],
                                            journey_insights: Dict[str, Any],
                                            revenue_insights: Dict[str, Any]) -> List[str]:
        """Generate actionable attribution recommendations"""
        recommendations = []
        
        try:
            # Model recommendations
            if model_performance:
                best_model = max(model_performance.items(), key=lambda x: x[1]["avg_revenue"])
                recommendations.append(f"Consider using {best_model[0]} model for highest revenue attribution accuracy")
            
            # Journey recommendations
            if journey_insights.get("avg_touchpoints_per_journey", 0) > 5:
                recommendations.append("High touchpoint count suggests need for multi-touch attribution models")
            elif journey_insights.get("avg_touchpoints_per_journey", 0) <= 2:
                recommendations.append("Simple customer journeys - single-touch models may be sufficient")
            
            # Revenue recommendations
            if revenue_insights.get("conversion_value_variance", 0) > 100000:
                recommendations.append("High revenue variance - consider segmented attribution analysis")
            
            # General recommendations
            avg_journey_length = journey_insights.get("avg_journey_length_days", 0)
            if avg_journey_length > 30:
                recommendations.append("Long customer journeys - consider extending attribution window")
            elif avg_journey_length < 3:
                recommendations.append("Short customer journeys - focus on immediate conversion drivers")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to analysis error"]
    
    def _analyze_touchpoint_positions(self, touchpoints: List[AttributionTouchpoint]) -> Dict[str, Any]:
        """Analyze touchpoint position effectiveness"""
        try:
            position_data = defaultdict(lambda: {"revenue": 0, "count": 0})
            
            for tp in touchpoints:
                position = tp.position_in_journey
                position_data[position]["revenue"] += tp.attributed_revenue
                position_data[position]["count"] += 1
            
            # Calculate effectiveness by position
            position_analysis = {}
            for position, data in position_data.items():
                position_analysis[f"position_{position}"] = {
                    "total_revenue": data["revenue"],
                    "touchpoint_count": data["count"],
                    "avg_revenue_per_touchpoint": data["revenue"] / max(1, data["count"])
                }
            
            return position_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing touchpoint positions: {e}")
            return {}
    
    def _analyze_attribution_over_time(self, touchpoints: List[AttributionTouchpoint],
                                     start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze attribution patterns over time"""
        try:
            daily_data = defaultdict(lambda: {"revenue": 0, "count": 0})
            
            for tp in touchpoints:
                day = tp.touchpoint_timestamp.date().isoformat()
                daily_data[day]["revenue"] += tp.attributed_revenue
                daily_data[day]["count"] += 1
            
            # Calculate trends
            sorted_days = sorted(daily_data.keys())
            if len(sorted_days) >= 2:
                first_half_revenue = sum(daily_data[day]["revenue"] for day in sorted_days[:len(sorted_days)//2])
                second_half_revenue = sum(daily_data[day]["revenue"] for day in sorted_days[len(sorted_days)//2:])
                
                trend = "increasing" if second_half_revenue > first_half_revenue else "decreasing"
            else:
                trend = "insufficient_data"
            
            return {
                "daily_attribution": dict(daily_data),
                "trend": trend,
                "peak_day": max(daily_data.items(), key=lambda x: x[1]["revenue"])[0] if daily_data else None,
                "total_days_active": len(daily_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing attribution over time: {e}")
            return {}
    
    def _get_campaign_cost(self, campaign_id: str, start_date: datetime, end_date: datetime) -> float:
        """Get campaign cost for ROI calculation"""
        try:
            # This would integrate with campaign management system
            # For now, return a simulated cost
            from core.database import Campaign
            campaign = self.db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
            
            if campaign and hasattr(campaign, 'budget'):
                return float(campaign.budget or 0)
            
            return 0.0  # Default if no cost data available
            
        except Exception as e:
            logger.error(f"Error getting campaign cost: {e}")
            return 0.0
    
    def _get_journey_length(self, attribution_id: str) -> int:
        """Get total length of customer journey"""
        try:
            touchpoints = self.db.query(AttributionTouchpoint).filter(
                AttributionTouchpoint.attribution_id == attribution_id
            ).all()
            
            return len(touchpoints)
            
        except Exception as e:
            logger.error(f"Error getting journey length: {e}")
            return 1