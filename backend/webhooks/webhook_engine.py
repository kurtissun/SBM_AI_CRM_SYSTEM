"""
Webhook Integration System
Handles outbound webhooks, integrations, and event broadcasting
"""
import asyncio
import aiohttp
import json
import hmac
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()
logger = logging.getLogger(__name__)

class WebhookStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    DISABLED = "disabled"
    RETRY = "retry"

class EventType(Enum):
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_DELETED = "customer.deleted"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_COMPLETED = "campaign.completed"
    PURCHASE_COMPLETED = "purchase.completed"
    SEGMENT_UPDATED = "segment.updated"
    ALERT_TRIGGERED = "alert.triggered"
    REPORT_GENERATED = "report.generated"
    AB_TEST_COMPLETED = "ab_test.completed"
    ATTRIBUTION_CALCULATED = "attribution.calculated"
    BEHAVIOR_EVENT = "behavior.event"
    CUSTOM_EVENT = "custom.event"

class DeliveryMethod(Enum):
    HTTP_POST = "http_post"
    HTTP_PUT = "http_put"
    WEBHOOK = "webhook"
    API_CALLBACK = "api_callback"

@dataclass
class WebhookPayload:
    event_type: str
    event_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = None
    version: str = "1.0"

class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    url = Column(String, nullable=False)
    secret_key = Column(String)  # For signature verification
    
    # Event configuration
    event_types = Column(JSON)  # List of event types to listen for
    event_filters = Column(JSON)  # Additional filtering criteria
    
    # Delivery settings
    delivery_method = Column(String, default=DeliveryMethod.HTTP_POST.value)
    headers = Column(JSON)  # Custom headers
    timeout_seconds = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    retry_backoff_seconds = Column(Integer, default=60)
    
    # Status and configuration
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=100)
    last_delivery_attempt = Column(DateTime)
    last_successful_delivery = Column(DateTime)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    tags = Column(JSON)

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String, nullable=False)
    event_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    
    # Delivery details
    status = Column(String, default=WebhookStatus.PENDING.value)
    delivery_method = Column(String)
    url = Column(String)
    payload = Column(JSON)
    headers = Column(JSON)
    
    # Response details
    response_status_code = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(Text)
    response_time_ms = Column(Float)
    
    # Retry and timing
    attempt_number = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)
    next_retry_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    attempted_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Error tracking
    error_message = Column(Text)
    error_code = Column(String)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    source_entity_type = Column(String)  # customer, campaign, etc.
    source_entity_id = Column(String)
    
    # Event data
    event_data = Column(JSON)
    event_metadata = Column(JSON)
    context = Column(JSON)  # Additional context like user_id, session_id
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    delivery_count = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    # Timestamps
    occurred_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

class WebhookIntegration(Base):
    __tablename__ = "webhook_integrations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    integration_type = Column(String)  # zapier, slack, discord, custom
    
    # Configuration
    config = Column(JSON)  # Integration-specific configuration
    auth_config = Column(JSON)  # Authentication details
    mapping_config = Column(JSON)  # Data mapping configuration
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_frequency_minutes = Column(Integer, default=60)
    
    # Metrics
    total_syncs = Column(Integer, default=0)
    successful_syncs = Column(Integer, default=0)
    failed_syncs = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    tags = Column(JSON)

