"""
Advanced Dynamic Segmentation Engine
"""
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
import numpy as np
from dataclasses import dataclass, asdict
from collections import defaultdict
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import silhouette_score
import pandas as pd

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class SegmentType(str, Enum):
    """Types of customer segments"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    PREDICTIVE = "predictive"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    TRANSACTIONAL = "transactional"
    ENGAGEMENT = "engagement"
    LIFECYCLE = "lifecycle"
    RFM = "rfm"
    CUSTOM = "custom"

class SegmentStatus(str, Enum):
    """Segment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    PROCESSING = "processing"

class CriteriaOperator(str, Enum):
    """Criteria operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"
    REGEX = "regex"

class LogicalOperator(str, Enum):
    """Logical operators for combining criteria"""
    AND = "and"
    OR = "or"
    NOT = "not"

class UpdateFrequency(str, Enum):
    """Segment update frequency"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MANUAL = "manual"

# Database Models
class DynamicSegment(Base):
    """Dynamic customer segment definition"""
    __tablename__ = "dynamic_segments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Segment configuration
    segment_type = Column(String, nullable=False, index=True)
    criteria = Column(JSON, nullable=False)  # Segmentation criteria
    ml_config = Column(JSON, default={})     # ML model configuration
    
    # Behavior and targeting
    target_size = Column(Integer)  # Expected segment size
    priority = Column(Integer, default=1)
    tags = Column(JSON, default=[])
    
    # Update settings
    update_frequency = Column(String, default=UpdateFrequency.DAILY.value)
    auto_update = Column(Boolean, default=True)
    last_updated = Column(DateTime)
    next_update = Column(DateTime)
    
    # Performance metrics
    current_size = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    engagement_rate = Column(Float, default=0.0)
    revenue_per_customer = Column(Float, default=0.0)
    lifetime_value = Column(Float, default=0.0)
    
    # A/B testing integration
    test_segments = Column(JSON, default=[])  # Related test segments
    performance_score = Column(Float, default=0.0)
    
    # Overlap analysis
    overlapping_segments = Column(JSON, default={})  # Overlap with other segments
    exclusion_rules = Column(JSON, default=[])       # Segments to exclude
    
    # Metadata
    status = Column(String, default=SegmentStatus.ACTIVE.value, index=True)
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    memberships = relationship("SegmentMembership", back_populates="segment")
    executions = relationship("SegmentExecution", back_populates="segment")

class SegmentMembership(Base):
    """Customer segment membership tracking"""
    __tablename__ = "segment_memberships"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String, ForeignKey("dynamic_segments.id"), index=True)
    customer_id = Column(String, index=True, nullable=False)
    
    # Membership details
    joined_at = Column(DateTime, default=datetime.now, index=True)
    left_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    
    # Membership context
    entry_reason = Column(String)  # How they entered the segment
    confidence_score = Column(Float, default=1.0)  # ML confidence
    segment_score = Column(Float)  # Customer's fit score for segment
    
    # Performance tracking
    conversions = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    engagement_events = Column(Integer, default=0)
    
    # Additional data
    additional_data = Column(JSON, default={})
    
    # Relationships
    segment = relationship("DynamicSegment", back_populates="memberships")
    
    __table_args__ = (
        Index('idx_segment_customer_active', 'segment_id', 'customer_id', 'is_active'),
        Index('idx_customer_segments', 'customer_id', 'is_active'),
    )

class SegmentExecution(Base):
    """Segment execution and processing history"""
    __tablename__ = "segment_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String, ForeignKey("dynamic_segments.id"), index=True)
    
    # Execution details
    execution_type = Column(String)  # full_refresh, incremental, manual
    trigger = Column(String)         # scheduled, manual, event_driven
    status = Column(String, index=True)
    
    # Execution metrics
    customers_processed = Column(Integer, default=0)
    customers_added = Column(Integer, default=0)
    customers_removed = Column(Integer, default=0)
    processing_time_seconds = Column(Float)
    
    # Results
    execution_results = Column(JSON, default={})
    error_messages = Column(JSON, default=[])
    warnings = Column(JSON, default=[])
    
    # Performance impact
    before_size = Column(Integer)
    after_size = Column(Integer)
    quality_score = Column(Float)  # Segment quality after execution
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.now, index=True)
    completed_at = Column(DateTime)
    
    # Relationships
    segment = relationship("DynamicSegment", back_populates="executions")

