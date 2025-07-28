"""
A/B Testing Framework for Campaign and Experience Optimization
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
import hashlib
import numpy as np
from scipy import stats
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass
import math

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class ExperimentStatus(str, Enum):
    """Experiment status types"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ExperimentType(str, Enum):
    """Types of experiments"""
    EMAIL_CAMPAIGN = "email_campaign"
    WEBSITE_EXPERIENCE = "website_experience"
    MOBILE_APP = "mobile_app"
    PRICING = "pricing"
    PRODUCT_FEATURE = "product_feature"
    MESSAGING = "messaging"
    UI_UX = "ui_ux"

class MetricType(str, Enum):
    """Types of success metrics"""
    CONVERSION_RATE = "conversion_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    OPEN_RATE = "open_rate"
    REVENUE = "revenue"
    ENGAGEMENT_TIME = "engagement_time"
    BOUNCE_RATE = "bounce_rate"
    PURCHASE_VALUE = "purchase_value"
    SIGNUP_RATE = "signup_rate"

class StatisticalTest(str, Enum):
    """Statistical test types"""
    T_TEST = "t_test"
    CHI_SQUARE = "chi_square"
    MANN_WHITNEY = "mann_whitney"
    PROPORTIONS_TEST = "proportions_test"

# Database Models
class Experiment(Base):
    """A/B test experiment"""
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    experiment_type = Column(String, nullable=False)
    status = Column(String, default=ExperimentStatus.DRAFT.value)
    
    # Experiment configuration
    hypothesis = Column(Text)
    variants = Column(JSON, nullable=False)  # List of variant configurations
    traffic_allocation = Column(JSON, nullable=False)  # Percentage allocation per variant
    target_audience = Column(JSON)  # Segmentation criteria
    
    # Success metrics
    primary_metric = Column(String, nullable=False)
    secondary_metrics = Column(JSON, default=[])
    success_criteria = Column(JSON)  # Statistical significance, minimum effect size
    
    # Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_days = Column(Integer)
    
    # Results
    statistical_results = Column(JSON, default={})
    winner_variant = Column(String)
    confidence_level = Column(Float)
    
    # Metadata
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    assignments = relationship("ExperimentAssignment", back_populates="experiment")
    conversions = relationship("ExperimentConversion", back_populates="experiment")

class ExperimentAssignment(Base):
    """Customer assignment to experiment variants"""
    __tablename__ = "experiment_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, ForeignKey("experiments.id"), index=True)
    customer_id = Column(String, index=True)
    variant_id = Column(String, index=True)
    assigned_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="assignments")

class ExperimentConversion(Base):
    """Conversion events for experiments"""
    __tablename__ = "experiment_conversions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, ForeignKey("experiments.id"), index=True)
    customer_id = Column(String, index=True)
    variant_id = Column(String, index=True)
    metric_type = Column(String)
    metric_value = Column(Float)
    conversion_data = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="conversions")

@dataclass
class ExperimentResult:
    """Experiment analysis result"""
    experiment_id: str
    status: str
    statistical_significance: bool
    confidence_level: float
    p_value: float
    effect_size: float
    winner_variant: Optional[str]
    variant_results: Dict[str, Any]
    recommendations: List[str]

@dataclass
class VariantPerformance:
    """Individual variant performance metrics"""
    variant_id: str
    sample_size: int
    conversion_rate: float
    average_value: float
    confidence_interval: Tuple[float, float]
    standard_error: float