class WebhookEngine:
    def __init__(self, db: Session):
        self.db = db
        self.session = aiohttp.ClientSession()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.rate_limiters: Dict[str, Dict] = {}
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    def register_endpoint(self, endpoint_config: Dict[str, Any]) -> str:
        """Register a new webhook endpoint"""
        try:
            endpoint = WebhookEndpoint(
                name=endpoint_config["name"],
                description=endpoint_config.get("description", ""),
                url=endpoint_config["url"],
                secret_key=endpoint_config.get("secret_key"),
                event_types=endpoint_config.get("event_types", []),
                event_filters=endpoint_config.get("event_filters", {}),
                delivery_method=endpoint_config.get("delivery_method", DeliveryMethod.HTTP_POST.value),
                headers=endpoint_config.get("headers", {}),
                timeout_seconds=endpoint_config.get("timeout_seconds", 30),
                retry_attempts=endpoint_config.get("retry_attempts", 3),
                retry_backoff_seconds=endpoint_config.get("retry_backoff_seconds", 60),
                rate_limit_per_minute=endpoint_config.get("rate_limit_per_minute", 100),
                created_by=endpoint_config.get("created_by", "system"),
                tags=endpoint_config.get("tags", [])
            )
            
            self.db.add(endpoint)
            self.db.commit()
            
            logger.info(f"Webhook endpoint registered: {endpoint.name} -> {endpoint.url}")
            return endpoint.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to register webhook endpoint: {e}")
            raise

    async def trigger_event(self, event_type: str, data: Dict[str, Any], 
                          metadata: Dict[str, Any] = None, context: Dict[str, Any] = None) -> str:
        """Trigger a webhook event"""
        try:
            # Create event record
            event = WebhookEvent(
                event_type=event_type,
                source_entity_type=data.get("entity_type"),
                source_entity_id=data.get("entity_id"),
                event_data=data,
                event_metadata=metadata or {},
                context=context or {}
            )
            
            self.db.add(event)
            self.db.commit()
            
            # Process event asynchronously
            await self._process_event(event)
            
            logger.info(f"Webhook event triggered: {event_type} - {event.id}")
            return event.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to trigger webhook event: {e}")
            raise

    async def _process_event(self, event: WebhookEvent):
        """Process webhook event and deliver to endpoints"""
        try:
            event.processing_started_at = datetime.now()
            self.db.commit()
            
            # Find matching endpoints
            endpoints = self.db.query(WebhookEndpoint).filter(
                WebhookEndpoint.is_active == True
            ).all()
            
            matching_endpoints = []
            for endpoint in endpoints:
                if self._event_matches_endpoint(event, endpoint):
                    matching_endpoints.append(endpoint)
            
            # Create deliveries
            deliveries = []
            for endpoint in matching_endpoints:
                delivery = await self._create_delivery(event, endpoint)
                deliveries.append(delivery)
            
            # Execute deliveries concurrently
            if deliveries:
                await asyncio.gather(*[
                    self._execute_delivery(delivery) for delivery in deliveries
                ], return_exceptions=True)
            
            # Update event status
            event.processed = True
            event.processing_completed_at = datetime.now()
            event.delivery_count = len(deliveries)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to process webhook event {event.id}: {e}")
            raise

    def _event_matches_endpoint(self, event: WebhookEvent, endpoint: WebhookEndpoint) -> bool:
        """Check if event matches endpoint criteria"""
        # Check event type
        if endpoint.event_types and event.event_type not in endpoint.event_types:
            return False
        
        # Apply additional filters
        if endpoint.event_filters:
            for filter_key, filter_value in endpoint.event_filters.items():
                event_value = event.event_data.get(filter_key)
                if event_value != filter_value:
                    return False
        
        # Check rate limiting
        if not self._check_rate_limit(endpoint):
            return False
        
        return True

    def _check_rate_limit(self, endpoint: WebhookEndpoint) -> bool:
        """Check if endpoint rate limit allows delivery"""
        current_time = datetime.now()
        rate_limit_key = endpoint.id
        
        if rate_limit_key not in self.rate_limiters:
            self.rate_limiters[rate_limit_key] = {
                "count": 0,
                "window_start": current_time
            }
        
        rate_limiter = self.rate_limiters[rate_limit_key]
        
        # Reset window if minute has passed
        if (current_time - rate_limiter["window_start"]).seconds >= 60:
            rate_limiter["count"] = 0
            rate_limiter["window_start"] = current_time
        
        # Check limit
        if rate_limiter["count"] >= endpoint.rate_limit_per_minute:
            return False
        
        rate_limiter["count"] += 1
        return True

    async def _create_delivery(self, event: WebhookEvent, endpoint: WebhookEndpoint) -> WebhookDelivery:
        """Create delivery record"""
        payload = WebhookPayload(
            event_type=event.event_type,
            event_id=event.id,
            timestamp=event.occurred_at,
            data=event.event_data,
            metadata=event.event_metadata
        )
        
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_id=event.id,
            event_type=event.event_type,
            delivery_method=endpoint.delivery_method,
            url=endpoint.url,
            payload=payload.__dict__,
            headers=endpoint.headers or {},
            max_attempts=endpoint.retry_attempts
        )
        
        self.db.add(delivery)
        self.db.commit()
        
        return delivery

    async def _execute_delivery(self, delivery: WebhookDelivery):
        """Execute webhook delivery"""
        try:
            delivery.attempted_at = datetime.now()
            delivery.status = WebhookStatus.PROCESSING.value
            self.db.commit()
            
            # Get endpoint details
            endpoint = self.db.query(WebhookEndpoint).filter(
                WebhookEndpoint.id == delivery.endpoint_id
            ).first()
            
            # Prepare request
            headers = delivery.headers.copy()
            headers["Content-Type"] = "application/json"
            headers["User-Agent"] = "SBM-CRM-Webhook/1.0"
            headers["X-Webhook-Event"] = delivery.event_type
            headers["X-Webhook-Delivery"] = delivery.id
            
            # Add signature if secret key is configured
            if endpoint.secret_key:
                payload_bytes = json.dumps(delivery.payload).encode('utf-8')
                signature = hmac.new(
                    endpoint.secret_key.encode('utf-8'),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            # Execute request
            start_time = datetime.now()
            
            async with self.session.request(
                method=delivery.delivery_method.replace("http_", "").upper(),
                url=delivery.url,
                json=delivery.payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            ) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Update delivery with response
                delivery.response_status_code = response.status
                delivery.response_headers = dict(response.headers)
                delivery.response_body = await response.text()
                delivery.response_time_ms = response_time
                
                if 200 <= response.status < 300:
                    delivery.status = WebhookStatus.DELIVERED.value
                    delivery.delivered_at = datetime.now()
                    
                    # Update endpoint metrics
                    endpoint.successful_deliveries = (endpoint.successful_deliveries or 0) + 1
                    endpoint.last_successful_delivery = datetime.now()
                else:
                    delivery.status = WebhookStatus.FAILED.value
                    delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"
                    
                    # Update endpoint metrics
                    endpoint.failed_deliveries = (endpoint.failed_deliveries or 0) + 1
                
                endpoint.total_deliveries = (endpoint.total_deliveries or 0) + 1
                endpoint.last_delivery_attempt = datetime.now()
                
                self.db.commit()
                
                logger.info(f"Webhook delivered: {delivery.id} -> {response.status}")
                
        except asyncio.TimeoutError:
            await self._handle_delivery_failure(delivery, "Request timeout")
        except Exception as e:
            await self._handle_delivery_failure(delivery, str(e))

    async def _handle_delivery_failure(self, delivery: WebhookDelivery, error_message: str):
        """Handle delivery failure and schedule retry if needed"""
        delivery.status = WebhookStatus.FAILED.value
        delivery.error_message = error_message
        
        # Schedule retry if attempts remaining
        if delivery.attempt_number < delivery.max_attempts:
            endpoint = self.db.query(WebhookEndpoint).filter(
                WebhookEndpoint.id == delivery.endpoint_id
            ).first()
            
            # Calculate next retry time with exponential backoff
            backoff_seconds = endpoint.retry_backoff_seconds * (2 ** (delivery.attempt_number - 1))
            delivery.next_retry_at = datetime.now() + timedelta(seconds=backoff_seconds)
            delivery.status = WebhookStatus.RETRY.value
            
            logger.warning(f"Webhook delivery failed, will retry: {delivery.id} - {error_message}")
        else:
            logger.error(f"Webhook delivery failed permanently: {delivery.id} - {error_message}")
        
        self.db.commit()

    async def process_retries(self):
        """Process pending webhook retries"""
        try:
            current_time = datetime.now()
            
            # Find deliveries ready for retry
            retry_deliveries = self.db.query(WebhookDelivery).filter(
                WebhookDelivery.status == WebhookStatus.RETRY.value,
                WebhookDelivery.next_retry_at <= current_time
            ).all()
            
            for delivery in retry_deliveries:
                delivery.attempt_number += 1
                await self._execute_delivery(delivery)
                
        except Exception as e:
            logger.error(f"Failed to process webhook retries: {e}")

    def get_endpoint_metrics(self, endpoint_id: str) -> Dict[str, Any]:
        """Get metrics for a webhook endpoint"""
        endpoint = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == endpoint_id
        ).first()
        
        if not endpoint:
            raise ValueError(f"Endpoint not found: {endpoint_id}")
        
        # Get recent deliveries
        recent_deliveries = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.endpoint_id == endpoint_id,
            WebhookDelivery.created_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        success_rate = 0
        avg_response_time = 0
        
        if recent_deliveries:
            successful = len([d for d in recent_deliveries if d.status == WebhookStatus.DELIVERED.value])
            success_rate = (successful / len(recent_deliveries)) * 100
            
            response_times = [d.response_time_ms for d in recent_deliveries if d.response_time_ms]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "endpoint_id": endpoint.id,
            "name": endpoint.name,
            "url": endpoint.url,
            "is_active": endpoint.is_active,
            "total_deliveries": endpoint.total_deliveries,
            "successful_deliveries": endpoint.successful_deliveries,
            "failed_deliveries": endpoint.failed_deliveries,
            "success_rate_7d": success_rate,
            "avg_response_time_ms_7d": avg_response_time,
            "last_delivery_attempt": endpoint.last_delivery_attempt.isoformat() if endpoint.last_delivery_attempt else None,
            "last_successful_delivery": endpoint.last_successful_delivery.isoformat() if endpoint.last_successful_delivery else None,
            "recent_deliveries_count": len(recent_deliveries)
        }

    def create_integration(self, integration_config: Dict[str, Any]) -> str:
        """Create a webhook integration"""
        try:
            integration = WebhookIntegration(
                name=integration_config["name"],
                description=integration_config.get("description", ""),
                integration_type=integration_config["integration_type"],
                config=integration_config.get("config", {}),
                auth_config=integration_config.get("auth_config", {}),
                mapping_config=integration_config.get("mapping_config", {}),
                sync_frequency_minutes=integration_config.get("sync_frequency_minutes", 60),
                created_by=integration_config.get("created_by", "system"),
                tags=integration_config.get("tags", [])
            )
            
            self.db.add(integration)
            self.db.commit()
            
            logger.info(f"Webhook integration created: {integration.name}")
            return integration.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create webhook integration: {e}")
            raise

    # Predefined event triggers for common CRM events
    async def trigger_customer_event(self, event_type: str, customer_data: Dict[str, Any]):
        """Trigger customer-related webhook events"""
        await self.trigger_event(
            event_type=event_type,
            data={
                "entity_type": "customer",
                "entity_id": customer_data.get("customer_id"),
                "customer": customer_data
            },
            metadata={
                "source": "crm_system",
                "timestamp": datetime.now().isoformat()
            }
        )

    async def trigger_campaign_event(self, event_type: str, campaign_data: Dict[str, Any]):
        """Trigger campaign-related webhook events"""
        await self.trigger_event(
            event_type=event_type,
            data={
                "entity_type": "campaign",
                "entity_id": campaign_data.get("campaign_id"),
                "campaign": campaign_data
            },
            metadata={
                "source": "campaign_system",
                "timestamp": datetime.now().isoformat()
            }
        )

    async def trigger_revenue_event(self, attribution_data: Dict[str, Any]):
        """Trigger revenue attribution webhook events"""
        await self.trigger_event(
            event_type=EventType.ATTRIBUTION_CALCULATED.value,
            data={
                "entity_type": "attribution",
                "entity_id": attribution_data.get("attribution_id"),
                "attribution": attribution_data
            },
            metadata={
                "source": "revenue_system",
                "timestamp": datetime.now().isoformat()
            }
        )