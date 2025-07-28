"""
Customer Journey Mapping and Lifecycle Management System
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from collections import defaultdict

from core.database import Base, get_db
from ai_engine.generative_analytics import generative_analytics

logger = logging.getLogger(__name__)

class LifecycleStage(str, Enum):
    """Customer lifecycle stages"""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    DORMANT = "dormant"
    REACTIVATION = "reactivation"

class TouchpointType(str, Enum):
    """Types of customer touchpoints"""
    WEBSITE_VISIT = "website_visit"
    STORE_VISIT = "store_visit"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    SMS_CLICK = "sms_click"
    APP_OPEN = "app_open"
    PURCHASE = "purchase"
    CUSTOMER_SERVICE = "customer_service"
    SOCIAL_MEDIA = "social_media"
    CAMPAIGN_RESPONSE = "campaign_response"
    LOYALTY_ACTION = "loyalty_action"
    REVIEW = "review"
    REFERRAL = "referral"

# Database Models
class CustomerJourney(Base):
    """Customer journey tracking"""
    __tablename__ = "customer_journeys"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    current_stage = Column(String, default=LifecycleStage.AWARENESS)
    stage_entered_at = Column(DateTime, default=datetime.now)
    journey_score = Column(Float, default=0.0)
    health_score = Column(Float, default=50.0)
    risk_score = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    last_touchpoint = Column(DateTime)
    total_touchpoints = Column(Integer, default=0)
    journey_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    touchpoints = relationship("Touchpoint", back_populates="journey")
    stage_history = relationship("StageTransition", back_populates="journey")

class Touchpoint(Base):
    """Individual customer touchpoints"""
    __tablename__ = "touchpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("customer_journeys.id"), index=True)
    customer_id = Column(String, index=True)
    touchpoint_type = Column(String)
    channel = Column(String)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    duration_seconds = Column(Integer)
    engagement_score = Column(Float, default=0.0)
    conversion_value = Column(Float, default=0.0)
    metadata = Column(JSON, default={})
    campaign_id = Column(String)
    device_type = Column(String)
    location = Column(String)
    
    # Relationships
    journey = relationship("CustomerJourney", back_populates="touchpoints")

class StageTransition(Base):
    """Track stage transitions"""
    __tablename__ = "stage_transitions"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("customer_journeys.id"), index=True)
    customer_id = Column(String, index=True)
    from_stage = Column(String)
    to_stage = Column(String)
    transition_date = Column(DateTime, default=datetime.now)
    trigger_event = Column(String)
    transition_score = Column(Float)
    
    # Relationships
    journey = relationship("CustomerJourney", back_populates="stage_history")

class CustomerLifecycleManager:
    """Manages customer journey and lifecycle tracking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stage_weights = {
            LifecycleStage.AWARENESS: 1.0,
            LifecycleStage.CONSIDERATION: 2.0,
            LifecycleStage.PURCHASE: 3.0,
            LifecycleStage.RETENTION: 4.0,
            LifecycleStage.ADVOCACY: 5.0,
            LifecycleStage.DORMANT: 0.5,
            LifecycleStage.REACTIVATION: 1.5
        }
        
        self.touchpoint_scores = {
            TouchpointType.WEBSITE_VISIT: 1.0,
            TouchpointType.STORE_VISIT: 3.0,
            TouchpointType.EMAIL_OPEN: 0.5,
            TouchpointType.EMAIL_CLICK: 2.0,
            TouchpointType.APP_OPEN: 1.5,
            TouchpointType.PURCHASE: 10.0,
            TouchpointType.CUSTOMER_SERVICE: 2.0,
            TouchpointType.SOCIAL_MEDIA: 1.5,
            TouchpointType.REVIEW: 5.0,
            TouchpointType.REFERRAL: 8.0
        }
    
    def track_touchpoint(self, customer_id: str, touchpoint_type: TouchpointType, 
                        metadata: Dict[str, Any] = None) -> Touchpoint:
        """Track a customer touchpoint"""
        try:
            # Get or create journey
            journey = self.db.query(CustomerJourney).filter(
                CustomerJourney.customer_id == customer_id
            ).first()
            
            if not journey:
                journey = CustomerJourney(
                    customer_id=customer_id,
                    current_stage=LifecycleStage.AWARENESS,
                    journey_metadata={"source": metadata.get("source", "organic")}
                )
                self.db.add(journey)
                self.db.commit()
            
            # Create touchpoint
            touchpoint = Touchpoint(
                journey_id=journey.id,
                customer_id=customer_id,
                touchpoint_type=touchpoint_type.value,
                channel=metadata.get("channel", "unknown"),
                engagement_score=self.touchpoint_scores.get(touchpoint_type, 1.0),
                metadata=metadata or {},
                campaign_id=metadata.get("campaign_id"),
                device_type=metadata.get("device_type"),
                location=metadata.get("location"),
                duration_seconds=metadata.get("duration_seconds", 0)
            )
            
            if touchpoint_type == TouchpointType.PURCHASE:
                touchpoint.conversion_value = metadata.get("purchase_amount", 0)
            
            self.db.add(touchpoint)
            
            # Update journey
            journey.last_touchpoint = datetime.now()
            journey.total_touchpoints += 1
            journey.journey_score += touchpoint.engagement_score
            
            # Check for stage progression
            self._check_stage_progression(journey, touchpoint)
            
            # Update scores
            self._update_journey_scores(journey)
            
            self.db.commit()
            
            logger.info(f"Tracked {touchpoint_type} for customer {customer_id}")
            return touchpoint
            
        except Exception as e:
            logger.error(f"Error tracking touchpoint: {e}")
            self.db.rollback()
            raise
    
    def _check_stage_progression(self, journey: CustomerJourney, touchpoint: Touchpoint):
        """Check if customer should progress to next stage"""
        current_stage = LifecycleStage(journey.current_stage)
        new_stage = None
        
        # Stage progression rules
        if current_stage == LifecycleStage.AWARENESS:
            # Move to consideration after multiple engagements
            recent_touchpoints = self._get_recent_touchpoints_count(journey.customer_id, days=30)
            if recent_touchpoints >= 3:
                new_stage = LifecycleStage.CONSIDERATION
        
        elif current_stage == LifecycleStage.CONSIDERATION:
            # Move to purchase after high engagement or purchase
            if touchpoint.touchpoint_type == TouchpointType.PURCHASE.value:
                new_stage = LifecycleStage.PURCHASE
            elif journey.journey_score > 20:
                new_stage = LifecycleStage.PURCHASE
        
        elif current_stage == LifecycleStage.PURCHASE:
            # Move to retention after multiple purchases
            purchase_count = self._get_purchase_count(journey.customer_id)
            if purchase_count >= 3:
                new_stage = LifecycleStage.RETENTION
        
        elif current_stage == LifecycleStage.RETENTION:
            # Move to advocacy based on referrals or reviews
            if touchpoint.touchpoint_type in [TouchpointType.REFERRAL.value, TouchpointType.REVIEW.value]:
                referral_count = self._get_referral_count(journey.customer_id)
                if referral_count >= 2:
                    new_stage = LifecycleStage.ADVOCACY
        
        # Check for dormancy
        if self._is_dormant(journey):
            new_stage = LifecycleStage.DORMANT
        
        # Process stage transition
        if new_stage and new_stage != current_stage:
            self._transition_stage(journey, current_stage, new_stage, touchpoint.touchpoint_type)
    
    def _transition_stage(self, journey: CustomerJourney, from_stage: LifecycleStage, 
                         to_stage: LifecycleStage, trigger_event: str):
        """Record stage transition"""
        transition = StageTransition(
            journey_id=journey.id,
            customer_id=journey.customer_id,
            from_stage=from_stage.value,
            to_stage=to_stage.value,
            trigger_event=trigger_event,
            transition_score=journey.journey_score
        )
        
        self.db.add(transition)
        journey.current_stage = to_stage.value
        journey.stage_entered_at = datetime.now()
        
        logger.info(f"Customer {journey.customer_id} transitioned from {from_stage} to {to_stage}")
    
    def _update_journey_scores(self, journey: CustomerJourney):
        """Update various journey scores"""
        # Health score (0-100)
        journey.health_score = self._calculate_health_score(journey)
        
        # Risk score (0-100)
        journey.risk_score = self._calculate_risk_score(journey)
        
        # Momentum score (-100 to 100)
        journey.momentum_score = self._calculate_momentum_score(journey)
    
    def _calculate_health_score(self, journey: CustomerJourney) -> float:
        """Calculate overall journey health"""
        factors = []
        
        # Recency factor
        if journey.last_touchpoint:
            days_since_last = (datetime.now() - journey.last_touchpoint).days
            recency_score = max(0, 100 - (days_since_last * 2))
            factors.append(recency_score * 0.3)
        
        # Frequency factor
        frequency_score = min(100, journey.total_touchpoints * 5)
        factors.append(frequency_score * 0.3)
        
        # Stage factor
        stage_score = self.stage_weights.get(LifecycleStage(journey.current_stage), 1) * 20
        factors.append(stage_score * 0.2)
        
        # Engagement factor
        engagement_score = min(100, journey.journey_score * 2)
        factors.append(engagement_score * 0.2)
        
        return sum(factors)
    
    def _calculate_risk_score(self, journey: CustomerJourney) -> float:
        """Calculate churn risk score"""
        risk_factors = []
        
        # Inactivity risk
        if journey.last_touchpoint:
            days_inactive = (datetime.now() - journey.last_touchpoint).days
            if days_inactive > 60:
                risk_factors.append(50)
            elif days_inactive > 30:
                risk_factors.append(30)
            elif days_inactive > 14:
                risk_factors.append(10)
        
        # Stage risk
        if journey.current_stage == LifecycleStage.DORMANT.value:
            risk_factors.append(40)
        
        # Declining engagement
        if journey.momentum_score < -20:
            risk_factors.append(30)
        
        return min(100, sum(risk_factors))
    
    def _calculate_momentum_score(self, journey: CustomerJourney) -> float:
        """Calculate engagement momentum"""
        # Get touchpoints from last 30 and previous 30 days
        recent_touchpoints = self._get_touchpoints_by_period(journey.customer_id, 0, 30)
        previous_touchpoints = self._get_touchpoints_by_period(journey.customer_id, 30, 60)
        
        recent_score = sum(self.touchpoint_scores.get(TouchpointType(t.touchpoint_type), 1) 
                          for t in recent_touchpoints)
        previous_score = sum(self.touchpoint_scores.get(TouchpointType(t.touchpoint_type), 1) 
                           for t in previous_touchpoints)
        
        if previous_score == 0:
            return 50 if recent_score > 0 else 0
        
        # Calculate percentage change
        change = ((recent_score - previous_score) / previous_score) * 100
        return max(-100, min(100, change))
    
    def get_journey_analytics(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive journey analytics for a customer"""
        journey = self.db.query(CustomerJourney).filter(
            CustomerJourney.customer_id == customer_id
        ).first()
        
        if not journey:
            return {"error": "No journey found for customer"}
        
        # Get touchpoints
        touchpoints = self.db.query(Touchpoint).filter(
            Touchpoint.customer_id == customer_id
        ).order_by(Touchpoint.timestamp.desc()).all()
        
        # Get stage history
        stage_history = self.db.query(StageTransition).filter(
            StageTransition.customer_id == customer_id
        ).order_by(StageTransition.transition_date).all()
        
        # Calculate journey metrics
        journey_duration = (datetime.now() - journey.created_at).days
        avg_days_between_touchpoints = journey_duration / max(1, journey.total_touchpoints)
        
        # Channel distribution
        channel_dist = defaultdict(int)
        for tp in touchpoints:
            channel_dist[tp.channel] += 1
        
        # Most effective touchpoints
        high_value_touchpoints = [tp for tp in touchpoints if tp.engagement_score > 5]
        
        return {
            "customer_id": customer_id,
            "current_stage": journey.current_stage,
            "journey_score": journey.journey_score,
            "health_score": journey.health_score,
            "risk_score": journey.risk_score,
            "momentum_score": journey.momentum_score,
            "journey_duration_days": journey_duration,
            "total_touchpoints": journey.total_touchpoints,
            "avg_days_between_touchpoints": avg_days_between_touchpoints,
            "last_touchpoint": journey.last_touchpoint.isoformat() if journey.last_touchpoint else None,
            "channel_distribution": dict(channel_dist),
            "stage_history": [
                {
                    "from": sh.from_stage,
                    "to": sh.to_stage,
                    "date": sh.transition_date.isoformat(),
                    "trigger": sh.trigger_event
                } for sh in stage_history
            ],
            "recent_touchpoints": [
                {
                    "type": tp.touchpoint_type,
                    "channel": tp.channel,
                    "timestamp": tp.timestamp.isoformat(),
                    "engagement_score": tp.engagement_score
                } for tp in touchpoints[:10]
            ],
            "high_value_touchpoints": len(high_value_touchpoints),
            "recommendations": self._generate_journey_recommendations(journey, touchpoints)
        }
    
    def get_segment_journey_patterns(self, segment_id: int) -> Dict[str, Any]:
        """Analyze journey patterns for a customer segment"""
        # Get all customers in segment
        from core.database import Customer
        customers = self.db.query(Customer).filter(
            Customer.segment_id == segment_id
        ).all()
        
        customer_ids = [c.customer_id for c in customers]
        
        # Get journeys for segment
        journeys = self.db.query(CustomerJourney).filter(
            CustomerJourney.customer_id.in_(customer_ids)
        ).all()
        
        if not journeys:
            return {"error": "No journeys found for segment"}
        
        # Analyze patterns
        stage_distribution = defaultdict(int)
        avg_health_score = 0
        avg_journey_score = 0
        high_risk_count = 0
        
        for journey in journeys:
            stage_distribution[journey.current_stage] += 1
            avg_health_score += journey.health_score
            avg_journey_score += journey.journey_score
            if journey.risk_score > 50:
                high_risk_count += 1
        
        avg_health_score /= len(journeys)
        avg_journey_score /= len(journeys)
        
        # Common paths
        common_paths = self._analyze_common_paths(customer_ids)
        
        # Touchpoint patterns
        touchpoint_patterns = self._analyze_touchpoint_patterns(customer_ids)
        
        return {
            "segment_id": segment_id,
            "total_customers": len(customers),
            "journeys_tracked": len(journeys),
            "stage_distribution": dict(stage_distribution),
            "average_health_score": avg_health_score,
            "average_journey_score": avg_journey_score,
            "high_risk_percentage": (high_risk_count / len(journeys) * 100) if journeys else 0,
            "common_journey_paths": common_paths,
            "touchpoint_patterns": touchpoint_patterns,
            "optimization_opportunities": self._identify_optimization_opportunities(journeys)
        }
    
    def predict_next_stage(self, customer_id: str) -> Dict[str, Any]:
        """Predict next likely stage for customer"""
        journey = self.db.query(CustomerJourney).filter(
            CustomerJourney.customer_id == customer_id
        ).first()
        
        if not journey:
            return {"error": "No journey found"}
        
        # Simple rule-based prediction (can be replaced with ML model)
        current_stage = LifecycleStage(journey.current_stage)
        predictions = {}
        
        if current_stage == LifecycleStage.AWARENESS:
            predictions[LifecycleStage.CONSIDERATION] = 0.7
            predictions[LifecycleStage.DORMANT] = 0.2
            predictions[LifecycleStage.AWARENESS] = 0.1
        
        elif current_stage == LifecycleStage.CONSIDERATION:
            predictions[LifecycleStage.PURCHASE] = 0.5
            predictions[LifecycleStage.CONSIDERATION] = 0.3
            predictions[LifecycleStage.DORMANT] = 0.2
        
        elif current_stage == LifecycleStage.PURCHASE:
            predictions[LifecycleStage.RETENTION] = 0.6
            predictions[LifecycleStage.PURCHASE] = 0.3
            predictions[LifecycleStage.DORMANT] = 0.1
        
        elif current_stage == LifecycleStage.RETENTION:
            predictions[LifecycleStage.ADVOCACY] = 0.4
            predictions[LifecycleStage.RETENTION] = 0.5
            predictions[LifecycleStage.DORMANT] = 0.1
        
        # Adjust based on momentum
        if journey.momentum_score < -50:
            predictions[LifecycleStage.DORMANT] = predictions.get(LifecycleStage.DORMANT, 0) + 0.3
        
        # Normalize probabilities
        total = sum(predictions.values())
        predictions = {k.value: v/total for k, v in predictions.items()}
        
        # Get most likely next stage
        next_stage = max(predictions, key=predictions.get)
        
        return {
            "current_stage": current_stage.value,
            "predictions": predictions,
            "most_likely_next_stage": next_stage,
            "confidence": predictions[next_stage],
            "recommended_actions": self._get_stage_transition_actions(current_stage, next_stage)
        }
    
    def _generate_journey_recommendations(self, journey: CustomerJourney, 
                                        touchpoints: List[Touchpoint]) -> List[Dict[str, str]]:
        """Generate recommendations based on journey analysis"""
        recommendations = []
        
        # Risk-based recommendations
        if journey.risk_score > 70:
            recommendations.append({
                "type": "urgent",
                "action": "Immediate re-engagement campaign",
                "reason": "High churn risk detected"
            })
        
        # Stage-based recommendations
        if journey.current_stage == LifecycleStage.CONSIDERATION.value:
            recommendations.append({
                "type": "conversion",
                "action": "Send personalized product recommendations",
                "reason": "Customer in consideration phase"
            })
        
        # Momentum-based recommendations
        if journey.momentum_score > 50:
            recommendations.append({
                "type": "opportunity",
                "action": "Capitalize on high engagement with exclusive offer",
                "reason": "Strong positive momentum detected"
            })
        
        return recommendations
    
    def _get_stage_transition_actions(self, current_stage: LifecycleStage, 
                                    next_stage: str) -> List[str]:
        """Get recommended actions for stage transition"""
        actions = {
            (LifecycleStage.AWARENESS, LifecycleStage.CONSIDERATION.value): [
                "Send educational content about products",
                "Offer first-time visitor discount",
                "Retarget with social media ads"
            ],
            (LifecycleStage.CONSIDERATION, LifecycleStage.PURCHASE.value): [
                "Send abandoned cart reminders",
                "Offer limited-time promotion",
                "Provide customer testimonials"
            ],
            (LifecycleStage.PURCHASE, LifecycleStage.RETENTION.value): [
                "Enroll in loyalty program",
                "Send post-purchase follow-up",
                "Recommend complementary products"
            ],
            (LifecycleStage.RETENTION, LifecycleStage.ADVOCACY.value): [
                "Invite to VIP program",
                "Request product reviews",
                "Offer referral incentives"
            ]
        }
        
        return actions.get((current_stage, next_stage), ["Continue current engagement strategy"])
    
    # Helper methods
    def _get_recent_touchpoints_count(self, customer_id: str, days: int) -> int:
        """Get count of recent touchpoints"""
        since_date = datetime.now() - timedelta(days=days)
        return self.db.query(Touchpoint).filter(
            Touchpoint.customer_id == customer_id,
            Touchpoint.timestamp >= since_date
        ).count()
    
    def _get_purchase_count(self, customer_id: str) -> int:
        """Get total purchase count"""
        return self.db.query(Touchpoint).filter(
            Touchpoint.customer_id == customer_id,
            Touchpoint.touchpoint_type == TouchpointType.PURCHASE.value
        ).count()
    
    def _get_referral_count(self, customer_id: str) -> int:
        """Get referral count"""
        return self.db.query(Touchpoint).filter(
            Touchpoint.customer_id == customer_id,
            Touchpoint.touchpoint_type == TouchpointType.REFERRAL.value
        ).count()
    
    def _is_dormant(self, journey: CustomerJourney) -> bool:
        """Check if customer is dormant"""
        if not journey.last_touchpoint:
            return False
        
        days_inactive = (datetime.now() - journey.last_touchpoint).days
        return days_inactive > 90  # 90 days of inactivity
    
    def _get_touchpoints_by_period(self, customer_id: str, 
                                  start_days_ago: int, end_days_ago: int) -> List[Touchpoint]:
        """Get touchpoints within a specific period"""
        start_date = datetime.now() - timedelta(days=end_days_ago)
        end_date = datetime.now() - timedelta(days=start_days_ago)
        
        return self.db.query(Touchpoint).filter(
            Touchpoint.customer_id == customer_id,
            Touchpoint.timestamp >= start_date,
            Touchpoint.timestamp <= end_date
        ).all()
    
    def _analyze_common_paths(self, customer_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze common journey paths"""
        # Get stage transitions for all customers
        transitions = self.db.query(StageTransition).filter(
            StageTransition.customer_id.in_(customer_ids)
        ).all()
        
        # Count path frequencies
        path_counts = defaultdict(int)
        for transition in transitions:
            path = f"{transition.from_stage} → {transition.to_stage}"
            path_counts[path] += 1
        
        # Sort by frequency
        common_paths = sorted(
            [{"path": path, "count": count} for path, count in path_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return common_paths[:5]  # Top 5 paths
    
    def _analyze_touchpoint_patterns(self, customer_ids: List[str]) -> Dict[str, Any]:
        """Analyze touchpoint patterns for customers"""
        touchpoints = self.db.query(Touchpoint).filter(
            Touchpoint.customer_id.in_(customer_ids)
        ).all()
        
        # Analyze patterns
        type_distribution = defaultdict(int)
        channel_distribution = defaultdict(int)
        total_engagement = 0
        
        for tp in touchpoints:
            type_distribution[tp.touchpoint_type] += 1
            channel_distribution[tp.channel] += 1
            total_engagement += tp.engagement_score
        
        return {
            "most_common_touchpoint": max(type_distribution, key=type_distribution.get) if type_distribution else None,
            "preferred_channel": max(channel_distribution, key=channel_distribution.get) if channel_distribution else None,
            "average_engagement_score": total_engagement / len(touchpoints) if touchpoints else 0,
            "touchpoint_distribution": dict(type_distribution),
            "channel_distribution": dict(channel_distribution)
        }
    
    def _identify_optimization_opportunities(self, journeys: List[CustomerJourney]) -> List[Dict[str, str]]:
        """Identify journey optimization opportunities"""
        opportunities = []
        
        # Check for high drop-off stages
        stage_counts = defaultdict(int)
        for journey in journeys:
            stage_counts[journey.current_stage] += 1
        
        if stage_counts.get(LifecycleStage.CONSIDERATION.value, 0) > len(journeys) * 0.4:
            opportunities.append({
                "opportunity": "High consideration stage accumulation",
                "action": "Improve conversion tactics to move customers to purchase"
            })
        
        # Check for dormancy
        dormant_count = stage_counts.get(LifecycleStage.DORMANT.value, 0)
        if dormant_count > len(journeys) * 0.2:
            opportunities.append({
                "opportunity": f"{dormant_count} customers are dormant",
                "action": "Launch reactivation campaign"
            })
        
        # Check journey health
        avg_health = sum(j.health_score for j in journeys) / len(journeys) if journeys else 0
        if avg_health < 50:
            opportunities.append({
                "opportunity": "Low average journey health score",
                "action": "Increase engagement frequency and quality"
            })
        
        return opportunities