class ABTestingFramework:
    """Comprehensive A/B testing framework"""
    
    def __init__(self, db: Session):
        self.db = db
        self.default_confidence_level = 0.95
        self.minimum_sample_size = 100
        self.minimum_effect_size = 0.05  # 5% minimum detectable effect
    
    def create_experiment(self, experiment_config: Dict[str, Any]) -> str:
        """Create a new A/B test experiment"""
        try:
            # Validate experiment configuration
            self._validate_experiment_config(experiment_config)
            
            # Calculate sample size requirements
            sample_size_info = self._calculate_sample_size(
                experiment_config.get("expected_effect_size", self.minimum_effect_size),
                experiment_config.get("statistical_power", 0.8),
                experiment_config.get("confidence_level", self.default_confidence_level)
            )
            
            experiment = Experiment(
                name=experiment_config["name"],
                description=experiment_config.get("description", ""),
                experiment_type=experiment_config["experiment_type"],
                hypothesis=experiment_config.get("hypothesis", ""),
                variants=experiment_config["variants"],
                traffic_allocation=experiment_config["traffic_allocation"],
                target_audience=experiment_config.get("target_audience", {}),
                primary_metric=experiment_config["primary_metric"],
                secondary_metrics=experiment_config.get("secondary_metrics", []),
                success_criteria={
                    "confidence_level": experiment_config.get("confidence_level", self.default_confidence_level),
                    "minimum_effect_size": experiment_config.get("expected_effect_size", self.minimum_effect_size),
                    "minimum_sample_size": sample_size_info["required_sample_size"],
                    "statistical_power": experiment_config.get("statistical_power", 0.8)
                },
                duration_days=experiment_config.get("duration_days", 14),
                created_by=experiment_config.get("created_by", "system")
            )
            
            self.db.add(experiment)
            self.db.commit()
            
            logger.info(f"Created experiment: {experiment.name} ({experiment.id})")
            return experiment.id
            
        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            self.db.rollback()
            raise
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an A/B test experiment"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            if experiment.status != ExperimentStatus.DRAFT.value:
                raise ValueError(f"Experiment must be in draft status to start")
            
            experiment.status = ExperimentStatus.RUNNING.value
            experiment.start_date = datetime.now()
            
            if experiment.duration_days:
                experiment.end_date = experiment.start_date + timedelta(days=experiment.duration_days)
            
            self.db.commit()
            
            logger.info(f"Started experiment: {experiment.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting experiment: {e}")
            self.db.rollback()
            return False
    
    def assign_variant(self, experiment_id: str, customer_id: str) -> str:
        """Assign customer to experiment variant"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment or experiment.status != ExperimentStatus.RUNNING.value:
                return None
            
            # Check if customer already assigned
            existing_assignment = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id,
                ExperimentAssignment.customer_id == customer_id
            ).first()
            
            if existing_assignment:
                return existing_assignment.variant_id
            
            # Check if customer matches target audience
            if not self._customer_matches_audience(customer_id, experiment.target_audience):
                return None
            
            # Assign variant using consistent hashing
            variant_id = self._hash_assign_variant(customer_id, experiment.traffic_allocation)
            
            # Record assignment
            assignment = ExperimentAssignment(
                experiment_id=experiment_id,
                customer_id=customer_id,
                variant_id=variant_id
            )
            
            self.db.add(assignment)
            self.db.commit()
            
            return variant_id
            
        except Exception as e:
            logger.error(f"Error assigning variant: {e}")
            self.db.rollback()
            return None
    
    def track_conversion(self, experiment_id: str, customer_id: str,
                        metric_type: str, metric_value: float,
                        conversion_data: Dict[str, Any] = None) -> bool:
        """Track conversion event for experiment"""
        try:
            # Get customer's variant assignment
            assignment = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id,
                ExperimentAssignment.customer_id == customer_id
            ).first()
            
            if not assignment:
                # Customer not in experiment
                return False
            
            # Record conversion
            conversion = ExperimentConversion(
                experiment_id=experiment_id,
                customer_id=customer_id,
                variant_id=assignment.variant_id,
                metric_type=metric_type,
                metric_value=metric_value,
                conversion_data=conversion_data or {}
            )
            
            self.db.add(conversion)
            self.db.commit()
            
            # Check if we should analyze results
            self._check_analysis_triggers(experiment_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            self.db.rollback()
            return False
    
    def analyze_experiment(self, experiment_id: str) -> ExperimentResult:
        """Analyze experiment results and determine statistical significance"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            # Get all conversions
            conversions = self.db.query(ExperimentConversion).filter(
                ExperimentConversion.experiment_id == experiment_id
            ).all()
            
            # Get all assignments
            assignments = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id
            ).all()
            
            if not conversions or not assignments:
                return ExperimentResult(
                    experiment_id=experiment_id,
                    status="insufficient_data",
                    statistical_significance=False,
                    confidence_level=0.0,
                    p_value=1.0,
                    effect_size=0.0,
                    winner_variant=None,
                    variant_results={},
                    recommendations=["Collect more data before analysis"]
                )
            
            # Analyze each variant
            variant_results = {}
            variant_performances = []
            
            for variant in experiment.variants:
                variant_id = variant["id"]
                performance = self._analyze_variant_performance(
                    experiment_id, variant_id, experiment.primary_metric
                )
                variant_results[variant_id] = performance.__dict__
                variant_performances.append(performance)
            
            # Perform statistical test
            statistical_result = self._perform_statistical_test(
                variant_performances, experiment.primary_metric
            )
            
            # Determine winner
            winner_variant = None
            if statistical_result["significant"]:
                winner_variant = max(
                    variant_performances,
                    key=lambda v: v.conversion_rate if experiment.primary_metric == MetricType.CONVERSION_RATE.value else v.average_value
                ).variant_id
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                statistical_result, variant_performances, experiment
            )
            
            # Update experiment with results
            experiment.statistical_results = statistical_result
            experiment.winner_variant = winner_variant
            experiment.confidence_level = statistical_result.get("confidence", 0.0)
            
            self.db.commit()
            
            return ExperimentResult(
                experiment_id=experiment_id,
                status="analyzed",
                statistical_significance=statistical_result["significant"],
                confidence_level=statistical_result.get("confidence", 0.0),
                p_value=statistical_result.get("p_value", 1.0),
                effect_size=statistical_result.get("effect_size", 0.0),
                winner_variant=winner_variant,
                variant_results=variant_results,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing experiment: {e}")
            raise
    
    def get_experiment_dashboard(self, experiment_id: str) -> Dict[str, Any]:
        """Get real-time experiment dashboard data"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment:
                return {"error": "Experiment not found"}
            
            # Get basic metrics
            total_assignments = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id
            ).count()
            
            total_conversions = self.db.query(ExperimentConversion).filter(
                ExperimentConversion.experiment_id == experiment_id
            ).count()
            
            # Get variant breakdown
            variant_breakdown = {}
            for variant in experiment.variants:
                variant_id = variant["id"]
                
                variant_assignments = self.db.query(ExperimentAssignment).filter(
                    ExperimentAssignment.experiment_id == experiment_id,
                    ExperimentAssignment.variant_id == variant_id
                ).count()
                
                variant_conversions = self.db.query(ExperimentConversion).filter(
                    ExperimentConversion.experiment_id == experiment_id,
                    ExperimentConversion.variant_id == variant_id
                ).count()
                
                conversion_rate = (variant_conversions / variant_assignments * 100) if variant_assignments > 0 else 0
                
                variant_breakdown[variant_id] = {
                    "name": variant.get("name", f"Variant {variant_id}"),
                    "assignments": variant_assignments,
                    "conversions": variant_conversions,
                    "conversion_rate": conversion_rate,
                    "traffic_allocation": experiment.traffic_allocation.get(variant_id, 0)
                }
            
            # Calculate experiment progress
            days_running = 0
            progress_percentage = 0
            
            if experiment.start_date:
                days_running = (datetime.now() - experiment.start_date).days
                if experiment.duration_days:
                    progress_percentage = min(100, (days_running / experiment.duration_days) * 100)
            
            # Check if minimum sample size reached
            min_sample_size = experiment.success_criteria.get("minimum_sample_size", self.minimum_sample_size)
            sample_size_reached = total_assignments >= min_sample_size
            
            return {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "status": experiment.status,
                "experiment_type": experiment.experiment_type,
                "primary_metric": experiment.primary_metric,
                "progress": {
                    "days_running": days_running,
                    "progress_percentage": progress_percentage,
                    "duration_days": experiment.duration_days
                },
                "traffic": {
                    "total_assignments": total_assignments,
                    "total_conversions": total_conversions,
                    "overall_conversion_rate": (total_conversions / total_assignments * 100) if total_assignments > 0 else 0
                },
                "variants": variant_breakdown,
                "statistical_power": {
                    "minimum_sample_size": min_sample_size,
                    "sample_size_reached": sample_size_reached,
                    "current_power": self._estimate_statistical_power(total_assignments, min_sample_size)
                },
                "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "winner_variant": experiment.winner_variant,
                "confidence_level": experiment.confidence_level
            }
            
        except Exception as e:
            logger.error(f"Error getting experiment dashboard: {e}")
            raise
    
    def stop_experiment(self, experiment_id: str, reason: str = "manual_stop") -> bool:
        """Stop a running experiment"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            if experiment.status != ExperimentStatus.RUNNING.value:
                raise ValueError("Experiment is not running")
            
            experiment.status = ExperimentStatus.COMPLETED.value
            experiment.end_date = datetime.now()
            
            # Perform final analysis
            try:
                final_result = self.analyze_experiment(experiment_id)
                logger.info(f"Final analysis completed for experiment {experiment_id}")
            except Exception as e:
                logger.error(f"Error in final analysis: {e}")
            
            self.db.commit()
            
            logger.info(f"Stopped experiment: {experiment.name} - Reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping experiment: {e}")
            self.db.rollback()
            return False
    
    # Helper methods
    def _validate_experiment_config(self, config: Dict[str, Any]):
        """Validate experiment configuration"""
        required_fields = ["name", "experiment_type", "variants", "traffic_allocation", "primary_metric"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate variants
        variants = config["variants"]
        if not isinstance(variants, list) or len(variants) < 2:
            raise ValueError("At least 2 variants required")
        
        # Validate traffic allocation
        allocation = config["traffic_allocation"]
        if not isinstance(allocation, dict):
            raise ValueError("Traffic allocation must be a dictionary")
        
        total_allocation = sum(allocation.values())
        if not (99 <= total_allocation <= 101):  # Allow for rounding
            raise ValueError("Traffic allocation must sum to 100%")
    
    def _calculate_sample_size(self, effect_size: float, power: float, alpha: float) -> Dict[str, Any]:
        """Calculate required sample size for experiment"""
        try:
            # Using simplified calculation for proportion tests
            z_alpha = stats.norm.ppf(1 - alpha/2)
            z_beta = stats.norm.ppf(power)
            
            # Assume baseline conversion rate of 10% if not provided
            p1 = 0.10
            p2 = p1 * (1 + effect_size)
            
            pooled_p = (p1 + p2) / 2
            
            n = (2 * pooled_p * (1 - pooled_p) * (z_alpha + z_beta)**2) / (p2 - p1)**2
            
            return {
                "required_sample_size": int(math.ceil(n)),
                "per_variant": int(math.ceil(n / 2)),
                "assumptions": {
                    "baseline_rate": p1,
                    "target_rate": p2,
                    "effect_size": effect_size,
                    "power": power,
                    "alpha": alpha
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating sample size: {e}")
            return {"required_sample_size": self.minimum_sample_size}
    
    def _customer_matches_audience(self, customer_id: str, audience_criteria: Dict[str, Any]) -> bool:
        """Check if customer matches target audience criteria"""
        if not audience_criteria:
            return True
        
        try:
            # Get customer data
            from core.database import Customer
            customer = self.db.query(Customer).filter(
                Customer.customer_id == customer_id
            ).first()
            
            if not customer:
                return False
            
            # Check criteria
            for field, criteria in audience_criteria.items():
                customer_value = getattr(customer, field, None)
                if customer_value is None:
                    return False
                
                if isinstance(criteria, dict):
                    operator = criteria.get("operator", "equals")
                    value = criteria.get("value")
                    
                    if operator == "equals" and customer_value != value:
                        return False
                    elif operator == "greater_than" and customer_value <= value:
                        return False
                    elif operator == "less_than" and customer_value >= value:
                        return False
                    elif operator == "in" and customer_value not in value:
                        return False
                else:
                    if customer_value != criteria:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking audience match: {e}")
            return False
    
    def _hash_assign_variant(self, customer_id: str, traffic_allocation: Dict[str, float]) -> str:
        """Assign variant using consistent hashing"""
        try:
            # Create hash of customer ID
            hash_value = int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)
            hash_percentage = (hash_value % 10000) / 100  # 0-99.99
            
            # Assign based on traffic allocation
            cumulative = 0
            for variant_id, allocation in traffic_allocation.items():
                cumulative += allocation
                if hash_percentage <= cumulative:
                    return variant_id
            
            # Fallback to first variant
            return list(traffic_allocation.keys())[0]
            
        except Exception as e:
            logger.error(f"Error in hash assignment: {e}")
            return list(traffic_allocation.keys())[0]
    
    def _analyze_variant_performance(self, experiment_id: str, variant_id: str, 
                                   metric_type: str) -> VariantPerformance:
        """Analyze performance metrics for a specific variant"""
        try:
            # Get assignments for variant
            assignments = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id,
                ExperimentAssignment.variant_id == variant_id
            ).count()
            
            # Get conversions for variant
            conversions = self.db.query(ExperimentConversion).filter(
                ExperimentConversion.experiment_id == experiment_id,
                ExperimentConversion.variant_id == variant_id,
                ExperimentConversion.metric_type == metric_type
            ).all()
            
            # Calculate metrics
            conversion_count = len(conversions)
            conversion_rate = (conversion_count / assignments) if assignments > 0 else 0
            
            if conversions:
                values = [c.metric_value for c in conversions]
                average_value = np.mean(values)
                std_dev = np.std(values)
            else:
                average_value = 0
                std_dev = 0
            
            # Calculate confidence interval
            if assignments > 1 and conversion_rate > 0:
                se = np.sqrt((conversion_rate * (1 - conversion_rate)) / assignments)
                margin_error = 1.96 * se  # 95% confidence interval
                ci_lower = max(0, conversion_rate - margin_error)
                ci_upper = min(1, conversion_rate + margin_error)
            else:
                se = 0
                ci_lower = conversion_rate
                ci_upper = conversion_rate
            
            return VariantPerformance(
                variant_id=variant_id,
                sample_size=assignments,
                conversion_rate=conversion_rate,
                average_value=average_value,
                confidence_interval=(ci_lower, ci_upper),
                standard_error=se
            )
            
        except Exception as e:
            logger.error(f"Error analyzing variant performance: {e}")
            return VariantPerformance(
                variant_id=variant_id,
                sample_size=0,
                conversion_rate=0,
                average_value=0,
                confidence_interval=(0, 0),
                standard_error=0
            )
    
    def _perform_statistical_test(self, variant_performances: List[VariantPerformance], 
                                 metric_type: str) -> Dict[str, Any]:
        """Perform appropriate statistical test"""
        try:
            if len(variant_performances) != 2:
                return {"significant": False, "p_value": 1.0, "test_type": "insufficient_variants"}
            
            var1, var2 = variant_performances
            
            # Check minimum sample size
            if var1.sample_size < self.minimum_sample_size or var2.sample_size < self.minimum_sample_size:
                return {
                    "significant": False,
                    "p_value": 1.0,
                    "test_type": "insufficient_sample_size",
                    "message": f"Minimum sample size: {self.minimum_sample_size}"
                }
            
            # Proportion test for conversion rates
            if metric_type in [MetricType.CONVERSION_RATE.value, MetricType.CLICK_THROUGH_RATE.value]:
                # Two-proportion z-test
                count1 = int(var1.conversion_rate * var1.sample_size)
                count2 = int(var2.conversion_rate * var2.sample_size)
                
                pooled_p = (count1 + count2) / (var1.sample_size + var2.sample_size)
                se = np.sqrt(pooled_p * (1 - pooled_p) * (1/var1.sample_size + 1/var2.sample_size))
                
                if se > 0:
                    z_score = (var1.conversion_rate - var2.conversion_rate) / se
                    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
                else:
                    p_value = 1.0
                
                effect_size = abs(var1.conversion_rate - var2.conversion_rate)
                
                return {
                    "significant": p_value < 0.05,
                    "p_value": p_value,
                    "z_score": z_score if 'z_score' in locals() else 0,
                    "effect_size": effect_size,
                    "test_type": "proportions_test",
                    "confidence": 1 - p_value if p_value < 0.05 else 0
                }
            
            # T-test for continuous metrics
            else:
                # Welch's t-test (unequal variances)
                try:
                    t_stat, p_value = stats.ttest_ind_from_stats(
                        var1.average_value, var1.standard_error * np.sqrt(var1.sample_size), var1.sample_size,
                        var2.average_value, var2.standard_error * np.sqrt(var2.sample_size), var2.sample_size,
                        equal_var=False
                    )
                    
                    effect_size = abs(var1.average_value - var2.average_value)
                    
                    return {
                        "significant": p_value < 0.05,
                        "p_value": p_value,
                        "t_statistic": t_stat,
                        "effect_size": effect_size,
                        "test_type": "t_test",
                        "confidence": 1 - p_value if p_value < 0.05 else 0
                    }
                    
                except Exception as t_error:
                    logger.error(f"T-test error: {t_error}")
                    return {"significant": False, "p_value": 1.0, "test_type": "t_test_failed"}
            
        except Exception as e:
            logger.error(f"Error performing statistical test: {e}")
            return {"significant": False, "p_value": 1.0, "test_type": "error", "error": str(e)}
    
    def _generate_recommendations(self, statistical_result: Dict[str, Any], 
                                variant_performances: List[VariantPerformance],
                                experiment) -> List[str]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        
        if not statistical_result.get("significant", False):
            recommendations.append("No statistically significant difference detected")
            
            # Check sample size
            total_sample = sum(v.sample_size for v in variant_performances)
            min_required = experiment.success_criteria.get("minimum_sample_size", self.minimum_sample_size)
            
            if total_sample < min_required:
                recommendations.append(f"Increase sample size to at least {min_required} for reliable results")
            else:
                recommendations.append("Consider testing larger effect sizes or longer duration")
        
        else:
            # Significant result
            best_variant = max(variant_performances, key=lambda v: v.conversion_rate)
            recommendations.append(f"Implement variant {best_variant.variant_id} as the winner")
            
            effect_size = statistical_result.get("effect_size", 0)
            if effect_size > 0.1:
                recommendations.append("Large effect size detected - high impact change")
            elif effect_size > 0.05:
                recommendations.append("Medium effect size - moderate impact expected")
            else:
                recommendations.append("Small effect size - monitor long-term impact")
        
        # General recommendations
        if len(variant_performances) == 2:
            performance_gap = abs(variant_performances[0].conversion_rate - variant_performances[1].conversion_rate)
            if performance_gap > 0.2:
                recommendations.append("Large performance gap - consider immediate implementation")
        
        return recommendations
    
    def _check_analysis_triggers(self, experiment_id: str):
        """Check if experiment should trigger automatic analysis"""
        try:
            experiment = self.db.query(Experiment).filter(
                Experiment.id == experiment_id
            ).first()
            
            if not experiment or experiment.status != ExperimentStatus.RUNNING.value:
                return
            
            # Check if minimum sample size reached
            total_assignments = self.db.query(ExperimentAssignment).filter(
                ExperimentAssignment.experiment_id == experiment_id
            ).count()
            
            min_sample_size = experiment.success_criteria.get("minimum_sample_size", self.minimum_sample_size)
            
            if total_assignments >= min_sample_size:
                # Run analysis
                try:
                    result = self.analyze_experiment(experiment_id)
                    
                    # Auto-stop if significant and sufficient sample
                    if result.statistical_significance and total_assignments >= min_sample_size * 1.5:
                        logger.info(f"Auto-stopping experiment {experiment_id} due to significant results")
                        # Could implement auto-stop logic here
                        
                except Exception as e:
                    logger.error(f"Error in automatic analysis: {e}")
            
        except Exception as e:
            logger.error(f"Error checking analysis triggers: {e}")
    
    def _estimate_statistical_power(self, current_sample: int, required_sample: int) -> float:
        """Estimate current statistical power"""
        if current_sample >= required_sample:
            return 0.8  # Target power level
        else:
            # Linear approximation
            return min(0.8, (current_sample / required_sample) * 0.8)