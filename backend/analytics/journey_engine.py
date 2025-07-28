"""
Customer Journey & Cohort Analytics Engine
Advanced customer flow analysis, journey mapping, and cohort retention analytics
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict, Counter
import uuid
import json

logger = logging.getLogger(__name__)

class JourneyStage(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    PURCHASE = "purchase"
    ONBOARDING = "onboarding"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    CHURN = "churn"

class TouchpointType(Enum):
    WEBSITE_VISIT = "website_visit"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    CUSTOMER_SERVICE = "customer_service"
    PURCHASE = "purchase"
    PRODUCT_USAGE = "product_usage"
    REVIEW = "review"
    REFERRAL = "referral"

class CohortType(Enum):
    ACQUISITION = "acquisition"
    BEHAVIORAL = "behavioral"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    PRODUCT = "product"

@dataclass
class JourneyTouchpoint:
    touchpoint_id: str
    customer_id: str
    touchpoint_type: TouchpointType
    stage: JourneyStage
    timestamp: datetime
    channel: str
    campaign_id: Optional[str]
    content_id: Optional[str]
    value: Optional[float]
    duration_seconds: Optional[int]
    metadata: Dict[str, Any]

@dataclass
class CustomerJourney:
    customer_id: str
    journey_start: datetime
    journey_end: Optional[datetime]
    current_stage: JourneyStage
    touchpoints: List[JourneyTouchpoint]
    conversion_events: List[str]
    time_to_conversion: Optional[int]
    total_value: float
    journey_score: float
    path_analysis: Dict[str, Any]

@dataclass
class CohortMetrics:
    cohort_id: str
    cohort_name: str
    cohort_type: CohortType
    cohort_date: datetime
    cohort_size: int
    retention_rates: Dict[str, float]  # period -> retention rate
    revenue_metrics: Dict[str, float]
    engagement_metrics: Dict[str, float]
    churn_analysis: Dict[str, Any]
    lifetime_value: float
    
@dataclass
class JourneyFlow:
    flow_id: str
    source_stage: JourneyStage
    target_stage: JourneyStage
    transition_count: int
    conversion_rate: float
    avg_time_to_transition: float
    success_factors: List[str]
    friction_points: List[str]

class JourneyAnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
        
    def track_customer_journey(self, customer_id: str, touchpoint_data: Dict[str, Any]) -> str:
        """Track a customer journey touchpoint"""
        try:
            touchpoint = JourneyTouchpoint(
                touchpoint_id=str(uuid.uuid4()),
                customer_id=customer_id,
                touchpoint_type=TouchpointType(touchpoint_data["touchpoint_type"]),
                stage=JourneyStage(touchpoint_data["stage"]),
                timestamp=touchpoint_data.get("timestamp", datetime.now()),
                channel=touchpoint_data["channel"],
                campaign_id=touchpoint_data.get("campaign_id"),
                content_id=touchpoint_data.get("content_id"),
                value=touchpoint_data.get("value"),
                duration_seconds=touchpoint_data.get("duration_seconds"),
                metadata=touchpoint_data.get("metadata", {})
            )
            
            # Store touchpoint (in production, this would go to database)
            logger.info(f"Journey touchpoint tracked: {customer_id} - {touchpoint.touchpoint_type.value}")
            
            return touchpoint.touchpoint_id
            
        except Exception as e:
            logger.error(f"Failed to track journey touchpoint: {e}")
            raise

    def analyze_customer_journey(self, customer_id: str, days_back: int = 90) -> CustomerJourney:
        """Analyze complete customer journey"""
        try:
            # Get customer journey data (simulated for demo)
            journey_data = self._simulate_customer_journey_data(customer_id, days_back)
            
            if not journey_data:
                raise ValueError(f"No journey data found for customer {customer_id}")
            
            # Analyze journey stages
            touchpoints = []
            conversion_events = []
            total_value = 0.0
            
            for event in journey_data:
                touchpoint = JourneyTouchpoint(
                    touchpoint_id=event["id"],
                    customer_id=customer_id,
                    touchpoint_type=TouchpointType(event["touchpoint_type"]),
                    stage=JourneyStage(event["stage"]),
                    timestamp=event["timestamp"],
                    channel=event["channel"],
                    campaign_id=event.get("campaign_id"),
                    content_id=event.get("content_id"),
                    value=event.get("value", 0),
                    duration_seconds=event.get("duration_seconds"),
                    metadata=event.get("metadata", {})
                )
                touchpoints.append(touchpoint)
                
                if touchpoint.touchpoint_type == TouchpointType.PURCHASE:
                    conversion_events.append(touchpoint.touchpoint_id)
                    total_value += touchpoint.value or 0
            
            # Calculate journey metrics
            journey_start = min(tp.timestamp for tp in touchpoints)
            journey_end = max(tp.timestamp for tp in touchpoints) if touchpoints else None
            current_stage = self._determine_current_stage(touchpoints)
            
            time_to_conversion = None
            if conversion_events:
                first_conversion = min(tp.timestamp for tp in touchpoints if tp.touchpoint_id in conversion_events)
                time_to_conversion = (first_conversion - journey_start).days
            
            journey_score = self._calculate_journey_score(touchpoints, total_value)
            path_analysis = self._analyze_journey_path(touchpoints)
            
            return CustomerJourney(
                customer_id=customer_id,
                journey_start=journey_start,
                journey_end=journey_end,
                current_stage=current_stage,
                touchpoints=touchpoints,
                conversion_events=conversion_events,
                time_to_conversion=time_to_conversion,
                total_value=total_value,
                journey_score=journey_score,
                path_analysis=path_analysis
            )
            
        except Exception as e:
            logger.error(f"Journey analysis failed for customer {customer_id}: {e}")
            raise

    def generate_journey_flow_analysis(self, timeframe_days: int = 30) -> List[JourneyFlow]:
        """Generate customer journey flow analysis (Sankey diagram data)"""
        try:
            # Get journey flow data
            flows = []
            
            # Simulate journey transitions
            stage_transitions = [
                (JourneyStage.AWARENESS, JourneyStage.CONSIDERATION, 2500, 0.65),
                (JourneyStage.CONSIDERATION, JourneyStage.PURCHASE, 1625, 0.35),
                (JourneyStage.PURCHASE, JourneyStage.ONBOARDING, 569, 0.95),
                (JourneyStage.ONBOARDING, JourneyStage.ENGAGEMENT, 540, 0.80),
                (JourneyStage.ENGAGEMENT, JourneyStage.RETENTION, 432, 0.75),
                (JourneyStage.RETENTION, JourneyStage.ADVOCACY, 324, 0.25),
                (JourneyStage.ENGAGEMENT, JourneyStage.CHURN, 108, 0.15),
                (JourneyStage.RETENTION, JourneyStage.CHURN, 65, 0.10)
            ]
            
            for source_stage, target_stage, count, conv_rate in stage_transitions:
                flow = JourneyFlow(
                    flow_id=str(uuid.uuid4()),
                    source_stage=source_stage,
                    target_stage=target_stage,
                    transition_count=count,
                    conversion_rate=conv_rate,
                    avg_time_to_transition=np.random.randint(1, 30),
                    success_factors=self._get_success_factors(source_stage, target_stage),
                    friction_points=self._get_friction_points(source_stage, target_stage)
                )
                flows.append(flow)
            
            return flows
            
        except Exception as e:
            logger.error(f"Journey flow analysis failed: {e}")
            raise

    def create_cohort_analysis(self, cohort_config: Dict[str, Any]) -> CohortMetrics:
        """Create comprehensive cohort analysis"""
        try:
            cohort_type = CohortType(cohort_config["type"])
            period_start = cohort_config.get("start_date", datetime.now() - timedelta(days=365))
            period_end = cohort_config.get("end_date", datetime.now())
            
            # Generate cohort data based on type
            if cohort_type == CohortType.ACQUISITION:
                cohort_data = self._analyze_acquisition_cohort(period_start, period_end)
            elif cohort_type == CohortType.BEHAVIORAL:
                cohort_data = self._analyze_behavioral_cohort(period_start, period_end)
            elif cohort_type == CohortType.REVENUE:
                cohort_data = self._analyze_revenue_cohort(period_start, period_end)
            else:
                cohort_data = self._analyze_engagement_cohort(period_start, period_end)
            
            return cohort_data
            
        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}")
            raise

    def generate_customer_path_analysis(self, limit: int = 100) -> Dict[str, Any]:
        """Analyze most common customer paths through the journey"""
        try:
            # Get customer journey paths
            paths = []
            path_counts = defaultdict(int)
            
            # Simulate common customer paths
            common_paths = [
                ["awareness", "consideration", "purchase", "onboarding", "engagement", "retention"],
                ["awareness", "consideration", "churn"],
                ["awareness", "purchase", "onboarding", "churn"],
                ["consideration", "purchase", "onboarding", "engagement", "advocacy"],
                ["awareness", "consideration", "purchase", "engagement", "churn"],
                ["social_media", "website", "email", "purchase", "retention"],
                ["advertising", "website", "consideration", "purchase", "advocacy"]
            ]
            
            for i, path in enumerate(common_paths):
                path_id = f"path_{i+1}"
                # Assign random counts based on path effectiveness
                count = np.random.randint(50, 500)
                path_counts[" -> ".join(path)] = count
                
                paths.append({
                    "path_id": path_id,
                    "path_sequence": path,
                    "customer_count": count,
                    "conversion_rate": np.random.uniform(0.1, 0.8),
                    "avg_journey_time": np.random.randint(1, 60),
                    "avg_touchpoints": len(path),
                    "success_score": np.random.uniform(0.3, 0.9)
                })
            
            # Sort by frequency
            paths.sort(key=lambda x: x["customer_count"], reverse=True)
            
            return {
                "total_paths_analyzed": len(paths),
                "top_paths": paths[:10],
                "path_summary": {
                    "most_common_path": paths[0]["path_sequence"] if paths else [],
                    "highest_conversion_path": max(paths, key=lambda x: x["conversion_rate"])["path_sequence"] if paths else [],
                    "fastest_path": min(paths, key=lambda x: x["avg_journey_time"])["path_sequence"] if paths else []
                },
                "path_insights": self._generate_path_insights(paths)
            }
            
        except Exception as e:
            logger.error(f"Customer path analysis failed: {e}")
            raise

    def generate_touchpoint_effectiveness_analysis(self) -> Dict[str, Any]:
        """Analyze effectiveness of different touchpoints"""
        try:
            touchpoint_data = []
            
            # Simulate touchpoint effectiveness data
            touchpoints = [
                {"type": "email_marketing", "channel": "email", "stage": "consideration"},
                {"type": "social_media_ad", "channel": "social", "stage": "awareness"},
                {"type": "website_visit", "channel": "web", "stage": "consideration"},
                {"type": "customer_service", "channel": "phone", "stage": "retention"},
                {"type": "product_demo", "channel": "web", "stage": "consideration"},
                {"type": "referral", "channel": "word_of_mouth", "stage": "awareness"},
                {"type": "retargeting_ad", "channel": "display", "stage": "consideration"},
                {"type": "newsletter", "channel": "email", "stage": "engagement"}
            ]
            
            for tp in touchpoints:
                effectiveness = {
                    "touchpoint_type": tp["type"],
                    "channel": tp["channel"],
                    "primary_stage": tp["stage"],
                    "total_interactions": np.random.randint(1000, 10000),
                    "conversion_rate": np.random.uniform(0.05, 0.35),
                    "engagement_rate": np.random.uniform(0.10, 0.80),
                    "avg_time_on_touchpoint": np.random.randint(30, 600),
                    "cost_per_interaction": np.random.uniform(0.50, 15.00),
                    "revenue_attribution": np.random.uniform(1000, 50000),
                    "customer_satisfaction": np.random.uniform(3.0, 5.0),
                    "next_action_rate": np.random.uniform(0.15, 0.70),
                    "effectiveness_score": np.random.uniform(0.4, 0.9)
                }
                touchpoint_data.append(effectiveness)
            
            # Sort by effectiveness score
            touchpoint_data.sort(key=lambda x: x["effectiveness_score"], reverse=True)
            
            return {
                "touchpoint_analysis": touchpoint_data,
                "top_performers": touchpoint_data[:3],
                "optimization_opportunities": [tp for tp in touchpoint_data if tp["effectiveness_score"] < 0.6],
                "channel_summary": self._summarize_by_channel(touchpoint_data),
                "stage_summary": self._summarize_by_stage(touchpoint_data),
                "recommendations": self._generate_touchpoint_recommendations(touchpoint_data)
            }
            
        except Exception as e:
            logger.error(f"Touchpoint effectiveness analysis failed: {e}")
            raise

    def generate_retention_heatmap_data(self, cohort_type: str = "monthly") -> Dict[str, Any]:
        """Generate retention heatmap data for visualization"""
        try:
            # Generate retention data for heatmap
            periods = 12 if cohort_type == "monthly" else 52  # 12 months or 52 weeks
            cohorts = 8  # Number of cohorts to analyze
            
            retention_matrix = []
            cohort_names = []
            
            for cohort_idx in range(cohorts):
                if cohort_type == "monthly":
                    cohort_date = datetime.now() - timedelta(days=30 * cohort_idx)
                    cohort_name = cohort_date.strftime("%Y-%m")
                else:
                    cohort_date = datetime.now() - timedelta(weeks=cohort_idx)
                    cohort_name = f"Week {cohort_date.strftime('%Y-W%U')}"
                
                cohort_names.append(cohort_name)
                
                # Generate retention rates (typically decreasing over time)
                base_retention = 0.85 - (cohort_idx * 0.05)  # Older cohorts may have different patterns
                retention_row = []
                
                for period in range(periods):
                    if period == 0:
                        retention_rate = 1.0  # 100% retention at start
                    else:
                        # Retention typically decreases over time with some volatility
                        decay_factor = 0.95 ** period
                        volatility = np.random.uniform(0.9, 1.1)
                        retention_rate = base_retention * decay_factor * volatility
                        retention_rate = max(0.05, min(1.0, retention_rate))  # Keep within bounds
                    
                    retention_row.append(round(retention_rate, 3))
                
                retention_matrix.append(retention_row)
            
            # Calculate averages and insights
            avg_retention_by_period = []
            for period in range(periods):
                period_retentions = [row[period] for row in retention_matrix if len(row) > period]
                avg_retention_by_period.append(round(np.mean(period_retentions), 3))
            
            return {
                "cohort_type": cohort_type,
                "retention_matrix": retention_matrix,
                "cohort_names": cohort_names,
                "period_labels": [f"Period {i}" for i in range(periods)],
                "avg_retention_by_period": avg_retention_by_period,
                "heatmap_config": {
                    "color_scale": ["#ff4444", "#ffaa44", "#ffff44", "#aaff44", "#44ff44"],
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "format": "percentage"
                },
                "insights": {
                    "best_performing_cohort": cohort_names[np.argmax([max(row) for row in retention_matrix])],
                    "strongest_retention_period": f"Period {np.argmax(avg_retention_by_period)}",
                    "overall_retention_trend": "declining" if avg_retention_by_period[1] > avg_retention_by_period[-1] else "stable",
                    "critical_drop_period": f"Period {np.argmax(np.diff([-r for r in avg_retention_by_period])) + 1}"
                }
            }
            
        except Exception as e:
            logger.error(f"Retention heatmap generation failed: {e}")
            raise

    # Helper methods
    def _simulate_customer_journey_data(self, customer_id: str, days_back: int) -> List[Dict[str, Any]]:
        """Simulate customer journey data for demonstration"""
        journey_events = []
        
        # Generate realistic journey progression
        stages = [
            ("awareness", "social_media", TouchpointType.SOCIAL_MEDIA),
            ("awareness", "advertising", TouchpointType.ADVERTISING), 
            ("consideration", "website", TouchpointType.WEBSITE_VISIT),
            ("consideration", "email", TouchpointType.EMAIL_OPEN),
            ("purchase", "website", TouchpointType.PURCHASE),
            ("onboarding", "email", TouchpointType.EMAIL_OPEN),
            ("engagement", "website", TouchpointType.PRODUCT_USAGE),
            ("retention", "email", TouchpointType.EMAIL_CLICK)
        ]
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i, (stage, channel, touchpoint_type) in enumerate(stages):
            event_date = start_date + timedelta(days=i * (days_back // len(stages)))
            
            journey_events.append({
                "id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "stage": stage,
                "channel": channel,
                "touchpoint_type": touchpoint_type.value,
                "timestamp": event_date,
                "value": np.random.uniform(50, 500) if touchpoint_type == TouchpointType.PURCHASE else None,
                "duration_seconds": np.random.randint(30, 600),
                "metadata": {
                    "device": np.random.choice(["desktop", "mobile", "tablet"]),
                    "location": np.random.choice(["US", "CA", "UK", "AU"])
                }
            })
        
        return journey_events

    def _determine_current_stage(self, touchpoints: List[JourneyTouchpoint]) -> JourneyStage:
        """Determine customer's current journey stage"""
        if not touchpoints:
            return JourneyStage.AWARENESS
        
        # Get the most recent touchpoint stage
        latest_touchpoint = max(touchpoints, key=lambda tp: tp.timestamp)
        return latest_touchpoint.stage

    def _calculate_journey_score(self, touchpoints: List[JourneyTouchpoint], total_value: float) -> float:
        """Calculate overall journey quality score"""
        if not touchpoints:
            return 0.0
        
        # Score based on progression, engagement, and value
        stage_progression_score = len(set(tp.stage for tp in touchpoints)) / len(JourneyStage) * 100
        engagement_score = min(100, len(touchpoints) * 5)  # 5 points per touchpoint, max 100
        value_score = min(100, total_value / 10)  # Normalize value to 0-100 scale
        
        return round((stage_progression_score + engagement_score + value_score) / 3, 2)

    def _analyze_journey_path(self, touchpoints: List[JourneyTouchpoint]) -> Dict[str, Any]:
        """Analyze customer journey path patterns"""
        if not touchpoints:
            return {}
        
        # Sort by timestamp
        sorted_touchpoints = sorted(touchpoints, key=lambda tp: tp.timestamp)
        
        # Analyze path
        path_stages = [tp.stage.value for tp in sorted_touchpoints]
        path_channels = [tp.channel for tp in sorted_touchpoints]
        path_types = [tp.touchpoint_type.value for tp in sorted_touchpoints]
        
        return {
            "path_length": len(sorted_touchpoints),
            "stage_sequence": path_stages,
            "channel_sequence": path_channels,
            "touchpoint_sequence": path_types,
            "unique_stages": len(set(path_stages)),
            "unique_channels": len(set(path_channels)),
            "journey_duration_days": (sorted_touchpoints[-1].timestamp - sorted_touchpoints[0].timestamp).days,
            "most_used_channel": Counter(path_channels).most_common(1)[0][0] if path_channels else None,
            "conversion_touchpoints": len([tp for tp in sorted_touchpoints if tp.touchpoint_type == TouchpointType.PURCHASE])
        }

    def _analyze_acquisition_cohort(self, start_date: datetime, end_date: datetime) -> CohortMetrics:
        """Analyze acquisition-based cohort"""
        cohort_size = np.random.randint(800, 2000)
        
        # Generate retention rates over time (typically declining)
        retention_periods = ["Month 0", "Month 1", "Month 3", "Month 6", "Month 12"]
        retention_rates = {
            "Month 0": 1.0,
            "Month 1": np.random.uniform(0.75, 0.90),
            "Month 3": np.random.uniform(0.55, 0.75),
            "Month 6": np.random.uniform(0.35, 0.55),
            "Month 12": np.random.uniform(0.20, 0.40)
        }
        
        return CohortMetrics(
            cohort_id=str(uuid.uuid4()),
            cohort_name=f"Acquisition Cohort {start_date.strftime('%Y-%m')}",
            cohort_type=CohortType.ACQUISITION,
            cohort_date=start_date,
            cohort_size=cohort_size,
            retention_rates=retention_rates,
            revenue_metrics={
                "total_revenue": cohort_size * np.random.uniform(50, 200),
                "avg_revenue_per_customer": np.random.uniform(50, 200),
                "revenue_growth_rate": np.random.uniform(-0.1, 0.3)
            },
            engagement_metrics={
                "avg_sessions_per_customer": np.random.uniform(5, 25),
                "avg_time_per_session": np.random.uniform(120, 600),
                "feature_adoption_rate": np.random.uniform(0.3, 0.8)
            },
            churn_analysis={
                "churn_rate": 1 - retention_rates["Month 12"],
                "primary_churn_reasons": ["price_sensitivity", "product_fit", "competition"],
                "at_risk_customers": int(cohort_size * 0.15)
            },
            lifetime_value=np.random.uniform(150, 500)
        )

    def _analyze_behavioral_cohort(self, start_date: datetime, end_date: datetime) -> CohortMetrics:
        """Analyze behavior-based cohort"""
        return self._analyze_acquisition_cohort(start_date, end_date)  # Simplified for demo

    def _analyze_revenue_cohort(self, start_date: datetime, end_date: datetime) -> CohortMetrics:
        """Analyze revenue-based cohort"""
        return self._analyze_acquisition_cohort(start_date, end_date)  # Simplified for demo

    def _analyze_engagement_cohort(self, start_date: datetime, end_date: datetime) -> CohortMetrics:
        """Analyze engagement-based cohort"""
        return self._analyze_acquisition_cohort(start_date, end_date)  # Simplified for demo

    def _get_success_factors(self, source_stage: JourneyStage, target_stage: JourneyStage) -> List[str]:
        """Get success factors for stage transitions"""
        factors_map = {
            (JourneyStage.AWARENESS, JourneyStage.CONSIDERATION): [
                "Compelling content", "Clear value proposition", "Social proof"
            ],
            (JourneyStage.CONSIDERATION, JourneyStage.PURCHASE): [
                "Product demonstrations", "Customer testimonials", "Limited-time offers"
            ],
            (JourneyStage.PURCHASE, JourneyStage.ONBOARDING): [
                "Quick setup process", "Welcome communications", "Support availability"
            ]
        }
        return factors_map.get((source_stage, target_stage), ["Personalized experience", "Timely follow-up"])

    def _get_friction_points(self, source_stage: JourneyStage, target_stage: JourneyStage) -> List[str]:
        """Get friction points for stage transitions"""
        friction_map = {
            (JourneyStage.AWARENESS, JourneyStage.CONSIDERATION): [
                "Information overload", "Unclear messaging", "Website navigation issues"
            ],
            (JourneyStage.CONSIDERATION, JourneyStage.PURCHASE): [
                "Complex checkout process", "Pricing concerns", "Trust issues"
            ],
            (JourneyStage.PURCHASE, JourneyStage.ONBOARDING): [
                "Delayed setup", "Poor documentation", "Lack of guidance"
            ]
        }
        return friction_map.get((source_stage, target_stage), ["Process complexity", "Communication gaps"])

    def _summarize_by_channel(self, touchpoint_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize touchpoint effectiveness by channel"""
        channel_summary = defaultdict(list)
        
        for tp in touchpoint_data:
            channel_summary[tp["channel"]].append(tp)
        
        summary = {}
        for channel, touchpoints in channel_summary.items():
            summary[channel] = {
                "total_touchpoints": len(touchpoints),
                "avg_effectiveness": np.mean([tp["effectiveness_score"] for tp in touchpoints]),
                "total_interactions": sum(tp["total_interactions"] for tp in touchpoints),
                "avg_conversion_rate": np.mean([tp["conversion_rate"] for tp in touchpoints])
            }
        
        return summary

    def _summarize_by_stage(self, touchpoint_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize touchpoint effectiveness by journey stage"""
        stage_summary = defaultdict(list)
        
        for tp in touchpoint_data:
            stage_summary[tp["primary_stage"]].append(tp)
        
        summary = {}
        for stage, touchpoints in stage_summary.items():
            summary[stage] = {
                "total_touchpoints": len(touchpoints),
                "avg_effectiveness": np.mean([tp["effectiveness_score"] for tp in touchpoints]),
                "best_performing": max(touchpoints, key=lambda x: x["effectiveness_score"])["touchpoint_type"]
            }
        
        return summary

    def _generate_touchpoint_recommendations(self, touchpoint_data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on touchpoint analysis"""
        recommendations = []
        
        # Find low-performing touchpoints
        low_performers = [tp for tp in touchpoint_data if tp["effectiveness_score"] < 0.6]
        if low_performers:
            recommendations.append(f"Optimize {len(low_performers)} underperforming touchpoints")
        
        # Find high-cost, low-return touchpoints
        high_cost_low_return = [tp for tp in touchpoint_data 
                               if tp["cost_per_interaction"] > 10 and tp["conversion_rate"] < 0.1]
        if high_cost_low_return:
            recommendations.append("Review budget allocation for high-cost, low-conversion touchpoints")
        
        # Find successful patterns to replicate
        top_performers = sorted(touchpoint_data, key=lambda x: x["effectiveness_score"], reverse=True)[:3]
        if top_performers:
            recommendations.append(f"Scale successful patterns from {top_performers[0]['touchpoint_type']}")
        
        return recommendations

    def _generate_path_insights(self, paths: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from path analysis"""
        insights = []
        
        if paths:
            # Most common path length
            avg_path_length = np.mean([p["avg_touchpoints"] for p in paths])
            insights.append(f"Average customer journey involves {avg_path_length:.1f} touchpoints")
            
            # Conversion rate insights
            high_conv_paths = [p for p in paths if p["conversion_rate"] > 0.5]
            if high_conv_paths:
                insights.append(f"{len(high_conv_paths)} paths show conversion rates above 50%")
            
            # Time insights
            fast_paths = [p for p in paths if p["avg_journey_time"] < 7]
            if fast_paths:
                insights.append(f"{len(fast_paths)} paths convert within a week")
        
        return insights