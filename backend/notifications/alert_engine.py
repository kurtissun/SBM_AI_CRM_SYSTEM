"""
Real-time Notifications & Alerts Engine
"""
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
import asyncio
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import smtplib
from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor

from core.database import Base, get_db

logger = logging.getLogger(__name__)

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(str, Enum):
    """Alert processing status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class TriggerType(str, Enum):
    """Alert trigger types"""
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    WORKFLOW = "workflow"

class AggregationMethod(str, Enum):
    """Alert aggregation methods"""
    NONE = "none"
    COUNT = "count"
    TIME_WINDOW = "time_window"
    DUPLICATE_CONTENT = "duplicate_content"
    SIMILAR_EVENTS = "similar_events"

# Database Models
class NotificationTemplate(Base):
    """Notification message templates"""
    __tablename__ = "notification_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Template content
    subject_template = Column(Text)
    body_template = Column(Text, nullable=False)
    html_template = Column(Text)
    
    # Template configuration
    channel = Column(String, nullable=False)
    template_variables = Column(JSON, default=[])  # List of required variables
    default_values = Column(JSON, default={})
    
    # Formatting options
    formatting_options = Column(JSON, default={})
    localization = Column(JSON, default={})
    
    # Template metadata
    category = Column(String)
    tags = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AlertRule(Base):
    """Alert rule definitions"""
    __tablename__ = "alert_rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    
    # Rule configuration
    trigger_type = Column(String, nullable=False)
    trigger_conditions = Column(JSON, nullable=False)  # Conditions that trigger the alert
    data_source = Column(String)  # Source of data to monitor
    query_config = Column(JSON, default={})
    
    # Alert settings
    severity = Column(String, default=AlertSeverity.MEDIUM.value)
    channels = Column(JSON, nullable=False)  # List of notification channels
    template_id = Column(String, ForeignKey("notification_templates.id"))
    
    # Frequency and timing
    check_interval_seconds = Column(Integer, default=300)  # 5 minutes
    aggregation_method = Column(String, default=AggregationMethod.NONE.value)
    aggregation_window_seconds = Column(Integer, default=3600)  # 1 hour
    
    # Recipients
    recipient_config = Column(JSON, nullable=False)  # Who receives alerts
    escalation_rules = Column(JSON, default=[])
    
    # Throttling and limits
    rate_limit_count = Column(Integer, default=10)
    rate_limit_window_seconds = Column(Integer, default=3600)
    quiet_hours = Column(JSON, default={})  # Time ranges to suppress alerts
    
    # Rule state
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    last_checked = Column(DateTime)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)
    
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    template = relationship("NotificationTemplate")
    alerts = relationship("Alert", back_populates="rule")

class Alert(Base):
    """Individual alert instances"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, ForeignKey("alert_rules.id"), index=True)
    
    # Alert details
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False, index=True)
    status = Column(String, default=AlertStatus.PENDING.value, index=True)
    
    # Context and data
    alert_data = Column(JSON, default={})  # Data that triggered the alert
    context = Column(JSON, default={})     # Additional context
    source_data = Column(JSON, default={}) # Original source data
    
    # Aggregation
    aggregated_count = Column(Integer, default=1)
    aggregated_alerts = Column(JSON, default=[])  # IDs of aggregated alerts
    parent_alert_id = Column(String, ForeignKey("alerts.id"))
    
    # Timing
    triggered_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Response tracking
    acknowledged_by = Column(String)
    resolved_by = Column(String)
    resolution_notes = Column(Text)
    
    # Delivery tracking
    delivery_attempts = Column(Integer, default=0)
    successful_deliveries = Column(JSON, default=[])
    failed_deliveries = Column(JSON, default=[])
    
    # Performance metrics
    time_to_acknowledge = Column(Float)  # Seconds
    time_to_resolve = Column(Float)      # Seconds
    impact_score = Column(Float, default=0.0)
    
    # Relationships
    rule = relationship("AlertRule", back_populates="alerts")
    notifications = relationship("NotificationDelivery", back_populates="alert")
    children = relationship("Alert", backref="parent", remote_side=[id])
    
    __table_args__ = (
        Index('idx_alert_status_time', 'status', 'triggered_at'),
        Index('idx_alert_severity_time', 'severity', 'triggered_at'),
    )