class SegmentCriteria(Base):
    """Individual segment criteria definitions"""
    __tablename__ = "segment_criteria"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String, ForeignKey("dynamic_segments.id"), index=True)
    
    # Criteria definition
    field_name = Column(String, nullable=False)
    field_type = Column(String)  # customer, behavioral, transactional, custom
    operator = Column(String, nullable=False)
    value = Column(JSON)  # Criteria value(s)
    
    # Logic
    logical_operator = Column(String, default=LogicalOperator.AND.value)
    group_id = Column(String)  # For grouping criteria
    priority = Column(Integer, default=1)
    
    # Dynamic criteria
    is_dynamic = Column(Boolean, default=False)
    time_window_days = Column(Integer)
    relative_date = Column(Boolean, default=False)
    
    # Performance
    selectivity = Column(Float)  # How selective this criteria is
    execution_time_ms = Column(Float)
    
    created_at = Column(DateTime, default=datetime.now)

@dataclass
class SegmentationResult:
    """Result of segmentation execution"""
    segment_id: str
    execution_id: str
    success: bool
    customers_processed: int
    customers_added: int
    customers_removed: int
    processing_time: float
    quality_score: float
    error_messages: List[str]
    warnings: List[str]

@dataclass
class SegmentInsight:
    """Insights about a segment"""
    insight_type: str
    title: str
    description: str
    impact: str
    confidence: float
    recommendations: List[str]
    supporting_data: Dict[str, Any]

