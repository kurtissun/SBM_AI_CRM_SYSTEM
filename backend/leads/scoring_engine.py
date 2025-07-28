"""
Lead Scoring and Qualification System
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import numpy as np
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

from core.database import Base, get_db
from journey.lifecycle_manager import TouchpointType, LifecycleStage

logger = logging.getLogger(__name__)

class LeadQuality(str, Enum):
    """Lead quality levels"""
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"
    QUALIFIED = "qualified"

class LeadStatus(str, Enum):
    """Lead status types"""
    NEW = "new"
    MQL = "mql"  # Marketing Qualified Lead
    SQL = "sql"  # Sales Qualified Lead
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    LOST = "lost"

class ScoreType(str, Enum):
    """Types of scores"""
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    FIRMOGRAPHIC = "firmographic"
    PREDICTIVE = "predictive"
    COMPOSITE = "composite"

# Database Models
class LeadScore(Base):
    """Lead scoring records"""
    __tablename__ = "lead_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    score_type = Column(String)  # behavioral, demographic, predictive, composite
    score_value = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)
    score_factors = Column(JSON, default={})  # Breakdown of score components
    calculated_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    model_version = Column(String)
    
    # Relationships
    scoring_events = relationship("ScoringEvent", back_populates="lead_score")

class ScoringEvent(Base):
    """Individual scoring events"""
    __tablename__ = "scoring_events"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_score_id = Column(Integer, ForeignKey("lead_scores.id"), index=True)
    customer_id = Column(String, index=True)
    event_type = Column(String)
    event_description = Column(Text)
    score_change = Column(Float)
    previous_score = Column(Float)
    new_score = Column(Float)
    event_metadata = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.now)
    
    # Relationships
    lead_score = relationship("LeadScore", back_populates="scoring_events")

class LeadQualification(Base):
    """Lead qualification records"""
    __tablename__ = "lead_qualifications"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    lead_status = Column(String, default=LeadStatus.NEW.value)
    lead_quality = Column(String, default=LeadQuality.COLD.value)
    qualification_score = Column(Float, default=0.0)
    qualification_criteria = Column(JSON, default={})
    qualified_by = Column(String)  # system, manual, ai
    qualified_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)
    next_action = Column(String)
    assigned_to = Column(String)

class ScoringRule(Base):
    """Configurable scoring rules"""
    __tablename__ = "scoring_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, unique=True)
    rule_type = Column(String)  # behavioral, demographic, custom
    condition = Column(JSON)  # Rule conditions
    score_value = Column(Float)  # Points to award
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

@dataclass
class ScoringFactors:
    """Score component breakdown"""
    behavioral_score: float = 0.0
    demographic_score: float = 0.0
    engagement_score: float = 0.0
    conversion_probability: float = 0.0
    recency_score: float = 0.0
    frequency_score: float = 0.0
    
class LeadScoringEngine:
    """Advanced lead scoring and qualification system"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scoring_model = None
        self.scaler = StandardScaler()
        self.model_version = "1.0"
        
        # Default scoring weights
        self.score_weights = {
            ScoreType.BEHAVIORAL: 0.4,
            ScoreType.DEMOGRAPHIC: 0.2,
            ScoreType.FIRMOGRAPHIC: 0.2,
            ScoreType.PREDICTIVE: 0.2
        }
        
        # Behavioral scoring values
        self.behavioral_scores = {
            TouchpointType.WEBSITE_VISIT: 2,
            TouchpointType.STORE_VISIT: 8,
            TouchpointType.EMAIL_OPEN: 1,
            TouchpointType.EMAIL_CLICK: 5,
            TouchpointType.APP_OPEN: 3,
            TouchpointType.PURCHASE: 25,
            TouchpointType.CUSTOMER_SERVICE: 4,
            TouchpointType.SOCIAL_MEDIA: 3,
            TouchpointType.REVIEW: 10,
            TouchpointType.REFERRAL: 15
        }
        
        # Load or initialize ML model
        self._initialize_scoring_model()
    
    def calculate_lead_score(self, customer_id: str, score_type: ScoreType = None) -> Dict[str, Any]:
        """Calculate comprehensive lead score for a customer"""
        try:
            # Calculate different score components
            behavioral_score = self._calculate_behavioral_score(customer_id)
            demographic_score = self._calculate_demographic_score(customer_id)
            predictive_score = self._calculate_predictive_score(customer_id)
            
            # Get existing score record or create new
            lead_score = self.db.query(LeadScore).filter(
                LeadScore.customer_id == customer_id,
                LeadScore.score_type == ScoreType.COMPOSITE.value
            ).order_by(LeadScore.calculated_at.desc()).first()
            
            if not lead_score:
                lead_score = LeadScore(
                    customer_id=customer_id,
                    score_type=ScoreType.COMPOSITE.value,
                    model_version=self.model_version
                )
                self.db.add(lead_score)
            
            # Calculate composite score
            composite_score = (
                behavioral_score * self.score_weights[ScoreType.BEHAVIORAL] +
                demographic_score * self.score_weights[ScoreType.DEMOGRAPHIC] +
                predictive_score * self.score_weights[ScoreType.PREDICTIVE]
            )
            
            # Normalize to 0-100 scale
            composite_score = min(100, max(0, composite_score))
            
            # Store previous score for change tracking
            previous_score = lead_score.score_value
            
            # Update score record
            lead_score.score_value = composite_score
            lead_score.score_factors = {
                "behavioral": behavioral_score,
                "demographic": demographic_score,
                "predictive": predictive_score,
                "engagement": self._calculate_engagement_score(customer_id),
                "recency": self._calculate_recency_score(customer_id),
                "frequency": self._calculate_frequency_score(customer_id)
            }
            lead_score.calculated_at = datetime.now()
            lead_score.expires_at = datetime.now() + timedelta(hours=24)  # Refresh daily
            
            # Log scoring event if score changed significantly
            if abs(composite_score - previous_score) >= 5:
                self._log_scoring_event(
                    lead_score.id, customer_id, "score_update",
                    f"Score changed from {previous_score:.1f} to {composite_score:.1f}",
                    composite_score - previous_score, previous_score, composite_score
                )
            
            self.db.commit()
            
            # Determine lead quality
            lead_quality = self._determine_lead_quality(composite_score)
            
            return {
                "customer_id": customer_id,
                "composite_score": composite_score,
                "previous_score": previous_score,
                "score_change": composite_score - previous_score,
                "lead_quality": lead_quality,
                "score_breakdown": lead_score.score_factors,
                "calculated_at": lead_score.calculated_at.isoformat(),
                "recommendations": self._generate_score_recommendations(composite_score, lead_score.score_factors)
            }
            
        except Exception as e:
            logger.error(f"Error calculating lead score: {e}")
            self.db.rollback()
            raise
    
    def _calculate_behavioral_score(self, customer_id: str) -> float:
        """Calculate behavioral score based on customer actions"""
        try:
            # Get recent touchpoints (last 30 days)
            from journey.lifecycle_manager import Touchpoint
            recent_touchpoints = self.db.query(Touchpoint).filter(
                Touchpoint.customer_id == customer_id,
                Touchpoint.timestamp >= datetime.now() - timedelta(days=30)
            ).all()
            
            if not recent_touchpoints:
                return 0.0
            
            total_score = 0.0
            engagement_multiplier = 1.0
            
            # Score based on touchpoint types
            for touchpoint in recent_touchpoints:
                try:
                    touchpoint_type = TouchpointType(touchpoint.touchpoint_type)
                    base_score = self.behavioral_scores.get(touchpoint_type, 1)
                    
                    # Apply engagement multiplier
                    score = base_score * engagement_multiplier
                    
                    # Bonus for recent activity (last 7 days)
                    if touchpoint.timestamp >= datetime.now() - timedelta(days=7):
                        score *= 1.5
                    
                    # Bonus for high-value touchpoints
                    if touchpoint.conversion_value and touchpoint.conversion_value > 0:
                        score *= (1 + touchpoint.conversion_value / 1000)  # $1000 doubles the score
                    
                    total_score += score
                    
                except ValueError:
                    # Handle unknown touchpoint types
                    total_score += 1
            
            # Apply frequency bonus
            unique_days = len(set(tp.timestamp.date() for tp in recent_touchpoints))
            frequency_bonus = min(unique_days * 2, 20)  # Up to 20 bonus points
            
            total_score += frequency_bonus
            
            # Apply custom scoring rules
            rule_score = self._apply_behavioral_rules(customer_id, recent_touchpoints)
            total_score += rule_score
            
            return min(100, total_score)
            
        except Exception as e:
            logger.error(f"Error calculating behavioral score: {e}")
            return 0.0
    
    def _calculate_demographic_score(self, customer_id: str) -> float:
        """Calculate demographic score based on customer profile"""
        try:
            from core.database import Customer
            customer = self.db.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return 0.0
            
            score = 0.0
            
            # Age scoring (prefer specific age ranges based on business)
            if customer.age:
                if 25 <= customer.age <= 45:  # Prime shopping age
                    score += 15
                elif 18 <= customer.age <= 65:  # Active shoppers
                    score += 10
                else:
                    score += 5
            
            # Gender scoring (if relevant to business)
            if customer.gender:
                score += 5  # Basic points for complete profile
            
            # Rating scoring
            if customer.rating_id:
                score += customer.rating_id * 5  # 5-25 points based on rating
            
            # Segment scoring
            if customer.segment_id is not None:
                # High-value segments get bonus points
                high_value_segments = [0, 2, 4]  # Tech, Tourists, Premium
                if customer.segment_id in high_value_segments:
                    score += 20
                else:
                    score += 10
            
            # Profile completeness
            completeness_score = self._calculate_profile_completeness(customer)
            score += completeness_score * 20  # Up to 20 points for complete profile
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"Error calculating demographic score: {e}")
            return 0.0
    
    def _calculate_predictive_score(self, customer_id: str) -> float:
        """Calculate predictive score using ML model"""
        try:
            if not self.scoring_model:
                return 50.0  # Default score if model not available
            
            # Prepare features for ML model
            features = self._prepare_ml_features(customer_id)
            if not features:
                return 50.0
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict conversion probability
            prediction = self.scoring_model.predict(features_scaled)[0]
            
            # Convert probability to 0-100 score
            predictive_score = min(100, max(0, prediction * 100))
            
            return predictive_score
            
        except Exception as e:
            logger.error(f"Error calculating predictive score: {e}")
            return 50.0
    
    def _calculate_engagement_score(self, customer_id: str) -> float:
        """Calculate engagement score based on interaction quality"""
        try:
            from journey.lifecycle_manager import Touchpoint
            recent_touchpoints = self.db.query(Touchpoint).filter(
                Touchpoint.customer_id == customer_id,
                Touchpoint.timestamp >= datetime.now() - timedelta(days=30)
            ).all()
            
            if not recent_touchpoints:
                return 0.0
            
            total_engagement = sum(tp.engagement_score for tp in recent_touchpoints)
            avg_engagement = total_engagement / len(recent_touchpoints)
            
            # Normalize to 0-100 scale
            return min(100, avg_engagement * 10)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    def _calculate_recency_score(self, customer_id: str) -> float:
        """Calculate recency score based on last activity"""
        try:
            from journey.lifecycle_manager import Touchpoint
            last_touchpoint = self.db.query(Touchpoint).filter(
                Touchpoint.customer_id == customer_id
            ).order_by(Touchpoint.timestamp.desc()).first()
            
            if not last_touchpoint:
                return 0.0
            
            days_since_last = (datetime.now() - last_touchpoint.timestamp).days
            
            # Recency scoring (more recent = higher score)
            if days_since_last <= 1:
                return 100
            elif days_since_last <= 7:
                return 80
            elif days_since_last <= 30:
                return 60
            elif days_since_last <= 90:
                return 40
            else:
                return 20
                
        except Exception as e:
            logger.error(f"Error calculating recency score: {e}")
            return 0.0
    
    def _calculate_frequency_score(self, customer_id: str) -> float:
        """Calculate frequency score based on interaction frequency"""
        try:
            from journey.lifecycle_manager import Touchpoint
            touchpoints_30d = self.db.query(Touchpoint).filter(
                Touchpoint.customer_id == customer_id,
                Touchpoint.timestamp >= datetime.now() - timedelta(days=30)
            ).count()
            
            # Frequency scoring
            if touchpoints_30d >= 20:
                return 100
            elif touchpoints_30d >= 10:
                return 80
            elif touchpoints_30d >= 5:
                return 60
            elif touchpoints_30d >= 2:
                return 40
            elif touchpoints_30d >= 1:
                return 20
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating frequency score: {e}")
            return 0.0
    
    def qualify_lead(self, customer_id: str, threshold: float = 70.0) -> Dict[str, Any]:
        """Qualify lead based on score and criteria"""
        try:
            # Get current lead score
            score_result = self.calculate_lead_score(customer_id)
            composite_score = score_result["composite_score"]
            
            # Get or create qualification record
            qualification = self.db.query(LeadQualification).filter(
                LeadQualification.customer_id == customer_id
            ).order_by(LeadQualification.qualified_at.desc()).first()
            
            if not qualification:
                qualification = LeadQualification(customer_id=customer_id)
                self.db.add(qualification)
            
            previous_status = qualification.lead_status
            
            # Determine new lead status
            if composite_score >= threshold:
                if composite_score >= 90:
                    qualification.lead_status = LeadStatus.SQL.value
                    qualification.lead_quality = LeadQuality.HOT.value
                else:
                    qualification.lead_status = LeadStatus.MQL.value
                    qualification.lead_quality = LeadQuality.QUALIFIED.value
            else:
                qualification.lead_status = LeadStatus.NEW.value
                if composite_score >= 50:
                    qualification.lead_quality = LeadQuality.WARM.value
                else:
                    qualification.lead_quality = LeadQuality.COLD.value
            
            qualification.qualification_score = composite_score
            qualification.qualified_by = "system"
            qualification.qualified_at = datetime.now()
            
            # Set qualification criteria
            qualification.qualification_criteria = {
                "score_threshold": threshold,
                "score_achieved": composite_score,
                "behavioral_score": score_result["score_breakdown"]["behavioral"],
                "demographic_score": score_result["score_breakdown"]["demographic"],
                "predictive_score": score_result["score_breakdown"]["predictive"]
            }
            
            # Recommend next actions
            next_actions = self._recommend_next_actions(qualification.lead_status, composite_score)
            qualification.next_action = ", ".join(next_actions)
            
            self.db.commit()
            
            # Check if status changed
            status_changed = previous_status != qualification.lead_status
            
            return {
                "customer_id": customer_id,
                "lead_status": qualification.lead_status,
                "lead_quality": qualification.lead_quality,
                "qualification_score": qualification.qualification_score,
                "status_changed": status_changed,
                "previous_status": previous_status,
                "qualification_criteria": qualification.qualification_criteria,
                "next_actions": next_actions,
                "qualified_at": qualification.qualified_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            self.db.rollback()
            raise
    
    def get_lead_insights(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive lead insights and analytics"""
        try:
            # Get current scores
            score_result = self.calculate_lead_score(customer_id)
            
            # Get qualification status
            qualification = self.db.query(LeadQualification).filter(
                LeadQualification.customer_id == customer_id
            ).order_by(LeadQualification.qualified_at.desc()).first()
            
            # Get scoring history
            score_history = self.db.query(LeadScore).filter(
                LeadScore.customer_id == customer_id
            ).order_by(LeadScore.calculated_at.desc()).limit(10).all()
            
            # Get scoring events
            scoring_events = self.db.query(ScoringEvent).filter(
                ScoringEvent.customer_id == customer_id
            ).order_by(ScoringEvent.timestamp.desc()).limit(20).all()
            
            # Calculate trends
            score_trend = self._calculate_score_trend(score_history)
            
            return {
                "customer_id": customer_id,
                "current_score": score_result,
                "qualification": {
                    "status": qualification.lead_status if qualification else "new",
                    "quality": qualification.lead_quality if qualification else "cold",
                    "next_actions": qualification.next_action.split(", ") if qualification and qualification.next_action else []
                },
                "score_trend": score_trend,
                "score_history": [
                    {
                        "score": score.score_value,
                        "calculated_at": score.calculated_at.isoformat(),
                        "factors": score.score_factors
                    } for score in score_history
                ],
                "recent_events": [
                    {
                        "event_type": event.event_type,
                        "description": event.event_description,
                        "score_change": event.score_change,
                        "timestamp": event.timestamp.isoformat()
                    } for event in scoring_events
                ],
                "optimization_suggestions": self._generate_optimization_suggestions(score_result, qualification)
            }
            
        except Exception as e:
            logger.error(f"Error getting lead insights: {e}")
            raise
    
    def get_segment_scoring_analysis(self, segment_id: int) -> Dict[str, Any]:
        """Analyze lead scoring patterns for a customer segment"""
        try:
            # Get customers in segment
            from core.database import Customer
            customers = self.db.query(Customer).filter(
                Customer.segment_id == segment_id
            ).all()
            
            customer_ids = [c.customer_id for c in customers]
            
            if not customer_ids:
                return {"error": "No customers found in segment"}
            
            # Get lead scores for segment
            lead_scores = self.db.query(LeadScore).filter(
                LeadScore.customer_id.in_(customer_ids),
                LeadScore.score_type == ScoreType.COMPOSITE.value
            ).all()
            
            # Get qualifications
            qualifications = self.db.query(LeadQualification).filter(
                LeadQualification.customer_id.in_(customer_ids)
            ).all()
            
            # Analyze patterns
            scores = [ls.score_value for ls in lead_scores]
            avg_score = np.mean(scores) if scores else 0
            median_score = np.median(scores) if scores else 0
            
            # Quality distribution
            quality_dist = {}
            status_dist = {}
            for qual in qualifications:
                quality_dist[qual.lead_quality] = quality_dist.get(qual.lead_quality, 0) + 1
                status_dist[qual.lead_status] = status_dist.get(qual.lead_status, 0) + 1
            
            # High potential leads
            high_potential = len([s for s in scores if s >= 70])
            
            return {
                "segment_id": segment_id,
                "total_customers": len(customers),
                "scored_customers": len(lead_scores),
                "average_score": avg_score,
                "median_score": median_score,
                "score_distribution": {
                    "90-100": len([s for s in scores if s >= 90]),
                    "70-89": len([s for s in scores if 70 <= s < 90]),
                    "50-69": len([s for s in scores if 50 <= s < 70]),
                    "30-49": len([s for s in scores if 30 <= s < 50]),
                    "0-29": len([s for s in scores if s < 30])
                },
                "quality_distribution": quality_dist,
                "status_distribution": status_dist,
                "high_potential_leads": high_potential,
                "conversion_potential": (high_potential / len(customers) * 100) if customers else 0,
                "recommendations": self._generate_segment_recommendations(avg_score, quality_dist, status_dist)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing segment scoring: {e}")
            raise
    
    # Helper methods
    def _initialize_scoring_model(self):
        """Initialize or load ML scoring model"""
        try:
            # Try to load existing model
            # In production, this would load from a file or model registry
            self.scoring_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Train with sample data if no model exists
            # In production, this would be trained on historical conversion data
            sample_features = np.random.random((1000, 10))
            sample_targets = np.random.random(1000)
            
            self.scoring_model.fit(sample_features, sample_targets)
            self.scaler.fit(sample_features)
            
            logger.info("Lead scoring model initialized")
            
        except Exception as e:
            logger.error(f"Error initializing scoring model: {e}")
            self.scoring_model = None
    
    def _prepare_ml_features(self, customer_id: str) -> List[float]:
        """Prepare features for ML model prediction"""
        try:
            # Get customer data
            from core.database import Customer
            from journey.lifecycle_manager import Touchpoint
            
            customer = self.db.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return None
            
            # Get touchpoint data
            touchpoints = self.db.query(Touchpoint).filter(
                Touchpoint.customer_id == customer_id,
                Touchpoint.timestamp >= datetime.now() - timedelta(days=90)
            ).all()
            
            # Feature engineering
            features = [
                customer.age or 0,
                customer.rating_id or 0,
                customer.segment_id or 0,
                len(touchpoints),  # Total touchpoints
                len([tp for tp in touchpoints if tp.touchpoint_type == TouchpointType.PURCHASE.value]),  # Purchases
                len(set(tp.timestamp.date() for tp in touchpoints)),  # Active days
                sum(tp.engagement_score for tp in touchpoints),  # Total engagement
                (datetime.now() - customer.created_at).days if customer.created_at else 0,  # Account age
                1 if customer.gender == "F" else 0,  # Gender encoding
                sum(tp.conversion_value or 0 for tp in touchpoints)  # Total conversion value
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing ML features: {e}")
            return None
    
    def _apply_behavioral_rules(self, customer_id: str, touchpoints: List) -> float:
        """Apply custom behavioral scoring rules"""
        try:
            rules = self.db.query(ScoringRule).filter(
                ScoringRule.rule_type == "behavioral",
                ScoringRule.is_active == True
            ).all()
            
            total_rule_score = 0.0
            
            for rule in rules:
                condition = rule.condition
                
                # Evaluate rule condition
                if self._evaluate_scoring_rule(condition, customer_id, touchpoints):
                    total_rule_score += rule.score_value
            
            return total_rule_score
            
        except Exception as e:
            logger.error(f"Error applying behavioral rules: {e}")
            return 0.0
    
    def _evaluate_scoring_rule(self, condition: Dict[str, Any], 
                              customer_id: str, touchpoints: List) -> bool:
        """Evaluate a scoring rule condition"""
        try:
            condition_type = condition.get("type")
            
            if condition_type == "touchpoint_count":
                touchpoint_type = condition.get("touchpoint_type")
                operator = condition.get("operator", ">=")
                value = condition.get("value", 0)
                
                count = len([tp for tp in touchpoints if tp.touchpoint_type == touchpoint_type])
                
                if operator == ">=":
                    return count >= value
                elif operator == "==":
                    return count == value
                elif operator == ">":
                    return count > value
            
            elif condition_type == "purchase_amount":
                operator = condition.get("operator", ">=")
                value = condition.get("value", 0)
                
                total_amount = sum(tp.conversion_value or 0 for tp in touchpoints 
                                 if tp.touchpoint_type == TouchpointType.PURCHASE.value)
                
                if operator == ">=":
                    return total_amount >= value
                elif operator == ">":
                    return total_amount > value
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating scoring rule: {e}")
            return False
    
    def _calculate_profile_completeness(self, customer) -> float:
        """Calculate customer profile completeness (0-1)"""
        fields = ["age", "gender", "email", "phone"]
        completed_fields = sum(1 for field in fields if getattr(customer, field, None))
        return completed_fields / len(fields)
    
    def _determine_lead_quality(self, score: float) -> str:
        """Determine lead quality based on score"""
        if score >= 80:
            return LeadQuality.HOT.value
        elif score >= 60:
            return LeadQuality.QUALIFIED.value
        elif score >= 40:
            return LeadQuality.WARM.value
        else:
            return LeadQuality.COLD.value
    
    def _generate_score_recommendations(self, score: float, 
                                      score_factors: Dict[str, float]) -> List[str]:
        """Generate recommendations based on score analysis"""
        recommendations = []
        
        if score < 50:
            recommendations.append("Increase engagement through targeted content")
            
            if score_factors.get("behavioral", 0) < 20:
                recommendations.append("Encourage more website and store visits")
            
            if score_factors.get("demographic", 0) < 30:
                recommendations.append("Complete customer profile information")
        
        elif score < 70:
            recommendations.append("Nurture with personalized campaigns")
            recommendations.append("Provide exclusive offers to increase engagement")
        
        else:
            recommendations.append("Ready for sales outreach")
            recommendations.append("Provide premium service experience")
        
        # Specific factor recommendations
        if score_factors.get("recency", 0) < 50:
            recommendations.append("Re-engage inactive customer")
        
        if score_factors.get("frequency", 0) < 50:
            recommendations.append("Increase touchpoint frequency")
        
        return recommendations
    
    def _recommend_next_actions(self, lead_status: str, score: float) -> List[str]:
        """Recommend next actions based on lead status"""
        if lead_status == LeadStatus.SQL.value:
            return ["Direct sales contact", "Personalized demo", "Premium service invitation"]
        elif lead_status == LeadStatus.MQL.value:
            return ["Targeted campaign", "Product education", "Limited-time offer"]
        elif lead_status == LeadStatus.NEW.value:
            if score >= 40:
                return ["Nurture campaign", "Content engagement", "Social proof"]
            else:
                return ["Awareness campaign", "Educational content", "Brand introduction"]
        else:
            return ["Monitor engagement", "General campaigns"]
    
    def _calculate_score_trend(self, score_history: List) -> Dict[str, Any]:
        """Calculate score trend from history"""
        if len(score_history) < 2:
            return {"trend": "insufficient_data"}
        
        scores = [s.score_value for s in score_history]
        scores.reverse()  # Oldest to newest
        
        # Simple trend calculation
        recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        older_avg = np.mean(scores[:-3]) if len(scores) >= 6 else scores[0]
        
        trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        trend_magnitude = abs(recent_avg - older_avg)
        
        return {
            "trend": trend_direction,
            "magnitude": trend_magnitude,
            "recent_average": recent_avg,
            "change_percentage": ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        }
    
    def _generate_optimization_suggestions(self, score_result: Dict[str, Any], 
                                         qualification) -> List[str]:
        """Generate optimization suggestions for lead scoring"""
        suggestions = []
        
        score_breakdown = score_result.get("score_breakdown", {})
        
        # Low behavioral score
        if score_breakdown.get("behavioral", 0) < 30:
            suggestions.append("Increase digital engagement through app notifications and email campaigns")
        
        # Low demographic score
        if score_breakdown.get("demographic", 0) < 30:
            suggestions.append("Complete customer profile through progressive profiling")
        
        # Low predictive score
        if score_breakdown.get("predictive", 0) < 50:
            suggestions.append("Focus on conversion optimization and purchase incentives")
        
        # Status-specific suggestions
        if qualification and qualification.lead_status == LeadStatus.NEW.value:
            suggestions.append("Implement lead nurturing workflow to move through sales funnel")
        
        return suggestions
    
    def _generate_segment_recommendations(self, avg_score: float, 
                                        quality_dist: Dict[str, int],
                                        status_dist: Dict[str, int]) -> List[str]:
        """Generate recommendations for segment scoring optimization"""
        recommendations = []
        
        if avg_score < 50:
            recommendations.append("Focus on engagement improvement strategies for this segment")
        
        # Check distribution patterns
        total_leads = sum(quality_dist.values())
        if total_leads > 0:
            cold_percentage = quality_dist.get(LeadQuality.COLD.value, 0) / total_leads * 100
            if cold_percentage > 60:
                recommendations.append("Implement segment-specific warming campaigns")
        
        qualified_count = status_dist.get(LeadStatus.MQL.value, 0) + status_dist.get(LeadStatus.SQL.value, 0)
        if qualified_count < total_leads * 0.2:
            recommendations.append("Optimize qualification criteria and nurturing processes")
        
        return recommendations
    
    def _log_scoring_event(self, lead_score_id: int, customer_id: str, 
                          event_type: str, description: str, score_change: float,
                          previous_score: float, new_score: float, metadata: Dict = None):
        """Log a scoring event"""
        event = ScoringEvent(
            lead_score_id=lead_score_id,
            customer_id=customer_id,
            event_type=event_type,
            event_description=description,
            score_change=score_change,
            previous_score=previous_score,
            new_score=new_score,
            event_metadata=metadata or {}
        )
        
        self.db.add(event)
        # Note: Commit handled by calling function