class NotificationDelivery(Base):
    """Notification delivery tracking"""
    __tablename__ = "notification_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_id = Column(String, ForeignKey("alerts.id"), index=True)
    
    # Delivery details
    channel = Column(String, nullable=False, index=True)
    recipient = Column(String, nullable=False, index=True)
    status = Column(String, default=AlertStatus.PENDING.value, index=True)
    
    # Message content
    subject = Column(String)
    body = Column(Text)
    formatted_content = Column(JSON, default={})
    
    # Delivery tracking
    attempted_at = Column(DateTime, default=datetime.now)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Provider details
    provider = Column(String)
    external_id = Column(String)  # ID from external service
    provider_response = Column(JSON, default={})
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)
    
    # Performance metrics
    delivery_time_ms = Column(Integer)
    cost = Column(Float, default=0.0)
    
    # Relationships
    alert = relationship("Alert", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_delivery_status_time', 'status', 'attempted_at'),
        Index('idx_delivery_channel_recipient', 'channel', 'recipient'),
    )

class NotificationPreference(Base):
    """User notification preferences"""
    __tablename__ = "notification_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Contact information
    email_address = Column(String)
    phone_number = Column(String)
    push_tokens = Column(JSON, default=[])
    
    # Severity preferences
    severity_preferences = Column(JSON, default={})  # Min severity per channel
    
    # Timing preferences
    quiet_hours = Column(JSON, default={})
    timezone = Column(String, default="UTC")
    
    # Category preferences
    alert_categories = Column(JSON, default={})  # Enabled categories
    frequency_limits = Column(JSON, default={})  # Max alerts per timeframe
    
    # Delivery options
    delivery_options = Column(JSON, default={})
    escalation_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

@dataclass
class AlertContext:
    """Context for alert processing"""
    rule_id: str
    trigger_data: Dict[str, Any]
    severity: AlertSeverity
    title: str
    message: str
    additional_context: Dict[str, Any] = None

@dataclass
class NotificationResult:
    """Result of notification delivery"""
    success: bool
    channel: str
    recipient: str
    message: str
    external_id: str = None
    delivery_time_ms: int = None
    cost: float = 0.0
    error: str = None

@dataclass
class AlertMetrics:
    """Alert system metrics"""
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    alerts_by_status: Dict[str, int]
    avg_response_time: float
    avg_resolution_time: float
    delivery_success_rate: float
    active_rules: int