class DynamicSegmentationEngine:
    """Advanced dynamic customer segmentation engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ml_models = {}
        self.feature_cache = {}
        
        # Configuration
        self.max_segment_size = 1000000
        self.min_segment_size = 10
        self.quality_threshold = 0.7
        self.overlap_threshold = 0.3
        
        # ML configuration
        self.feature_columns = [
            'age', 'total_purchases', 'avg_order_value', 'days_since_last_purchase',
            'total_revenue', 'engagement_score', 'support_tickets', 'referrals'
        ]
        
        # Performance tracking
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'avg_processing_time': 0.0,
            'avg_quality_score': 0.0
        }
    
    def create_dynamic_segment(self, segment_config: Dict[str, Any]) -> str:
        """Create a new dynamic segment"""
        try:
            # Validate segment configuration
            self._validate_segment_config(segment_config)
            
            # Create segment
            segment = DynamicSegment(
                name=segment_config["name"],
                description=segment_config.get("description", ""),
                segment_type=segment_config["segment_type"],
                criteria=segment_config["criteria"],
                ml_config=segment_config.get("ml_config", {}),
                target_size=segment_config.get("target_size"),
                priority=segment_config.get("priority", 1),
                tags=segment_config.get("tags", []),
                update_frequency=segment_config.get("update_frequency", UpdateFrequency.DAILY.value),
                auto_update=segment_config.get("auto_update", True),
                exclusion_rules=segment_config.get("exclusion_rules", []),
                created_by=segment_config.get("created_by", "system")
            )
            
            self.db.add(segment)
            self.db.flush()  # Get the ID
            
            # Create individual criteria records
            if "detailed_criteria" in segment_config:
                for criteria in segment_config["detailed_criteria"]:
                    self._create_segment_criteria(segment.id, criteria)
            
            # Schedule initial execution
            self._schedule_next_update(segment)
            
            self.db.commit()
            
            logger.info(f"Created dynamic segment: {segment.name} ({segment.id})")
            return segment.id
            
        except Exception as e:
            logger.error(f"Error creating dynamic segment: {e}")
            self.db.rollback()
            raise
    
    async def execute_segmentation(self, segment_id: str, execution_type: str = "scheduled") -> SegmentationResult:
        """Execute segmentation for a specific segment"""
        try:
            start_time = datetime.now()
            
            # Get segment
            segment = self.db.query(DynamicSegment).filter(
                DynamicSegment.id == segment_id
            ).first()
            
            if not segment:
                raise ValueError(f"Segment {segment_id} not found")
            
            # Create execution record
            execution = SegmentExecution(
                segment_id=segment_id,
                execution_type=execution_type,
                trigger=execution_type,
                status="running",
                before_size=segment.current_size or 0
            )
            
            self.db.add(execution)
            self.db.flush()
            
            # Set segment status
            segment.status = SegmentStatus.PROCESSING.value
            
            try:
                # Execute based on segment type
                if segment.segment_type == SegmentType.PREDICTIVE.value:
                    result = await self._execute_predictive_segmentation(segment, execution)
                elif segment.segment_type == SegmentType.BEHAVIORAL.value:
                    result = await self._execute_behavioral_segmentation(segment, execution)
                elif segment.segment_type == SegmentType.RFM.value:
                    result = await self._execute_rfm_segmentation(segment, execution)
                else:
                    result = await self._execute_criteria_based_segmentation(segment, execution)
                
                # Update segment metrics
                await self._update_segment_metrics(segment)
                
                # Calculate quality score
                quality_score = await self._calculate_segment_quality(segment_id)
                
                # Complete execution
                execution.status = "completed"
                execution.completed_at = datetime.now()
                execution.customers_processed = result.customers_processed
                execution.customers_added = result.customers_added
                execution.customers_removed = result.customers_removed
                execution.after_size = segment.current_size
                execution.quality_score = quality_score
                execution.processing_time_seconds = (datetime.now() - start_time).total_seconds()
                
                # Update segment
                segment.status = SegmentStatus.ACTIVE.value
                segment.last_updated = datetime.now()
                self._schedule_next_update(segment)
                
                self.db.commit()
                
                # Update execution stats
                self._update_execution_stats(execution)
                
                logger.info(f"Completed segmentation for {segment.name}: {result.customers_added} added, {result.customers_removed} removed")
                
                return SegmentationResult(
                    segment_id=segment_id,
                    execution_id=execution.id,
                    success=True,
                    customers_processed=result.customers_processed,
                    customers_added=result.customers_added,
                    customers_removed=result.customers_removed,
                    processing_time=execution.processing_time_seconds,
                    quality_score=quality_score,
                    error_messages=[],
                    warnings=[]
                )
                
            except Exception as e:
                # Handle execution error
                execution.status = "failed"
                execution.completed_at = datetime.now()
                execution.error_messages = [str(e)]
                execution.processing_time_seconds = (datetime.now() - start_time).total_seconds()
                
                segment.status = SegmentStatus.ACTIVE.value  # Reset status
                
                self.db.commit()
                
                raise
                
        except Exception as e:
            logger.error(f"Error executing segmentation for {segment_id}: {e}")
            self.db.rollback()
            raise
    
    def get_customer_segments(self, customer_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all segments for a customer"""
        try:
            query = self.db.query(SegmentMembership, DynamicSegment).join(
                DynamicSegment, SegmentMembership.segment_id == DynamicSegment.id
            ).filter(SegmentMembership.customer_id == customer_id)
            
            if active_only:
                query = query.filter(SegmentMembership.is_active == True)
            
            memberships = query.all()
            
            segment_data = []
            for membership, segment in memberships:
                segment_data.append({
                    "segment_id": segment.id,
                    "segment_name": segment.name,
                    "segment_type": segment.segment_type,
                    "joined_at": membership.joined_at.isoformat(),
                    "confidence_score": membership.confidence_score,
                    "segment_score": membership.segment_score,
                    "entry_reason": membership.entry_reason,
                    "performance": {
                        "conversions": membership.conversions,
                        "revenue_generated": membership.revenue_generated,
                        "engagement_events": membership.engagement_events
                    }
                })
            
            return segment_data
            
        except Exception as e:
            logger.error(f"Error getting customer segments: {e}")
            raise
    
    def get_segment_analytics(self, segment_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a segment"""
        try:
            segment = self.db.query(DynamicSegment).filter(
                DynamicSegment.id == segment_id
            ).first()
            
            if not segment:
                raise ValueError(f"Segment {segment_id} not found")
            
            # Get current memberships
            active_memberships = self.db.query(SegmentMembership).filter(
                SegmentMembership.segment_id == segment_id,
                SegmentMembership.is_active == True
            ).all()
            
            # Calculate analytics
            total_members = len(active_memberships)
            total_revenue = sum(m.revenue_generated for m in active_memberships)
            total_conversions = sum(m.conversions for m in active_memberships)
            total_engagements = sum(m.engagement_events for m in active_memberships)
            
            # Performance metrics
            avg_revenue_per_customer = total_revenue / max(1, total_members)
            conversion_rate = (total_conversions / max(1, total_members)) * 100
            engagement_rate = (total_engagements / max(1, total_members))
            
            # Membership trends
            membership_trends = self._calculate_membership_trends(segment_id)
            
            # Segment composition
            composition = self._analyze_segment_composition(active_memberships)
            
            # Overlap analysis
            overlap_analysis = self._analyze_segment_overlaps(segment_id)
            
            # Performance comparison
            performance_comparison = self._compare_segment_performance(segment_id)
            
            # Generate insights
            insights = self._generate_segment_insights(segment, active_memberships)
            
            return {
                "segment_id": segment_id,
                "segment_name": segment.name,
                "segment_type": segment.segment_type,
                "status": segment.status,
                "overview": {
                    "total_members": total_members,
                    "target_size": segment.target_size,
                    "fill_rate": (total_members / max(1, segment.target_size)) * 100 if segment.target_size else None,
                    "last_updated": segment.last_updated.isoformat() if segment.last_updated else None,
                    "update_frequency": segment.update_frequency
                },
                "performance": {
                    "total_revenue": total_revenue,
                    "avg_revenue_per_customer": avg_revenue_per_customer,
                    "total_conversions": total_conversions,
                    "conversion_rate": conversion_rate,
                    "total_engagements": total_engagements,
                    "engagement_rate": engagement_rate,
                    "lifetime_value": segment.lifetime_value,
                    "performance_score": segment.performance_score
                },
                "trends": membership_trends,
                "composition": composition,
                "overlap_analysis": overlap_analysis,
                "performance_comparison": performance_comparison,
                "insights": [asdict(insight) for insight in insights],
                "criteria": segment.criteria,
                "tags": segment.tags
            }
            
        except Exception as e:
            logger.error(f"Error getting segment analytics: {e}")
            raise
    
    def analyze_segment_overlap(self, segment_ids: List[str]) -> Dict[str, Any]:
        """Analyze overlap between multiple segments"""
        try:
            if len(segment_ids) < 2:
                return {"error": "At least 2 segments required for overlap analysis"}
            
            # Get memberships for all segments
            segment_memberships = {}
            segment_names = {}
            
            for segment_id in segment_ids:
                segment = self.db.query(DynamicSegment).filter(
                    DynamicSegment.id == segment_id
                ).first()
                
                if segment:
                    segment_names[segment_id] = segment.name
                    
                    memberships = self.db.query(SegmentMembership).filter(
                        SegmentMembership.segment_id == segment_id,
                        SegmentMembership.is_active == True
                    ).all()
                    
                    segment_memberships[segment_id] = set(m.customer_id for m in memberships)
            
            # Calculate overlaps
            overlap_matrix = {}
            for i, segment_a in enumerate(segment_ids):
                overlap_matrix[segment_a] = {}
                for j, segment_b in enumerate(segment_ids):
                    if i != j:
                        customers_a = segment_memberships.get(segment_a, set())
                        customers_b = segment_memberships.get(segment_b, set())
                        
                        intersection = customers_a.intersection(customers_b)
                        overlap_count = len(intersection)
                        overlap_percentage_a = (overlap_count / max(1, len(customers_a))) * 100
                        overlap_percentage_b = (overlap_count / max(1, len(customers_b))) * 100
                        
                        overlap_matrix[segment_a][segment_b] = {
                            "overlap_count": overlap_count,
                            "overlap_percentage_a": overlap_percentage_a,
                            "overlap_percentage_b": overlap_percentage_b,
                            "jaccard_index": overlap_count / max(1, len(customers_a.union(customers_b)))
                        }
            
            # Find common customers across all segments
            all_customers = [segment_memberships.get(sid, set()) for sid in segment_ids]
            common_customers = set.intersection(*all_customers) if all_customers else set()
            
            # Calculate segment uniqueness
            uniqueness_analysis = {}
            for segment_id in segment_ids:
                customers = segment_memberships.get(segment_id, set())
                other_customers = set()
                
                for other_id in segment_ids:
                    if other_id != segment_id:
                        other_customers.update(segment_memberships.get(other_id, set()))
                
                unique_customers = customers - other_customers
                uniqueness_percentage = (len(unique_customers) / max(1, len(customers))) * 100
                
                uniqueness_analysis[segment_id] = {
                    "unique_customers": len(unique_customers),
                    "uniqueness_percentage": uniqueness_percentage,
                    "total_customers": len(customers)
                }
            
            return {
                "segments": {sid: segment_names.get(sid, sid) for sid in segment_ids},
                "overlap_matrix": overlap_matrix,
                "common_customers": {
                    "count": len(common_customers),
                    "percentage_of_total": (len(common_customers) / max(1, len(set().union(*all_customers)))) * 100
                },
                "uniqueness_analysis": uniqueness_analysis,
                "summary": {
                    "total_segments": len(segment_ids),
                    "total_unique_customers": len(set().union(*all_customers)) if all_customers else 0,
                    "avg_overlap_percentage": np.mean([
                        overlap_matrix[a][b]["overlap_percentage_a"] 
                        for a in overlap_matrix for b in overlap_matrix[a]
                    ]) if overlap_matrix else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing segment overlap: {e}")
            raise
    
    async def create_predictive_segment(self, config: Dict[str, Any]) -> str:
        """Create ML-powered predictive segment"""
        try:
            # Prepare training data
            training_data = await self._prepare_training_data(config)
            
            # Train ML model
            model_info = await self._train_segment_model(training_data, config)
            
            # Create segment with ML configuration
            segment_config = {
                **config,
                "segment_type": SegmentType.PREDICTIVE.value,
                "ml_config": {
                    "model_type": model_info["model_type"],
                    "features": model_info["features"],
                    "model_params": model_info["params"],
                    "accuracy": model_info["accuracy"],
                    "feature_importance": model_info["feature_importance"],
                    "trained_at": datetime.now().isoformat()
                }
            }
            
            segment_id = self.create_dynamic_segment(segment_config)
            
            # Store model
            self.ml_models[segment_id] = model_info["model"]
            
            # Execute initial segmentation
            await self.execute_segmentation(segment_id, "initial")
            
            return segment_id
            
        except Exception as e:
            logger.error(f"Error creating predictive segment: {e}")
            raise
    
    # Helper methods
    async def _execute_criteria_based_segmentation(self, segment: DynamicSegment, 
                                                 execution: SegmentExecution) -> SegmentationResult:
        """Execute criteria-based segmentation"""
        try:
            # Build query from criteria
            query_conditions = self._build_query_from_criteria(segment.criteria)
            
            # Get current members
            current_members = set(
                m.customer_id for m in self.db.query(SegmentMembership).filter(
                    SegmentMembership.segment_id == segment.id,
                    SegmentMembership.is_active == True
                ).all()
            )
            
            # Execute query to get qualified customers
            from core.database import Customer
            qualified_customers = set()
            
            # This would be replaced with actual query execution
            # For now, simulate the process
            all_customers = self.db.query(Customer).all()
            for customer in all_customers:
                if self._evaluate_customer_criteria(customer, segment.criteria):
                    qualified_customers.add(customer.customer_id)
            
            # Calculate changes
            customers_to_add = qualified_customers - current_members
            customers_to_remove = current_members - qualified_customers
            
            # Apply exclusion rules
            if segment.exclusion_rules:
                customers_to_add = self._apply_exclusion_rules(customers_to_add, segment.exclusion_rules)
            
            # Apply changes
            customers_added = 0
            customers_removed = 0
            
            # Add new members
            for customer_id in customers_to_add:
                membership = SegmentMembership(
                    segment_id=segment.id,
                    customer_id=customer_id,
                    entry_reason="criteria_match",
                    confidence_score=1.0
                )
                self.db.add(membership)
                customers_added += 1
            
            # Remove old members
            for customer_id in customers_to_remove:
                memberships = self.db.query(SegmentMembership).filter(
                    SegmentMembership.segment_id == segment.id,
                    SegmentMembership.customer_id == customer_id,
                    SegmentMembership.is_active == True
                ).all()
                
                for membership in memberships:
                    membership.is_active = False
                    membership.left_at = datetime.now()
                
                customers_removed += 1
            
            # Update segment size
            segment.current_size = len(qualified_customers)
            
            return SegmentationResult(
                segment_id=segment.id,
                execution_id=execution.id,
                success=True,
                customers_processed=len(all_customers),
                customers_added=customers_added,
                customers_removed=customers_removed,
                processing_time=0.0,  # Will be set by caller
                quality_score=0.0,    # Will be calculated separately
                error_messages=[],
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Error in criteria-based segmentation: {e}")
            raise
    
    async def _execute_predictive_segmentation(self, segment: DynamicSegment, 
                                             execution: SegmentExecution) -> SegmentationResult:
        """Execute ML-powered predictive segmentation"""
        try:
            # Get or load ML model
            model = self.ml_models.get(segment.id)
            if not model:
                raise ValueError(f"ML model not found for segment {segment.id}")
            
            # Get customer features
            features_df = await self._get_customer_features()
            
            # Make predictions
            predictions = model.predict_proba(features_df[self.feature_columns])
            
            # Get customers with high probability
            threshold = segment.ml_config.get("threshold", 0.7)
            qualified_indices = np.where(predictions[:, 1] >= threshold)[0]
            
            qualified_customers = set(features_df.iloc[qualified_indices]['customer_id'].values)
            
            # Get current members
            current_members = set(
                m.customer_id for m in self.db.query(SegmentMembership).filter(
                    SegmentMembership.segment_id == segment.id,
                    SegmentMembership.is_active == True
                ).all()
            )
            
            # Calculate changes
            customers_to_add = qualified_customers - current_members
            customers_to_remove = current_members - qualified_customers
            
            # Apply changes with confidence scores
            customers_added = 0
            customers_removed = 0
            
            for customer_id in customers_to_add:
                customer_idx = features_df[features_df['customer_id'] == customer_id].index[0]
                confidence = predictions[customer_idx, 1]
                
                membership = SegmentMembership(
                    segment_id=segment.id,
                    customer_id=customer_id,
                    entry_reason="ml_prediction",
                    confidence_score=float(confidence)
                )
                self.db.add(membership)
                customers_added += 1
            
            for customer_id in customers_to_remove:
                memberships = self.db.query(SegmentMembership).filter(
                    SegmentMembership.segment_id == segment.id,
                    SegmentMembership.customer_id == customer_id,
                    SegmentMembership.is_active == True
                ).all()
                
                for membership in memberships:
                    membership.is_active = False
                    membership.left_at = datetime.now()
                
                customers_removed += 1
            
            segment.current_size = len(qualified_customers)
            
            return SegmentationResult(
                segment_id=segment.id,
                execution_id=execution.id,
                success=True,
                customers_processed=len(features_df),
                customers_added=customers_added,
                customers_removed=customers_removed,
                processing_time=0.0,
                quality_score=0.0,
                error_messages=[],
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Error in predictive segmentation: {e}")
            raise
    
    async def _execute_behavioral_segmentation(self, segment: DynamicSegment, 
                                             execution: SegmentExecution) -> SegmentationResult:
        """Execute behavioral pattern segmentation"""
        try:
            # Get behavioral data
            behavioral_data = await self._get_behavioral_features()
            
            # Apply clustering
            clustering_config = segment.ml_config.get("clustering", {})
            cluster_method = clustering_config.get("method", "kmeans")
            n_clusters = clustering_config.get("n_clusters", 5)
            
            if cluster_method == "kmeans":
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(behavioral_data[self.feature_columns])
            else:
                dbscan = DBSCAN(eps=0.5, min_samples=5)
                clusters = dbscan.fit_predict(behavioral_data[self.feature_columns])
            
            # Get target cluster
            target_cluster = segment.ml_config.get("target_cluster", 0)
            qualified_customers = set(
                behavioral_data[clusters == target_cluster]['customer_id'].values
            )
            
            # Apply similar logic as other segmentation methods
            # ... (implementation continues)
            
            return SegmentationResult(
                segment_id=segment.id,
                execution_id=execution.id,
                success=True,
                customers_processed=len(behavioral_data),
                customers_added=0,  # Would calculate actual values
                customers_removed=0,
                processing_time=0.0,
                quality_score=0.0,
                error_messages=[],
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Error in behavioral segmentation: {e}")
            raise
    
    async def _execute_rfm_segmentation(self, segment: DynamicSegment, 
                                      execution: SegmentExecution) -> SegmentationResult:
        """Execute RFM (Recency, Frequency, Monetary) segmentation"""
        try:
            # Calculate RFM scores
            rfm_data = await self._calculate_rfm_scores()
            
            # Define RFM segment criteria
            rfm_criteria = segment.criteria.get("rfm_criteria", {})
            min_recency = rfm_criteria.get("min_recency_score", 0)
            min_frequency = rfm_criteria.get("min_frequency_score", 0)
            min_monetary = rfm_criteria.get("min_monetary_score", 0)
            
            # Filter customers based on RFM criteria
            qualified_mask = (
                (rfm_data['recency_score'] >= min_recency) &
                (rfm_data['frequency_score'] >= min_frequency) &
                (rfm_data['monetary_score'] >= min_monetary)
            )
            
            qualified_customers = set(rfm_data[qualified_mask]['customer_id'].values)
            
            # Apply similar logic for membership updates
            # ... (implementation continues)
            
            return SegmentationResult(
                segment_id=segment.id,
                execution_id=execution.id,
                success=True,
                customers_processed=len(rfm_data),
                customers_added=0,  # Would calculate actual values
                customers_removed=0,
                processing_time=0.0,
                quality_score=0.0,
                error_messages=[],
                warnings=[]
            )
            
        except Exception as e:
            logger.error(f"Error in RFM segmentation: {e}")
            raise
    
    def _validate_segment_config(self, config: Dict[str, Any]):
        """Validate segment configuration"""
        required_fields = ["name", "segment_type", "criteria"]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate segment type
        if config["segment_type"] not in [t.value for t in SegmentType]:
            raise ValueError(f"Invalid segment type: {config['segment_type']}")
        
        # Validate criteria structure
        if not isinstance(config["criteria"], dict):
            raise ValueError("Criteria must be a dictionary")
    
    def _build_query_from_criteria(self, criteria: Dict[str, Any]) -> str:
        """Build SQL query from criteria (simplified implementation)"""
        # This would build an actual SQL query from the criteria
        # For now, return a placeholder
        return "SELECT customer_id FROM customers WHERE 1=1"
    
    def _evaluate_customer_criteria(self, customer, criteria: Dict[str, Any]) -> bool:
        """Evaluate if customer matches criteria (simplified implementation)"""
        # This would evaluate the customer against the criteria
        # For now, return True for demonstration
        return True
    
    def _apply_exclusion_rules(self, customers: set, exclusion_rules: List[Dict[str, Any]]) -> set:
        """Apply exclusion rules to customer set"""
        filtered_customers = customers.copy()
        
        for rule in exclusion_rules:
            if rule.get("type") == "segment":
                excluded_segment_id = rule.get("segment_id")
                if excluded_segment_id:
                    excluded_customers = set(
                        m.customer_id for m in self.db.query(SegmentMembership).filter(
                            SegmentMembership.segment_id == excluded_segment_id,
                            SegmentMembership.is_active == True
                        ).all()
                    )
                    filtered_customers -= excluded_customers
        
        return filtered_customers
    
    async def _update_segment_metrics(self, segment: DynamicSegment):
        """Update segment performance metrics"""
        try:
            # Get active memberships
            memberships = self.db.query(SegmentMembership).filter(
                SegmentMembership.segment_id == segment.id,
                SegmentMembership.is_active == True
            ).all()
            
            if memberships:
                # Calculate metrics
                total_revenue = sum(m.revenue_generated for m in memberships)
                total_conversions = sum(m.conversions for m in memberships)
                total_engagements = sum(m.engagement_events for m in memberships)
                
                segment.conversion_rate = (total_conversions / len(memberships)) * 100
                segment.engagement_rate = total_engagements / len(memberships)
                segment.revenue_per_customer = total_revenue / len(memberships)
                segment.lifetime_value = total_revenue / len(memberships)  # Simplified LTV
            
        except Exception as e:
            logger.error(f"Error updating segment metrics: {e}")
    
    async def _calculate_segment_quality(self, segment_id: str) -> float:
        """Calculate segment quality score"""
        try:
            # Get segment and memberships
            segment = self.db.query(DynamicSegment).filter(
                DynamicSegment.id == segment_id
            ).first()
            
            if not segment:
                return 0.0
            
            memberships = self.db.query(SegmentMembership).filter(
                SegmentMembership.segment_id == segment_id,
                SegmentMembership.is_active == True
            ).all()
            
            if not memberships:
                return 0.0
            
            # Quality factors
            size_score = min(1.0, len(memberships) / max(1, segment.target_size)) if segment.target_size else 1.0
            
            confidence_score = sum(m.confidence_score for m in memberships) / len(memberships)
            
            performance_score = min(1.0, segment.conversion_rate / 10) if segment.conversion_rate else 0.0
            
            # Weighted quality score
            quality_score = (size_score * 0.3 + confidence_score * 0.4 + performance_score * 0.3) * 100
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating segment quality: {e}")
            return 0.0
    
    def _schedule_next_update(self, segment: DynamicSegment):
        """Schedule next segment update"""
        try:
            if not segment.auto_update:
                return
            
            frequency_mapping = {
                UpdateFrequency.HOURLY.value: timedelta(hours=1),
                UpdateFrequency.DAILY.value: timedelta(days=1),
                UpdateFrequency.WEEKLY.value: timedelta(weeks=1),
                UpdateFrequency.MONTHLY.value: timedelta(days=30)
            }
            
            interval = frequency_mapping.get(segment.update_frequency, timedelta(days=1))
            segment.next_update = datetime.now() + interval
            
        except Exception as e:
            logger.error(f"Error scheduling next update: {e}")
    
    def _update_execution_stats(self, execution: SegmentExecution):
        """Update global execution statistics"""
        try:
            self.execution_stats['total_executions'] += 1
            
            if execution.status == "completed":
                self.execution_stats['successful_executions'] += 1
                
                # Update averages
                current_avg_time = self.execution_stats['avg_processing_time']
                new_time = execution.processing_time_seconds
                total_successful = self.execution_stats['successful_executions']
                
                self.execution_stats['avg_processing_time'] = (
                    (current_avg_time * (total_successful - 1) + new_time) / total_successful
                )
                
                if execution.quality_score:
                    current_avg_quality = self.execution_stats['avg_quality_score']
                    self.execution_stats['avg_quality_score'] = (
                        (current_avg_quality * (total_successful - 1) + execution.quality_score) / total_successful
                    )
            
        except Exception as e:
            logger.error(f"Error updating execution stats: {e}")
    
    # Additional helper methods for analytics, ML training, etc. would continue here...
    # (Due to length constraints, including key methods only)
    
    async def _prepare_training_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        """Prepare training data for ML model"""
        # Placeholder implementation
        return pd.DataFrame()
    
    async def _train_segment_model(self, training_data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Train ML model for predictive segmentation"""
        # Placeholder implementation
        return {
            "model": None,
            "model_type": "random_forest",
            "features": self.feature_columns,
            "params": {},
            "accuracy": 0.85,
            "feature_importance": {}
        }
    
    async def _get_customer_features(self) -> pd.DataFrame:
        """Get customer feature matrix"""
        # Placeholder implementation
        return pd.DataFrame()
    
    async def _get_behavioral_features(self) -> pd.DataFrame:
        """Get behavioral feature matrix"""
        # Placeholder implementation
        return pd.DataFrame()
    
    async def _calculate_rfm_scores(self) -> pd.DataFrame:
        """Calculate RFM scores for all customers"""
        # Placeholder implementation
        return pd.DataFrame()
    
    def _calculate_membership_trends(self, segment_id: str) -> Dict[str, Any]:
        """Calculate membership trends over time"""
        # Placeholder implementation
        return {}
    
    def _analyze_segment_composition(self, memberships: List) -> Dict[str, Any]:
        """Analyze segment composition"""
        # Placeholder implementation
        return {}
    
    def _analyze_segment_overlaps(self, segment_id: str) -> Dict[str, Any]:
        """Analyze overlaps with other segments"""
        # Placeholder implementation
        return {}
    
    def _compare_segment_performance(self, segment_id: str) -> Dict[str, Any]:
        """Compare segment performance with others"""
        # Placeholder implementation
        return {}
    
    def _generate_segment_insights(self, segment: DynamicSegment, memberships: List) -> List[SegmentInsight]:
        """Generate actionable insights for segment"""
        insights = []
        
        try:
            # Size insights
            if segment.current_size and segment.target_size:
                fill_rate = (segment.current_size / segment.target_size) * 100
                if fill_rate < 50:
                    insights.append(SegmentInsight(
                        insight_type="size",
                        title="Low Segment Fill Rate",
                        description=f"Segment is only {fill_rate:.1f}% filled",
                        impact="medium",
                        confidence=0.9,
                        recommendations=[
                            "Review and relax segment criteria",
                            "Expand target market definition",
                            "Consider predictive expansion"
                        ],
                        supporting_data={"fill_rate": fill_rate, "current_size": segment.current_size}
                    ))
            
            # Performance insights
            if segment.conversion_rate and segment.conversion_rate > 15:
                insights.append(SegmentInsight(
                    insight_type="performance",
                    title="High Converting Segment",
                    description="This segment shows exceptional conversion performance",
                    impact="high",
                    confidence=0.8,
                    recommendations=[
                        "Increase marketing budget allocation",
                        "Create lookalike segments",
                        "Expand targeting criteria"
                    ],
                    supporting_data={"conversion_rate": segment.conversion_rate}
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating segment insights: {e}")
            return []
    
    def _create_segment_criteria(self, segment_id: str, criteria: Dict[str, Any]):
        """Create individual segment criteria record"""
        try:
            segment_criteria = SegmentCriteria(
                segment_id=segment_id,
                field_name=criteria["field_name"],
                field_type=criteria.get("field_type", "customer"),
                operator=criteria["operator"],
                value=criteria["value"],
                logical_operator=criteria.get("logical_operator", LogicalOperator.AND.value),
                group_id=criteria.get("group_id"),
                priority=criteria.get("priority", 1),
                is_dynamic=criteria.get("is_dynamic", False),
                time_window_days=criteria.get("time_window_days"),
                relative_date=criteria.get("relative_date", False)
            )
            
            self.db.add(segment_criteria)
            
        except Exception as e:
            logger.error(f"Error creating segment criteria: {e}")
            raise