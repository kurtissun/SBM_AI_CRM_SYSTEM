"""
Customer Data Platform (CDP) - Unified Customer Profile System
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import hashlib
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class IdentityType(str, Enum):
    """Types of customer identities"""
    EMAIL = "email"
    PHONE = "phone"
    DEVICE_ID = "device_id"
    SOCIAL_ID = "social_id"
    LOYALTY_ID = "loyalty_id"
    CUSTOMER_ID = "customer_id"
    EXTERNAL_ID = "external_id"

class DataSource(str, Enum):
    """Data source types"""
    POS = "pos"
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    EMAIL_PLATFORM = "email_platform"
    SOCIAL_MEDIA = "social_media"
    CUSTOMER_SERVICE = "customer_service"
    SURVEY = "survey"
    IMPORT = "import"
    API = "api"

# Database Models
class UnifiedProfile(Base):
    """Central unified customer profile"""
    __tablename__ = "unified_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    master_customer_id = Column(String, unique=True, index=True)
    primary_email = Column(String, index=True)
    primary_phone = Column(String, index=True)
    profile_data = Column(JSON, default={})  # Merged profile information
    computed_attributes = Column(JSON, default={})  # Calculated fields
    preferences = Column(JSON, default={})  # Communication preferences
    data_quality_score = Column(Float, default=0.0)
    last_merged_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    identities = relationship("CustomerIdentity", back_populates="profile")
    attributes = relationship("CustomerAttribute", back_populates="profile")
    events = relationship("CustomerEvent", back_populates="profile")

class CustomerIdentity(Base):
    """Customer identity mapping across different systems"""
    __tablename__ = "customer_identities"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("unified_profiles.id"), index=True)
    identity_type = Column(String, index=True)
    identity_value = Column(String, index=True)
    data_source = Column(String)
    confidence_score = Column(Float, default=1.0)  # 0-1 confidence in this identity
    verified = Column(Boolean, default=False)
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    
    # Relationships
    profile = relationship("UnifiedProfile", back_populates="identities")
    
    __table_args__ = (
        Index('idx_identity_lookup', 'identity_type', 'identity_value'),
    )

class CustomerAttribute(Base):
    """Customer attributes from various sources"""
    __tablename__ = "customer_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("unified_profiles.id"), index=True)
    attribute_name = Column(String, index=True)
    attribute_value = Column(String)
    data_source = Column(String)
    source_timestamp = Column(DateTime)
    confidence_score = Column(Float, default=1.0)
    is_pii = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    profile = relationship("UnifiedProfile", back_populates="attributes")

class CustomerEvent(Base):
    """Customer events and interactions"""
    __tablename__ = "customer_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String, ForeignKey("unified_profiles.id"), index=True)
    event_type = Column(String, index=True)
    event_name = Column(String)
    event_data = Column(JSON, default={})
    data_source = Column(String)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    session_id = Column(String, index=True)
    device_info = Column(JSON)
    location_data = Column(JSON)
    
    # Relationships
    profile = relationship("UnifiedProfile", back_populates="events")

@dataclass
class ProfileMergeResult:
    """Result of profile merge operation"""
    success: bool
    master_profile_id: str
    merged_profiles: List[str]
    conflicts_resolved: int
    data_quality_improvement: float
    message: str

class CustomerDataPlatform:
    """Customer Data Platform for unified profile management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.identity_matching_threshold = 0.8
        self.data_quality_weights = {
            'completeness': 0.3,
            'accuracy': 0.25,
            'consistency': 0.25,
            'freshness': 0.2
        }
    
    def resolve_identity(self, identifiers: Dict[str, str]) -> Optional[str]:
        """Resolve customer identity across multiple identifiers"""
        try:
            potential_profiles = set()
            
            # Look up each identifier
            for identity_type, identity_value in identifiers.items():
                if not identity_value:
                    continue
                
                identities = self.db.query(CustomerIdentity).filter(
                    CustomerIdentity.identity_type == identity_type,
                    CustomerIdentity.identity_value == identity_value
                ).all()
                
                for identity in identities:
                    if identity.confidence_score >= self.identity_matching_threshold:
                        potential_profiles.add(identity.profile_id)
            
            if not potential_profiles:
                return None
            
            if len(potential_profiles) == 1:
                return list(potential_profiles)[0]
            
            # Multiple profiles found - trigger merge
            return self._merge_profiles(list(potential_profiles))
            
        except Exception as e:
            logger.error(f"Error resolving identity: {e}")
            return None
    
    def create_unified_profile(self, profile_data: Dict[str, Any], 
                             identifiers: Dict[str, str],
                             data_source: DataSource) -> str:
        """Create a new unified customer profile"""
        try:
            # Check if profile already exists
            existing_profile_id = self.resolve_identity(identifiers)
            if existing_profile_id:
                return self.update_profile(existing_profile_id, profile_data, identifiers, data_source)
            
            # Create new profile
            master_customer_id = self._generate_master_id()
            
            profile = UnifiedProfile(
                master_customer_id=master_customer_id,
                primary_email=identifiers.get(IdentityType.EMAIL),
                primary_phone=identifiers.get(IdentityType.PHONE),
                profile_data=profile_data
            )
            
            self.db.add(profile)
            self.db.flush()  # Get the ID
            
            # Add identities
            for identity_type, identity_value in identifiers.items():
                if identity_value:
                    identity = CustomerIdentity(
                        profile_id=profile.id,
                        identity_type=identity_type,
                        identity_value=identity_value,
                        data_source=data_source.value,
                        verified=identity_type in [IdentityType.EMAIL, IdentityType.PHONE]
                    )
                    self.db.add(identity)
            
            # Add profile attributes
            for attr_name, attr_value in profile_data.items():
                if attr_value is not None:
                    attribute = CustomerAttribute(
                        profile_id=profile.id,
                        attribute_name=attr_name,
                        attribute_value=str(attr_value),
                        data_source=data_source.value,
                        source_timestamp=datetime.now(),
                        is_pii=self._is_pii_field(attr_name)
                    )
                    self.db.add(attribute)
            
            # Calculate initial data quality score
            profile.data_quality_score = self._calculate_data_quality_score(profile.id)
            
            self.db.commit()
            
            logger.info(f"Created unified profile: {profile.id}")
            return profile.id
            
        except Exception as e:
            logger.error(f"Error creating unified profile: {e}")
            self.db.rollback()
            raise
    
    def update_profile(self, profile_id: str, new_data: Dict[str, Any],
                      identifiers: Dict[str, str] = None,
                      data_source: DataSource = DataSource.API) -> str:
        """Update existing unified profile with new data"""
        try:
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                raise ValueError(f"Profile {profile_id} not found")
            
            # Merge new data with existing
            updated_data = profile.profile_data.copy()
            conflicts_resolved = 0
            
            for key, new_value in new_data.items():
                if key in updated_data and updated_data[key] != new_value:
                    # Conflict resolution - prefer newer data for most fields
                    if self._should_prefer_new_value(key, updated_data[key], new_value):
                        updated_data[key] = new_value
                        conflicts_resolved += 1
                else:
                    updated_data[key] = new_value
            
            profile.profile_data = updated_data
            
            # Add new identifiers if provided
            if identifiers:
                for identity_type, identity_value in identifiers.items():
                    if identity_value:
                        existing = self.db.query(CustomerIdentity).filter(
                            CustomerIdentity.profile_id == profile_id,
                            CustomerIdentity.identity_type == identity_type,
                            CustomerIdentity.identity_value == identity_value
                        ).first()
                        
                        if not existing:
                            identity = CustomerIdentity(
                                profile_id=profile_id,
                                identity_type=identity_type,
                                identity_value=identity_value,
                                data_source=data_source.value
                            )
                            self.db.add(identity)
            
            # Update attributes
            for attr_name, attr_value in new_data.items():
                if attr_value is not None:
                    # Check if attribute exists
                    existing_attr = self.db.query(CustomerAttribute).filter(
                        CustomerAttribute.profile_id == profile_id,
                        CustomerAttribute.attribute_name == attr_name,
                        CustomerAttribute.data_source == data_source.value
                    ).first()
                    
                    if existing_attr:
                        existing_attr.attribute_value = str(attr_value)
                        existing_attr.source_timestamp = datetime.now()
                    else:
                        attribute = CustomerAttribute(
                            profile_id=profile_id,
                            attribute_name=attr_name,
                            attribute_value=str(attr_value),
                            data_source=data_source.value,
                            source_timestamp=datetime.now(),
                            is_pii=self._is_pii_field(attr_name)
                        )
                        self.db.add(attribute)
            
            # Recalculate data quality score
            profile.data_quality_score = self._calculate_data_quality_score(profile_id)
            profile.updated_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Updated profile {profile_id}, resolved {conflicts_resolved} conflicts")
            return profile_id
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            self.db.rollback()
            raise
    
    def get_unified_profile(self, profile_id: str = None, 
                          identifiers: Dict[str, str] = None) -> Dict[str, Any]:
        """Get complete unified customer profile"""
        try:
            if not profile_id and identifiers:
                profile_id = self.resolve_identity(identifiers)
            
            if not profile_id:
                return None
            
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                return None
            
            # Get all identities
            identities = self.db.query(CustomerIdentity).filter(
                CustomerIdentity.profile_id == profile_id
            ).all()
            
            # Get all attributes
            attributes = self.db.query(CustomerAttribute).filter(
                CustomerAttribute.profile_id == profile_id
            ).order_by(CustomerAttribute.created_at.desc()).all()
            
            # Get recent events
            recent_events = self.db.query(CustomerEvent).filter(
                CustomerEvent.profile_id == profile_id
            ).order_by(CustomerEvent.timestamp.desc()).limit(100).all()
            
            # Compute real-time attributes
            computed_attributes = self._compute_profile_attributes(profile_id)
            
            return {
                "profile_id": profile.id,
                "master_customer_id": profile.master_customer_id,
                "primary_email": profile.primary_email,
                "primary_phone": profile.primary_phone,
                "profile_data": profile.profile_data,
                "computed_attributes": computed_attributes,
                "preferences": profile.preferences,
                "data_quality_score": profile.data_quality_score,
                "identities": [
                    {
                        "type": identity.identity_type,
                        "value": identity.identity_value,
                        "source": identity.data_source,
                        "confidence": identity.confidence_score,
                        "verified": identity.verified
                    } for identity in identities
                ],
                "attributes": [
                    {
                        "name": attr.attribute_name,
                        "value": attr.attribute_value,
                        "source": attr.data_source,
                        "timestamp": attr.source_timestamp.isoformat() if attr.source_timestamp else None,
                        "confidence": attr.confidence_score
                    } for attr in attributes
                ],
                "recent_activity": [
                    {
                        "event_type": event.event_type,
                        "event_name": event.event_name,
                        "timestamp": event.timestamp.isoformat(),
                        "source": event.data_source,
                        "data": event.event_data
                    } for event in recent_events[:20]
                ],
                "last_updated": profile.updated_at.isoformat(),
                "profile_completeness": self._calculate_profile_completeness(profile_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting unified profile: {e}")
            raise
    
    def track_event(self, profile_id: str, event_type: str, event_name: str,
                   event_data: Dict[str, Any], data_source: DataSource,
                   session_id: str = None) -> str:
        """Track customer event in unified profile"""
        try:
            event = CustomerEvent(
                profile_id=profile_id,
                event_type=event_type,
                event_name=event_name,
                event_data=event_data,
                data_source=data_source.value,
                session_id=session_id or str(uuid.uuid4())
            )
            
            self.db.add(event)
            
            # Update computed attributes based on event
            self._update_computed_attributes(profile_id, event_type, event_data)
            
            self.db.commit()
            
            return event.id
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            self.db.rollback()
            raise
    
    def merge_profiles(self, profile_ids: List[str]) -> ProfileMergeResult:
        """Merge multiple customer profiles into one"""
        try:
            if len(profile_ids) < 2:
                return ProfileMergeResult(
                    success=False,
                    master_profile_id="",
                    merged_profiles=[],
                    conflicts_resolved=0,
                    data_quality_improvement=0.0,
                    message="At least 2 profiles required for merge"
                )
            
            # Get all profiles
            profiles = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id.in_(profile_ids)
            ).all()
            
            if len(profiles) != len(profile_ids):
                return ProfileMergeResult(
                    success=False,
                    master_profile_id="",
                    merged_profiles=[],
                    conflicts_resolved=0,
                    data_quality_improvement=0.0,
                    message="Some profiles not found"
                )
            
            # Select master profile (highest data quality score)
            master_profile = max(profiles, key=lambda p: p.data_quality_score)
            other_profiles = [p for p in profiles if p.id != master_profile.id]
            
            initial_quality = master_profile.data_quality_score
            conflicts_resolved = 0
            
            # Merge data from other profiles
            merged_data = master_profile.profile_data.copy()
            
            for profile in other_profiles:
                for key, value in profile.profile_data.items():
                    if key not in merged_data:
                        merged_data[key] = value
                    elif merged_data[key] != value:
                        # Conflict resolution
                        if self._should_prefer_new_value(key, merged_data[key], value):
                            merged_data[key] = value
                            conflicts_resolved += 1
            
            master_profile.profile_data = merged_data
            
            # Move all identities to master profile
            for profile in other_profiles:
                self.db.query(CustomerIdentity).filter(
                    CustomerIdentity.profile_id == profile.id
                ).update({"profile_id": master_profile.id})
                
                # Move all attributes
                self.db.query(CustomerAttribute).filter(
                    CustomerAttribute.profile_id == profile.id
                ).update({"profile_id": master_profile.id})
                
                # Move all events
                self.db.query(CustomerEvent).filter(
                    CustomerEvent.profile_id == profile.id
                ).update({"profile_id": master_profile.id})
            
            # Delete other profiles
            for profile in other_profiles:
                self.db.delete(profile)
            
            # Recalculate data quality
            master_profile.data_quality_score = self._calculate_data_quality_score(master_profile.id)
            master_profile.last_merged_at = datetime.now()
            
            final_quality = master_profile.data_quality_score
            quality_improvement = final_quality - initial_quality
            
            self.db.commit()
            
            return ProfileMergeResult(
                success=True,
                master_profile_id=master_profile.id,
                merged_profiles=[p.id for p in other_profiles],
                conflicts_resolved=conflicts_resolved,
                data_quality_improvement=quality_improvement,
                message=f"Successfully merged {len(other_profiles)} profiles"
            )
            
        except Exception as e:
            logger.error(f"Error merging profiles: {e}")
            self.db.rollback()
            raise
    
    def get_profile_analytics(self, profile_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a customer profile"""
        try:
            # Get profile
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                return {"error": "Profile not found"}
            
            # Get events for analysis
            events = self.db.query(CustomerEvent).filter(
                CustomerEvent.profile_id == profile_id,
                CustomerEvent.timestamp >= datetime.now() - timedelta(days=90)
            ).all()
            
            # Analyze activity patterns
            daily_activity = defaultdict(int)
            event_types = defaultdict(int)
            data_sources = defaultdict(int)
            
            for event in events:
                day = event.timestamp.date().isoformat()
                daily_activity[day] += 1
                event_types[event.event_type] += 1
                data_sources[event.data_source] += 1
            
            # Calculate engagement metrics
            total_events = len(events)
            unique_days = len(daily_activity)
            avg_daily_events = total_events / max(1, unique_days)
            
            # Data quality breakdown
            quality_breakdown = self._analyze_data_quality(profile_id)
            
            return {
                "profile_id": profile_id,
                "master_customer_id": profile.master_customer_id,
                "analytics_period": "Last 90 days",
                "activity_summary": {
                    "total_events": total_events,
                    "active_days": unique_days,
                    "average_daily_events": avg_daily_events,
                    "most_active_day": max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None
                },
                "engagement_patterns": {
                    "event_type_distribution": dict(event_types),
                    "data_source_distribution": dict(data_sources),
                    "daily_activity": dict(daily_activity)
                },
                "data_quality": {
                    "overall_score": profile.data_quality_score,
                    "breakdown": quality_breakdown,
                    "last_updated": profile.updated_at.isoformat()
                },
                "computed_attributes": self._compute_profile_attributes(profile_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting profile analytics: {e}")
            raise
    
    # Helper methods
    def _generate_master_id(self) -> str:
        """Generate unique master customer ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:8]
        return f"SBM_{timestamp}_{random_suffix}"
    
    def _merge_profiles(self, profile_ids: List[str]) -> str:
        """Internal method to merge profiles"""
        merge_result = self.merge_profiles(profile_ids)
        return merge_result.master_profile_id if merge_result.success else profile_ids[0]
    
    def _should_prefer_new_value(self, field_name: str, old_value: Any, new_value: Any) -> bool:
        """Determine if new value should be preferred over old"""
        # Prefer non-empty values
        if not old_value and new_value:
            return True
        if old_value and not new_value:
            return False
        
        # For specific fields, prefer newer data
        prefer_newer_fields = ["email", "phone", "address", "job_title"]
        if field_name.lower() in prefer_newer_fields:
            return True
        
        # For dates, prefer more recent
        if "date" in field_name.lower():
            try:
                old_date = datetime.fromisoformat(str(old_value))
                new_date = datetime.fromisoformat(str(new_value))
                return new_date > old_date
            except:
                pass
        
        return False
    
    def _is_pii_field(self, field_name: str) -> bool:
        """Check if field contains PII"""
        pii_fields = [
            "email", "phone", "address", "name", "ssn", "id_number",
            "credit_card", "bank_account", "passport", "driver_license"
        ]
        return any(pii in field_name.lower() for pii in pii_fields)
    
    def _calculate_data_quality_score(self, profile_id: str) -> float:
        """Calculate data quality score for profile"""
        try:
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                return 0.0
            
            # Completeness score
            completeness = self._calculate_profile_completeness(profile_id)
            
            # Accuracy score (based on verified identities)
            verified_identities = self.db.query(CustomerIdentity).filter(
                CustomerIdentity.profile_id == profile_id,
                CustomerIdentity.verified == True
            ).count()
            total_identities = self.db.query(CustomerIdentity).filter(
                CustomerIdentity.profile_id == profile_id
            ).count()
            accuracy = (verified_identities / max(1, total_identities)) * 100
            
            # Consistency score (conflicts in attributes)
            attributes = self.db.query(CustomerAttribute).filter(
                CustomerAttribute.profile_id == profile_id
            ).all()
            
            attr_conflicts = 0
            attr_groups = defaultdict(list)
            for attr in attributes:
                attr_groups[attr.attribute_name].append(attr.attribute_value)
            
            for attr_name, values in attr_groups.items():
                if len(set(values)) > 1:
                    attr_conflicts += 1
            
            consistency = max(0, 100 - (attr_conflicts * 10))
            
            # Freshness score (how recent is the data)
            days_since_update = (datetime.now() - profile.updated_at).days
            freshness = max(0, 100 - (days_since_update * 2))
            
            # Calculate weighted score
            total_score = (
                completeness * self.data_quality_weights['completeness'] +
                accuracy * self.data_quality_weights['accuracy'] +
                consistency * self.data_quality_weights['consistency'] +
                freshness * self.data_quality_weights['freshness']
            )
            
            return min(100, max(0, total_score))
            
        except Exception as e:
            logger.error(f"Error calculating data quality score: {e}")
            return 0.0
    
    def _calculate_profile_completeness(self, profile_id: str) -> float:
        """Calculate profile completeness percentage"""
        try:
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                return 0.0
            
            essential_fields = [
                "name", "email", "phone", "age", "gender", 
                "city", "country", "preferences"
            ]
            
            filled_fields = 0
            total_fields = len(essential_fields)
            
            profile_data = profile.profile_data or {}
            
            for field in essential_fields:
                if field in profile_data and profile_data[field]:
                    filled_fields += 1
                elif field == "email" and profile.primary_email:
                    filled_fields += 1
                elif field == "phone" and profile.primary_phone:
                    filled_fields += 1
            
            return (filled_fields / total_fields) * 100
            
        except Exception as e:
            logger.error(f"Error calculating profile completeness: {e}")
            return 0.0
    
    def _compute_profile_attributes(self, profile_id: str) -> Dict[str, Any]:
        """Compute real-time profile attributes"""
        try:
            # Get recent events
            events = self.db.query(CustomerEvent).filter(
                CustomerEvent.profile_id == profile_id,
                CustomerEvent.timestamp >= datetime.now() - timedelta(days=30)
            ).all()
            
            # Compute attributes
            computed = {
                "total_events_30d": len(events),
                "unique_sessions_30d": len(set(e.session_id for e in events if e.session_id)),
                "last_activity": events[0].timestamp.isoformat() if events else None,
                "most_common_event": None,
                "preferred_channel": None,
                "activity_score": 0
            }
            
            if events:
                # Most common event type
                event_counts = defaultdict(int)
                source_counts = defaultdict(int)
                
                for event in events:
                    event_counts[event.event_type] += 1
                    source_counts[event.data_source] += 1
                
                computed["most_common_event"] = max(event_counts.items(), key=lambda x: x[1])[0]
                computed["preferred_channel"] = max(source_counts.items(), key=lambda x: x[1])[0]
                
                # Activity score (0-100)
                unique_days = len(set(e.timestamp.date() for e in events))
                computed["activity_score"] = min(100, (unique_days / 30) * 100)
            
            return computed
            
        except Exception as e:
            logger.error(f"Error computing profile attributes: {e}")
            return {}
    
    def _update_computed_attributes(self, profile_id: str, event_type: str, event_data: Dict[str, Any]):
        """Update computed attributes based on new event"""
        try:
            profile = self.db.query(UnifiedProfile).filter(
                UnifiedProfile.id == profile_id
            ).first()
            
            if not profile:
                return
            
            computed = profile.computed_attributes or {}
            
            # Update last activity
            computed["last_activity"] = datetime.now().isoformat()
            
            # Update event counters
            computed["total_events"] = computed.get("total_events", 0) + 1
            
            # Update preferences based on event
            if event_type == "email_click":
                preferences = profile.preferences or {}
                preferences["email_engagement"] = True
                profile.preferences = preferences
            
            profile.computed_attributes = computed
            
        except Exception as e:
            logger.error(f"Error updating computed attributes: {e}")
    
    def _analyze_data_quality(self, profile_id: str) -> Dict[str, Any]:
        """Analyze data quality breakdown"""
        try:
            completeness = self._calculate_profile_completeness(profile_id)
            
            # Count verified vs unverified identities
            total_identities = self.db.query(CustomerIdentity).filter(
                CustomerIdentity.profile_id == profile_id
            ).count()
            
            verified_identities = self.db.query(CustomerIdentity).filter(
                CustomerIdentity.profile_id == profile_id,
                CustomerIdentity.verified == True
            ).count()
            
            verification_rate = (verified_identities / max(1, total_identities)) * 100
            
            # Check for duplicate attributes
            attributes = self.db.query(CustomerAttribute).filter(
                CustomerAttribute.profile_id == profile_id
            ).all()
            
            attr_groups = defaultdict(list)
            for attr in attributes:
                attr_groups[attr.attribute_name].append(attr.attribute_value)
            
            duplicate_attrs = sum(1 for values in attr_groups.values() if len(set(values)) > 1)
            consistency_score = max(0, 100 - (duplicate_attrs * 10))
            
            return {
                "completeness_score": completeness,
                "verification_rate": verification_rate,
                "consistency_score": consistency_score,
                "total_identities": total_identities,
                "verified_identities": verified_identities,
                "attribute_conflicts": duplicate_attrs
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data quality: {e}")
            return {}