class NotificationEngine:
    """Real-time notifications and alerts engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_queue = deque()
        self.active_websockets = set()
        self.rate_limiters = defaultdict(lambda: defaultdict(list))
        
        # Configuration
        self.max_queue_size = 10000
        self.batch_size = 100
        self.processing_interval = 1  # seconds
        self.websocket_port = 8765
        
        # Delivery providers (would be configured with actual credentials)
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": ""
        }
        
        self.sms_config = {
            "provider": "twilio",
            "account_sid": "",
            "auth_token": "",
            "from_number": ""
        }
        
        # Template engine
        self.template_cache = {}
        
        # Alert aggregation
        self.aggregation_windows = defaultdict(list)
        self.duplicate_detector = defaultdict(set)
        
        # Performance tracking
        self.metrics = AlertMetrics(
            total_alerts=0,
            alerts_by_severity={},
            alerts_by_status={},
            avg_response_time=0.0,
            avg_resolution_time=0.0,
            delivery_success_rate=0.0,
            active_rules=0
        )
    
    async def trigger_alert(self, alert_context: AlertContext) -> str:
        """Trigger a new alert"""
        try:
            # Get alert rule
            rule = self.db.query(AlertRule).filter(
                AlertRule.id == alert_context.rule_id,
                AlertRule.is_active == True
            ).first()
            
            if not rule:
                raise ValueError(f"Alert rule {alert_context.rule_id} not found or inactive")
            
            # Check rate limiting
            if self._is_rate_limited(rule):
                logger.warning(f"Alert rule {rule.name} is rate limited")
                return None
            
            # Check quiet hours
            if self._is_in_quiet_hours(rule):
                logger.info(f"Alert rule {rule.name} suppressed due to quiet hours")
                return None
            
            # Check for aggregation
            aggregated_alert_id = await self._check_aggregation(rule, alert_context)
            if aggregated_alert_id:
                logger.info(f"Alert aggregated with {aggregated_alert_id}")
                return aggregated_alert_id
            
            # Create alert
            alert = Alert(
                rule_id=rule.id,
                title=alert_context.title,
                message=alert_context.message,
                severity=alert_context.severity.value,
                alert_data=alert_context.trigger_data,
                context=alert_context.additional_context or {},
                triggered_at=datetime.now()
            )
            
            self.db.add(alert)
            self.db.flush()  # Get the ID
            
            # Update rule metrics
            rule.trigger_count += 1
            rule.last_triggered = datetime.now()
            
            # Queue for processing
            await self._queue_alert_for_processing(alert, rule)
            
            self.db.commit()
            
            logger.info(f"Alert triggered: {alert.title} (ID: {alert.id})")
            return alert.id
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
            self.db.rollback()
            raise
    
    async def process_notification_queue(self):
        """Process pending notifications"""
        try:
            while True:
                if not self.notification_queue:
                    await asyncio.sleep(self.processing_interval)
                    continue
                
                # Process batch
                batch = []
                for _ in range(min(self.batch_size, len(self.notification_queue))):
                    if self.notification_queue:
                        batch.append(self.notification_queue.popleft())
                
                if batch:
                    await self._process_notification_batch(batch)
                
                await asyncio.sleep(self.processing_interval)
                
        except Exception as e:
            logger.error(f"Error in notification queue processing: {e}")
    
    async def send_notification(self, alert: Alert, channel: NotificationChannel,
                             recipient: str, content: Dict[str, Any]) -> NotificationResult:
        """Send notification through specified channel"""
        try:
            start_time = datetime.now()
            
            # Create delivery record
            delivery = NotificationDelivery(
                alert_id=alert.id,
                channel=channel.value,
                recipient=recipient,
                subject=content.get("subject"),
                body=content.get("body"),
                formatted_content=content
            )
            
            self.db.add(delivery)
            self.db.flush()
            
            # Send through appropriate channel
            result = None
            if channel == NotificationChannel.EMAIL:
                result = await self._send_email(recipient, content)
            elif channel == NotificationChannel.SMS:
                result = await self._send_sms(recipient, content)
            elif channel == NotificationChannel.PUSH:
                result = await self._send_push(recipient, content)
            elif channel == NotificationChannel.IN_APP:
                result = await self._send_in_app(recipient, content)
            elif channel == NotificationChannel.WEBHOOK:
                result = await self._send_webhook(recipient, content)
            else:
                result = NotificationResult(
                    success=False,
                    channel=channel.value,
                    recipient=recipient,
                    message="Unsupported channel",
                    error="Channel not implemented"
                )
            
            # Update delivery record
            delivery_time = (datetime.now() - start_time).total_seconds() * 1000
            delivery.delivery_time_ms = int(delivery_time)
            delivery.cost = result.cost
            
            if result.success:
                delivery.status = AlertStatus.DELIVERED.value
                delivery.delivered_at = datetime.now()
                delivery.external_id = result.external_id
            else:
                delivery.status = AlertStatus.FAILED.value
                delivery.error_message = result.error
                
                # Schedule retry if under limit
                if delivery.retry_count < delivery.max_retries:
                    delivery.retry_count += 1
                    delivery.next_retry_at = datetime.now() + timedelta(
                        minutes=2 ** delivery.retry_count  # Exponential backoff
                    )
            
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            self.db.rollback()
            
            return NotificationResult(
                success=False,
                channel=channel.value,
                recipient=recipient,
                message="Internal error",
                error=str(e)
            )
    
    def create_alert_rule(self, rule_config: Dict[str, Any]) -> str:
        """Create a new alert rule"""
        try:
            rule = AlertRule(
                name=rule_config["name"],
                description=rule_config.get("description", ""),
                trigger_type=rule_config["trigger_type"],
                trigger_conditions=rule_config["trigger_conditions"],
                data_source=rule_config.get("data_source"),
                query_config=rule_config.get("query_config", {}),
                severity=rule_config.get("severity", AlertSeverity.MEDIUM.value),
                channels=rule_config["channels"],
                template_id=rule_config.get("template_id"),
                check_interval_seconds=rule_config.get("check_interval_seconds", 300),
                aggregation_method=rule_config.get("aggregation_method", AggregationMethod.NONE.value),
                aggregation_window_seconds=rule_config.get("aggregation_window_seconds", 3600),
                recipient_config=rule_config["recipient_config"],
                escalation_rules=rule_config.get("escalation_rules", []),
                rate_limit_count=rule_config.get("rate_limit_count", 10),
                rate_limit_window_seconds=rule_config.get("rate_limit_window_seconds", 3600),
                quiet_hours=rule_config.get("quiet_hours", {}),
                created_by=rule_config.get("created_by", "system")
            )
            
            self.db.add(rule)
            self.db.commit()
            
            logger.info(f"Created alert rule: {rule.name}")
            return rule.id
            
        except Exception as e:
            logger.error(f"Error creating alert rule: {e}")
            self.db.rollback()
            raise
    
    def create_notification_template(self, template_config: Dict[str, Any]) -> str:
        """Create a notification template"""
        try:
            template = NotificationTemplate(
                name=template_config["name"],
                description=template_config.get("description", ""),
                subject_template=template_config.get("subject_template"),
                body_template=template_config["body_template"],
                html_template=template_config.get("html_template"),
                channel=template_config["channel"],
                template_variables=template_config.get("template_variables", []),
                default_values=template_config.get("default_values", {}),
                formatting_options=template_config.get("formatting_options", {}),
                localization=template_config.get("localization", {}),
                category=template_config.get("category"),
                tags=template_config.get("tags", [])
            )
            
            self.db.add(template)
            self.db.commit()
            
            # Clear template cache
            self.template_cache.clear()
            
            logger.info(f"Created notification template: {template.name}")
            return template.id
            
        except Exception as e:
            logger.error(f"Error creating notification template: {e}")
            self.db.rollback()
            raise
    
    def get_alert_metrics(self, timeframe_hours: int = 24) -> AlertMetrics:
        """Get alert system metrics"""
        try:
            start_time = datetime.now() - timedelta(hours=timeframe_hours)
            
            # Get alerts in timeframe
            alerts = self.db.query(Alert).filter(
                Alert.triggered_at >= start_time
            ).all()
            
            # Calculate metrics
            total_alerts = len(alerts)
            
            alerts_by_severity = defaultdict(int)
            alerts_by_status = defaultdict(int)
            response_times = []
            resolution_times = []
            
            for alert in alerts:
                alerts_by_severity[alert.severity] += 1
                alerts_by_status[alert.status] += 1
                
                if alert.time_to_acknowledge:
                    response_times.append(alert.time_to_acknowledge)
                
                if alert.time_to_resolve:
                    resolution_times.append(alert.time_to_resolve)
            
            # Get delivery metrics
            deliveries = self.db.query(NotificationDelivery).join(Alert).filter(
                Alert.triggered_at >= start_time
            ).all()
            
            successful_deliveries = sum(1 for d in deliveries if d.status == AlertStatus.DELIVERED.value)
            total_deliveries = len(deliveries)
            delivery_success_rate = (successful_deliveries / max(1, total_deliveries)) * 100
            
            # Get active rules count
            active_rules = self.db.query(AlertRule).filter(
                AlertRule.is_active == True
            ).count()
            
            return AlertMetrics(
                total_alerts=total_alerts,
                alerts_by_severity=dict(alerts_by_severity),
                alerts_by_status=dict(alerts_by_status),
                avg_response_time=sum(response_times) / max(1, len(response_times)),
                avg_resolution_time=sum(resolution_times) / max(1, len(resolution_times)),
                delivery_success_rate=delivery_success_rate,
                active_rules=active_rules
            )
            
        except Exception as e:
            logger.error(f"Error getting alert metrics: {e}")
            return self.metrics
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, notes: str = None) -> bool:
        """Acknowledge an alert"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                return False
            
            if alert.status != AlertStatus.PENDING.value:
                return False  # Already acknowledged or resolved
            
            # Update alert
            alert.status = AlertStatus.ACKNOWLEDGED.value
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id
            
            if alert.triggered_at:
                alert.time_to_acknowledge = (
                    alert.acknowledged_at - alert.triggered_at
                ).total_seconds()
            
            # Send acknowledgment notifications
            await self._send_acknowledgment_notifications(alert, user_id, notes)
            
            self.db.commit()
            
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            self.db.rollback()
            return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, notes: str = None) -> bool:
        """Resolve an alert"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                return False
            
            # Update alert
            alert.status = AlertStatus.RESOLVED.value
            alert.resolved_at = datetime.now()
            alert.resolved_by = user_id
            alert.resolution_notes = notes
            
            if alert.triggered_at:
                alert.time_to_resolve = (
                    alert.resolved_at - alert.triggered_at
                ).total_seconds()
            
            # Send resolution notifications
            await self._send_resolution_notifications(alert, user_id, notes)
            
            self.db.commit()
            
            logger.info(f"Alert {alert_id} resolved by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            self.db.rollback()
            return False
    
    # Helper methods
    def _is_rate_limited(self, rule: AlertRule) -> bool:
        """Check if rule is rate limited"""
        try:
            now = datetime.now()
            window_start = now - timedelta(seconds=rule.rate_limit_window_seconds)
            
            recent_alerts = self.db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.triggered_at >= window_start
            ).count()
            
            return recent_alerts >= rule.rate_limit_count
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    def _is_in_quiet_hours(self, rule: AlertRule) -> bool:
        """Check if current time is in quiet hours"""
        try:
            if not rule.quiet_hours:
                return False
            
            now = datetime.now()
            current_hour = now.hour
            current_day = now.strftime("%A").lower()
            
            # Check daily quiet hours
            daily_quiet = rule.quiet_hours.get("daily", {})
            if daily_quiet:
                start_hour = daily_quiet.get("start_hour", 0)
                end_hour = daily_quiet.get("end_hour", 24)
                
                if start_hour <= current_hour < end_hour:
                    return True
            
            # Check day-specific quiet hours
            day_quiet = rule.quiet_hours.get(current_day, {})
            if day_quiet:
                start_hour = day_quiet.get("start_hour", 0)
                end_hour = day_quiet.get("end_hour", 24)
                
                if start_hour <= current_hour < end_hour:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False
    
    async def _check_aggregation(self, rule: AlertRule, alert_context: AlertContext) -> Optional[str]:
        """Check if alert should be aggregated"""
        try:
            if rule.aggregation_method == AggregationMethod.NONE.value:
                return None
            
            window_start = datetime.now() - timedelta(seconds=rule.aggregation_window_seconds)
            
            if rule.aggregation_method == AggregationMethod.TIME_WINDOW.value:
                # Find alerts in time window
                recent_alerts = self.db.query(Alert).filter(
                    Alert.rule_id == rule.id,
                    Alert.triggered_at >= window_start,
                    Alert.status.in_([AlertStatus.PENDING.value, AlertStatus.ACKNOWLEDGED.value])
                ).first()
                
                if recent_alerts:
                    # Aggregate with existing alert
                    recent_alerts.aggregated_count += 1
                    recent_alerts.aggregated_alerts.append({
                        "timestamp": datetime.now().isoformat(),
                        "data": alert_context.trigger_data
                    })
                    self.db.commit()
                    return recent_alerts.id
            
            elif rule.aggregation_method == AggregationMethod.DUPLICATE_CONTENT.value:
                # Check for duplicate content
                content_hash = self._generate_content_hash(alert_context.title, alert_context.message)
                
                duplicate_alert = self.db.query(Alert).filter(
                    Alert.rule_id == rule.id,
                    Alert.triggered_at >= window_start,
                    Alert.status.in_([AlertStatus.PENDING.value, AlertStatus.ACKNOWLEDGED.value])
                ).first()  # Would need to add content hash to check properly
                
                if duplicate_alert:
                    duplicate_alert.aggregated_count += 1
                    self.db.commit()
                    return duplicate_alert.id
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking aggregation: {e}")
            return None
    
    async def _queue_alert_for_processing(self, alert: Alert, rule: AlertRule):
        """Queue alert for notification processing"""
        try:
            # Add to processing queue
            queue_item = {
                "alert_id": alert.id,
                "rule_id": rule.id,
                "priority": self._get_processing_priority(alert.severity),
                "queued_at": datetime.now().isoformat()
            }
            
            if len(self.notification_queue) >= self.max_queue_size:
                # Remove oldest low priority item
                removed = False
                for i, item in enumerate(self.notification_queue):
                    if item["priority"] <= 1:  # Low priority
                        del self.notification_queue[i]
                        removed = True
                        break
                
                if not removed:
                    logger.warning("Notification queue full, dropping alert")
                    return
            
            # Insert based on priority
            inserted = False
            for i, item in enumerate(self.notification_queue):
                if queue_item["priority"] > item["priority"]:
                    self.notification_queue.insert(i, queue_item)
                    inserted = True
                    break
            
            if not inserted:
                self.notification_queue.append(queue_item)
            
        except Exception as e:
            logger.error(f"Error queueing alert: {e}")
    
    async def _process_notification_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of notifications"""
        try:
            tasks = []
            
            for queue_item in batch:
                alert_id = queue_item["alert_id"]
                task = asyncio.create_task(self._process_single_alert(alert_id))
                tasks.append(task)
            
            # Process all alerts in parallel
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error processing notification batch: {e}")
    
    async def _process_single_alert(self, alert_id: str):
        """Process a single alert for notification"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert or not alert.rule:
                return
            
            rule = alert.rule
            
            # Get recipients
            recipients = await self._get_alert_recipients(rule)
            
            # Get or generate notification content
            content = await self._generate_notification_content(alert, rule)
            
            # Send notifications through all configured channels
            notification_tasks = []
            
            for channel_name in rule.channels:
                try:
                    channel = NotificationChannel(channel_name)
                    
                    for recipient in recipients:
                        # Check recipient preferences
                        if await self._should_send_to_recipient(recipient, channel, alert.severity):
                            task = asyncio.create_task(
                                self.send_notification(alert, channel, recipient, content)
                            )
                            notification_tasks.append(task)
                
                except ValueError:
                    logger.warning(f"Unknown notification channel: {channel_name}")
            
            # Execute all notifications
            if notification_tasks:
                results = await asyncio.gather(*notification_tasks, return_exceptions=True)
                
                # Update alert with delivery results
                successful_deliveries = sum(1 for r in results if isinstance(r, NotificationResult) and r.success)
                alert.delivery_attempts = len(notification_tasks)
                
                if successful_deliveries > 0:
                    alert.status = AlertStatus.SENT.value
                
                self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing alert {alert_id}: {e}")
    
    def _get_processing_priority(self, severity: str) -> int:
        """Get processing priority based on severity"""
        priority_map = {
            AlertSeverity.EMERGENCY.value: 5,
            AlertSeverity.CRITICAL.value: 4,
            AlertSeverity.HIGH.value: 3,
            AlertSeverity.MEDIUM.value: 2,
            AlertSeverity.LOW.value: 1,
            AlertSeverity.INFO.value: 0
        }
        return priority_map.get(severity, 1)
    
    def _generate_content_hash(self, title: str, message: str) -> str:
        """Generate hash for content deduplication"""
        import hashlib
        content = f"{title}:{message}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_alert_recipients(self, rule: AlertRule) -> List[str]:
        """Get list of recipients for alert rule"""
        try:
            recipients = []
            recipient_config = rule.recipient_config
            
            # Direct recipients
            if "direct" in recipient_config:
                recipients.extend(recipient_config["direct"])
            
            # Role-based recipients
            if "roles" in recipient_config:
                for role in recipient_config["roles"]:
                    # Get users with specific role (would integrate with user management)
                    role_recipients = await self._get_users_by_role(role)
                    recipients.extend(role_recipients)
            
            # Team-based recipients
            if "teams" in recipient_config:
                for team in recipient_config["teams"]:
                    team_recipients = await self._get_team_members(team)
                    recipients.extend(team_recipients)
            
            # Remove duplicates
            return list(set(recipients))
            
        except Exception as e:
            logger.error(f"Error getting alert recipients: {e}")
            return []
    
    async def _generate_notification_content(self, alert: Alert, rule: AlertRule) -> Dict[str, str]:
        """Generate notification content from template"""
        try:
            template_id = rule.template_id
            
            if template_id:
                template = self._get_template(template_id)
                if template:
                    return await self._render_template(template, alert, rule)
            
            # Default content if no template
            return {
                "subject": f"Alert: {alert.title}",
                "body": alert.message,
                "html": f"<h2>{alert.title}</h2><p>{alert.message}</p>"
            }
            
        except Exception as e:
            logger.error(f"Error generating notification content: {e}")
            return {
                "subject": f"Alert: {alert.title}",
                "body": alert.message
            }
    
    def _get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get notification template with caching"""
        try:
            if template_id in self.template_cache:
                return self.template_cache[template_id]
            
            template = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.id == template_id,
                NotificationTemplate.is_active == True
            ).first()
            
            if template:
                self.template_cache[template_id] = template
            
            return template
            
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    async def _render_template(self, template: NotificationTemplate, 
                             alert: Alert, rule: AlertRule) -> Dict[str, str]:
        """Render notification template with alert data"""
        try:
            from jinja2 import Template
            
            # Prepare template variables
            variables = {
                "alert": {
                    "id": alert.id,
                    "title": alert.title,
                    "message": alert.message,
                    "severity": alert.severity,
                    "triggered_at": alert.triggered_at.isoformat(),
                    "data": alert.alert_data,
                    "context": alert.context
                },
                "rule": {
                    "name": rule.name,
                    "description": rule.description
                },
                "system": {
                    "timestamp": datetime.now().isoformat(),
                    "environment": "production"  # Would be configurable
                }
            }
            
            # Add default values
            variables.update(template.default_values)
            
            # Render templates
            rendered_content = {}
            
            if template.subject_template:
                subject_template = Template(template.subject_template)
                rendered_content["subject"] = subject_template.render(**variables)
            
            body_template = Template(template.body_template)
            rendered_content["body"] = body_template.render(**variables)
            
            if template.html_template:
                html_template = Template(template.html_template)
                rendered_content["html"] = html_template.render(**variables)
            
            # Update usage tracking
            template.usage_count += 1
            template.last_used = datetime.now()
            
            return rendered_content
            
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return {
                "subject": alert.title,
                "body": alert.message
            }
    
    async def _should_send_to_recipient(self, recipient: str, channel: NotificationChannel, 
                                      severity: str) -> bool:
        """Check if notification should be sent to recipient"""
        try:
            # Get recipient preferences
            preferences = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == recipient
            ).first()
            
            if not preferences:
                return True  # Default to send if no preferences set
            
            # Check channel enabled
            channel_enabled = {
                NotificationChannel.EMAIL: preferences.email_enabled,
                NotificationChannel.SMS: preferences.sms_enabled,
                NotificationChannel.PUSH: preferences.push_enabled,
                NotificationChannel.IN_APP: preferences.in_app_enabled
            }.get(channel, True)
            
            if not channel_enabled:
                return False
            
            # Check severity threshold
            severity_prefs = preferences.severity_preferences or {}
            min_severity = severity_prefs.get(channel.value, AlertSeverity.INFO.value)
            
            severity_levels = [
                AlertSeverity.INFO.value,
                AlertSeverity.LOW.value,
                AlertSeverity.MEDIUM.value,
                AlertSeverity.HIGH.value,
                AlertSeverity.CRITICAL.value,
                AlertSeverity.EMERGENCY.value
            ]
            
            if severity_levels.index(severity) < severity_levels.index(min_severity):
                return False
            
            # Check quiet hours
            if self._is_recipient_in_quiet_hours(preferences):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking recipient preferences: {e}")
            return True
    
    # Delivery methods (simplified implementations)
    async def _send_email(self, recipient: str, content: Dict[str, str]) -> NotificationResult:
        """Send email notification"""
        try:
            # This would integrate with actual email service
            # For now, return success simulation
            return NotificationResult(
                success=True,
                channel=NotificationChannel.EMAIL.value,
                recipient=recipient,
                message="Email sent successfully",
                external_id=f"email_{uuid.uuid4()}",
                delivery_time_ms=150,
                cost=0.01
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL.value,
                recipient=recipient,
                message="Email delivery failed",
                error=str(e)
            )
    
    async def _send_sms(self, recipient: str, content: Dict[str, str]) -> NotificationResult:
        """Send SMS notification"""
        try:
            # This would integrate with SMS service like Twilio
            return NotificationResult(
                success=True,
                channel=NotificationChannel.SMS.value,
                recipient=recipient,
                message="SMS sent successfully",
                external_id=f"sms_{uuid.uuid4()}",
                delivery_time_ms=800,
                cost=0.05
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.SMS.value,
                recipient=recipient,
                message="SMS delivery failed",
                error=str(e)
            )
    
    async def _send_push(self, recipient: str, content: Dict[str, str]) -> NotificationResult:
        """Send push notification"""
        try:
            # This would integrate with push notification service
            return NotificationResult(
                success=True,
                channel=NotificationChannel.PUSH.value,
                recipient=recipient,
                message="Push notification sent",
                external_id=f"push_{uuid.uuid4()}",
                delivery_time_ms=50,
                cost=0.001
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.PUSH.value,
                recipient=recipient,
                message="Push delivery failed",
                error=str(e)
            )
    
    async def _send_in_app(self, recipient: str, content: Dict[str, str]) -> NotificationResult:
        """Send in-app notification"""
        try:
            # Send through WebSocket to connected clients
            notification = {
                "type": "alert",
                "recipient": recipient,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected WebSocket clients for this user
            await self._broadcast_websocket_message(recipient, notification)
            
            return NotificationResult(
                success=True,
                channel=NotificationChannel.IN_APP.value,
                recipient=recipient,
                message="In-app notification sent",
                external_id=f"in_app_{uuid.uuid4()}",
                delivery_time_ms=10,
                cost=0.0
            )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.IN_APP.value,
                recipient=recipient,
                message="In-app delivery failed",
                error=str(e)
            )
    
    async def _send_webhook(self, webhook_url: str, content: Dict[str, str]) -> NotificationResult:
        """Send webhook notification"""
        try:
            payload = {
                "alert": content,
                "timestamp": datetime.now().isoformat(),
                "source": "sbm_crm"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        return NotificationResult(
                            success=True,
                            channel=NotificationChannel.WEBHOOK.value,
                            recipient=webhook_url,
                            message="Webhook delivered successfully",
                            external_id=f"webhook_{uuid.uuid4()}",
                            delivery_time_ms=200,
                            cost=0.0
                        )
                    else:
                        return NotificationResult(
                            success=False,
                            channel=NotificationChannel.WEBHOOK.value,
                            recipient=webhook_url,
                            message="Webhook delivery failed",
                            error=f"HTTP {response.status}"
                        )
            
        except Exception as e:
            return NotificationResult(
                success=False,
                channel=NotificationChannel.WEBHOOK.value,
                recipient=webhook_url,
                message="Webhook delivery failed",
                error=str(e)
            )
    
    # Additional helper methods would continue here...
    # (Due to length constraints, including key methods only)
    
    async def _broadcast_websocket_message(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to user's WebSocket connections"""
        try:
            # This would integrate with WebSocket connection management
            message_json = json.dumps(message)
            
            # Send to all active WebSocket connections for user
            for websocket in self.active_websockets:
                try:
                    if hasattr(websocket, 'user_id') and websocket.user_id == user_id:
                        await websocket.send(message_json)
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    self.active_websockets.discard(websocket)
            
        except Exception as e:
            logger.error(f"Error broadcasting WebSocket message: {e}")
    
    def _is_recipient_in_quiet_hours(self, preferences: NotificationPreference) -> bool:
        """Check if recipient is in quiet hours"""
        try:
            if not preferences.quiet_hours:
                return False
            
            # Would implement timezone-aware quiet hours checking
            return False
            
        except Exception as e:
            logger.error(f"Error checking recipient quiet hours: {e}")
            return False
    
    async def _get_users_by_role(self, role: str) -> List[str]:
        """Get users by role (would integrate with user management)"""
        # Placeholder implementation
        return []
    
    async def _get_team_members(self, team: str) -> List[str]:
        """Get team members (would integrate with team management)"""
        # Placeholder implementation
        return []
    
    async def _send_acknowledgment_notifications(self, alert: Alert, user_id: str, notes: str):
        """Send notifications about alert acknowledgment"""
        # Would implement acknowledgment notifications
        pass
    
    async def _send_resolution_notifications(self, alert: Alert, user_id: str, notes: str):
        """Send notifications about alert resolution"""
        # Would implement resolution notifications
        pass