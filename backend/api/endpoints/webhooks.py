"""
Webhook Integration API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...webhooks.webhook_engine import (
    WebhookEngine,
    EventType,
    DeliveryMethod,
    WebhookStatus
)

router = APIRouter()

class WebhookEndpointRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    url: HttpUrl
    secret_key: Optional[str] = None
    event_types: List[str] = []
    event_filters: Dict[str, Any] = {}
    delivery_method: str = DeliveryMethod.HTTP_POST.value
    headers: Dict[str, str] = {}
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_seconds: int = 60
    rate_limit_per_minute: int = 100
    tags: List[str] = []

class WebhookIntegrationRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    integration_type: str  # zapier, slack, discord, custom
    config: Dict[str, Any] = {}
    auth_config: Dict[str, Any] = {}
    mapping_config: Dict[str, Any] = {}
    sync_frequency_minutes: int = 60
    tags: List[str] = []

class TriggerEventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

class WebhookResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/endpoints", response_model=WebhookResponse)
async def create_webhook_endpoint(
    request: WebhookEndpointRequest,
    current_user: dict = Depends(require_permission("manage_webhooks")),
    db: Session = Depends(get_db)
):
    """Create a new webhook endpoint"""
    try:
        webhook_engine = WebhookEngine(db)
        
        endpoint_config = {
            "name": request.name,
            "description": request.description,
            "url": str(request.url),
            "secret_key": request.secret_key,
            "event_types": request.event_types,
            "event_filters": request.event_filters,
            "delivery_method": request.delivery_method,
            "headers": request.headers,
            "timeout_seconds": request.timeout_seconds,
            "retry_attempts": request.retry_attempts,
            "retry_backoff_seconds": request.retry_backoff_seconds,
            "rate_limit_per_minute": request.rate_limit_per_minute,
            "created_by": current_user.get("username", "unknown"),
            "tags": request.tags
        }
        
        endpoint_id = webhook_engine.register_endpoint(endpoint_config)
        
        return WebhookResponse(
            success=True,
            message="Webhook endpoint created successfully",
            data={"endpoint_id": endpoint_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create webhook endpoint: {str(e)}")

@router.get("/endpoints")
async def list_webhook_endpoints(
    active_only: bool = Query(True),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_webhooks")),
    db: Session = Depends(get_db)
):
    """List webhook endpoints"""
    try:
        from ...webhooks.webhook_engine import WebhookEndpoint
        
        query = db.query(WebhookEndpoint)
        
        if active_only:
            query = query.filter(WebhookEndpoint.is_active == True)
        
        endpoints = query.order_by(WebhookEndpoint.created_at.desc()).offset(offset).limit(limit).all()
        
        endpoint_data = []
        for endpoint in endpoints:
            endpoint_data.append({
                "id": endpoint.id,
                "name": endpoint.name,
                "description": endpoint.description,
                "url": endpoint.url,
                "event_types": endpoint.event_types,
                "delivery_method": endpoint.delivery_method,
                "is_active": endpoint.is_active,
                "total_deliveries": endpoint.total_deliveries,
                "successful_deliveries": endpoint.successful_deliveries,
                "failed_deliveries": endpoint.failed_deliveries,
                "last_delivery_attempt": endpoint.last_delivery_attempt.isoformat() if endpoint.last_delivery_attempt else None,
                "last_successful_delivery": endpoint.last_successful_delivery.isoformat() if endpoint.last_successful_delivery else None,
                "rate_limit_per_minute": endpoint.rate_limit_per_minute,
                "created_at": endpoint.created_at.isoformat(),
                "tags": endpoint.tags
            })
        
        return {
            "endpoints": endpoint_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(endpoint_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list webhook endpoints: {str(e)}")

@router.get("/endpoints/{endpoint_id}")
async def get_webhook_endpoint(
    endpoint_id: str,
    current_user: dict = Depends(require_permission("view_webhooks")),
    db: Session = Depends(get_db)
):
    """Get detailed webhook endpoint information"""
    try:
        from ...webhooks.webhook_engine import WebhookEndpoint
        
        endpoint = db.query(WebhookEndpoint).filter(WebhookEndpoint.id == endpoint_id).first()
        
        if not endpoint:
            raise HTTPException(status_code=404, detail="Webhook endpoint not found")
        
        webhook_engine = WebhookEngine(db)
        metrics = webhook_engine.get_endpoint_metrics(endpoint_id)
        
        return {
            "id": endpoint.id,
            "name": endpoint.name,
            "description": endpoint.description,
            "url": endpoint.url,
            "event_types": endpoint.event_types,
            "event_filters": endpoint.event_filters,
            "delivery_method": endpoint.delivery_method,
            "headers": endpoint.headers,
            "timeout_seconds": endpoint.timeout_seconds,
            "retry_attempts": endpoint.retry_attempts,
            "retry_backoff_seconds": endpoint.retry_backoff_seconds,
            "rate_limit_per_minute": endpoint.rate_limit_per_minute,
            "is_active": endpoint.is_active,
            "metrics": metrics,
            "created_by": endpoint.created_by,
            "created_at": endpoint.created_at.isoformat(),
            "updated_at": endpoint.updated_at.isoformat(),
            "tags": endpoint.tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get webhook endpoint: {str(e)}")

@router.put("/endpoints/{endpoint_id}/toggle")
async def toggle_webhook_endpoint(
    endpoint_id: str,
    current_user: dict = Depends(require_permission("manage_webhooks")),
    db: Session = Depends(get_db)
):
    """Toggle webhook endpoint active status"""
    try:
        from ...webhooks.webhook_engine import WebhookEndpoint
        
        endpoint = db.query(WebhookEndpoint).filter(WebhookEndpoint.id == endpoint_id).first()
        
        if not endpoint:
            raise HTTPException(status_code=404, detail="Webhook endpoint not found")
        
        endpoint.is_active = not endpoint.is_active
        endpoint.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Webhook endpoint {'activated' if endpoint.is_active else 'deactivated'}",
            "is_active": endpoint.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to toggle webhook endpoint: {str(e)}")

@router.post("/integrations", response_model=WebhookResponse)
async def create_webhook_integration(
    request: WebhookIntegrationRequest,
    current_user: dict = Depends(require_permission("manage_webhooks")),
    db: Session = Depends(get_db)
):
    """Create a webhook integration"""
    try:
        webhook_engine = WebhookEngine(db)
        
        integration_config = {
            "name": request.name,
            "description": request.description,
            "integration_type": request.integration_type,
            "config": request.config,
            "auth_config": request.auth_config,
            "mapping_config": request.mapping_config,
            "sync_frequency_minutes": request.sync_frequency_minutes,
            "created_by": current_user.get("username", "unknown"),
            "tags": request.tags
        }
        
        integration_id = webhook_engine.create_integration(integration_config)
        
        return WebhookResponse(
            success=True,
            message="Webhook integration created successfully",
            data={"integration_id": integration_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create webhook integration: {str(e)}")

@router.get("/integrations")
async def list_webhook_integrations(
    integration_type: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: dict = Depends(require_permission("view_webhooks")),
    db: Session = Depends(get_db)
):
    """List webhook integrations"""
    try:
        from ...webhooks.webhook_engine import WebhookIntegration
        
        query = db.query(WebhookIntegration)
        
        if active_only:
            query = query.filter(WebhookIntegration.is_active == True)
        
        if integration_type:
            query = query.filter(WebhookIntegration.integration_type == integration_type)
        
        integrations = query.order_by(WebhookIntegration.created_at.desc()).all()
        
        integration_data = []
        for integration in integrations:
            integration_data.append({
                "id": integration.id,
                "name": integration.name,
                "description": integration.description,
                "integration_type": integration.integration_type,
                "is_active": integration.is_active,
                "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
                "sync_frequency_minutes": integration.sync_frequency_minutes,
                "total_syncs": integration.total_syncs,
                "successful_syncs": integration.successful_syncs,
                "failed_syncs": integration.failed_syncs,
                "success_rate": (integration.successful_syncs / max(1, integration.total_syncs)) * 100,
                "created_at": integration.created_at.isoformat(),
                "tags": integration.tags
            })
        
        return {
            "integrations": integration_data,
            "total": len(integration_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list webhook integrations: {str(e)}")

@router.post("/events/trigger", response_model=WebhookResponse)
async def trigger_webhook_event(
    request: TriggerEventRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("trigger_webhooks")),
    db: Session = Depends(get_db)
):
    """Manually trigger a webhook event"""
    try:
        webhook_engine = WebhookEngine(db)
        
        # Add user context
        context = request.context.copy()
        context.update({
            "triggered_by": current_user.get("username", "unknown"),
            "trigger_source": "manual",
            "trigger_timestamp": datetime.now().isoformat()
        })
        
        event_id = await webhook_engine.trigger_event(
            event_type=request.event_type,
            data=request.data,
            metadata=request.metadata,
            context=context
        )
        
        return WebhookResponse(
            success=True,
            message="Webhook event triggered successfully",
            data={"event_id": event_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger webhook event: {str(e)}")

@router.get("/events")
async def list_webhook_events(
    event_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_webhooks")),
    db: Session = Depends(get_db)
):
    """List webhook events"""
    try:
        from ...webhooks.webhook_engine import WebhookEvent
        
        query = db.query(WebhookEvent)
        
        if event_type:
            query = query.filter(WebhookEvent.event_type == event_type)
        
        if start_date:
            query = query.filter(WebhookEvent.occurred_at >= start_date)
        
        if end_date:
            query = query.filter(WebhookEvent.occurred_at <= end_date)
        
        events = query.order_by(WebhookEvent.occurred_at.desc()).offset(offset).limit(limit).all()
        
        event_data = []
        for event in events:
            event_data.append({
                "id": event.id,
                "event_type": event.event_type,
                "source_entity_type": event.source_entity_type,
                "source_entity_id": event.source_entity_id,
                "processed": event.processed,
                "delivery_count": event.delivery_count,
                "successful_deliveries": event.successful_deliveries,
                "failed_deliveries": event.failed_deliveries,
                "occurred_at": event.occurred_at.isoformat(),
                "processing_started_at": event.processing_started_at.isoformat() if event.processing_started_at else None,
                "processing_completed_at": event.processing_completed_at.isoformat() if event.processing_completed_at else None
            })
        
        return {
            "events": event_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(event_data)
            },
            "filters": {
                "event_type": event_type,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list webhook events: {str(e)}")

@router.get("/deliveries")
async def list_webhook_deliveries(
    endpoint_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_webhooks")),
    db: Session = Depends(get_db)
):
    """List webhook deliveries"""
    try:
        from ...webhooks.webhook_engine import WebhookDelivery
        
        query = db.query(WebhookDelivery)
        
        if endpoint_id:
            query = query.filter(WebhookDelivery.endpoint_id == endpoint_id)
        
        if status:
            query = query.filter(WebhookDelivery.status == status)
        
        if start_date:
            query = query.filter(WebhookDelivery.created_at >= start_date)
        
        if end_date:
            query = query.filter(WebhookDelivery.created_at <= end_date)
        
        deliveries = query.order_by(WebhookDelivery.created_at.desc()).offset(offset).limit(limit).all()
        
        delivery_data = []
        for delivery in deliveries:
            delivery_data.append({
                "id": delivery.id,
                "endpoint_id": delivery.endpoint_id,
                "event_id": delivery.event_id,
                "event_type": delivery.event_type,
                "status": delivery.status,
                "delivery_method": delivery.delivery_method,
                "url": delivery.url,
                "response_status_code": delivery.response_status_code,
                "response_time_ms": delivery.response_time_ms,
                "attempt_number": delivery.attempt_number,
                "max_attempts": delivery.max_attempts,
                "created_at": delivery.created_at.isoformat(),
                "attempted_at": delivery.attempted_at.isoformat() if delivery.attempted_at else None,
                "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                "next_retry_at": delivery.next_retry_at.isoformat() if delivery.next_retry_at else None,
                "error_message": delivery.error_message,
                "error_code": delivery.error_code
            })
        
        return {
            "deliveries": delivery_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(delivery_data)
            },
            "filters": {
                "endpoint_id": endpoint_id,
                "status": status,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list webhook deliveries: {str(e)}")

@router.post("/process-retries")
async def process_webhook_retries(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_permission("manage_webhooks")),
    db: Session = Depends(get_db)
):
    """Process pending webhook retries"""
    try:
        webhook_engine = WebhookEngine(db)
        
        background_tasks.add_task(webhook_engine.process_retries)
        
        return {
            "success": True,
            "message": "Webhook retry processing started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process webhook retries: {str(e)}")

@router.get("/metrics")
async def get_webhook_metrics(
    timeframe_hours: int = Query(24, ge=1, le=8760),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get webhook system metrics"""
    try:
        from ...webhooks.webhook_engine import WebhookEvent, WebhookDelivery, WebhookEndpoint
        from collections import defaultdict
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=timeframe_hours)
        
        # Get events in timeframe
        events = db.query(WebhookEvent).filter(
            WebhookEvent.occurred_at.between(start_time, end_time)
        ).all()
        
        # Get deliveries in timeframe
        deliveries = db.query(WebhookDelivery).filter(
            WebhookDelivery.created_at.between(start_time, end_time)
        ).all()
        
        # Calculate metrics
        total_events = len(events)
        processed_events = len([e for e in events if e.processed])
        
        total_deliveries = len(deliveries)
        successful_deliveries = len([d for d in deliveries if d.status == WebhookStatus.DELIVERED.value])
        failed_deliveries = len([d for d in deliveries if d.status == WebhookStatus.FAILED.value])
        
        # Event type distribution
        event_type_counts = defaultdict(int)
        for event in events:
            event_type_counts[event.event_type] += 1
        
        # Response time analysis
        response_times = [d.response_time_ms for d in deliveries if d.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Active endpoints
        active_endpoints = db.query(WebhookEndpoint).filter(WebhookEndpoint.is_active == True).count()
        total_endpoints = db.query(WebhookEndpoint).count()
        
        return {
            "timeframe_hours": timeframe_hours,
            "analysis_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "event_metrics": {
                "total_events": total_events,
                "processed_events": processed_events,
                "processing_rate": (processed_events / max(1, total_events)) * 100,
                "event_type_distribution": dict(event_type_counts)
            },
            "delivery_metrics": {
                "total_deliveries": total_deliveries,
                "successful_deliveries": successful_deliveries,
                "failed_deliveries": failed_deliveries,
                "success_rate": (successful_deliveries / max(1, total_deliveries)) * 100,
                "avg_response_time_ms": avg_response_time
            },
            "endpoint_metrics": {
                "active_endpoints": active_endpoints,
                "total_endpoints": total_endpoints,
                "utilization_rate": (active_endpoints / max(1, total_endpoints)) * 100
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get webhook metrics: {str(e)}")

@router.get("/event-types")
async def get_available_event_types(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available webhook event types"""
    return {
        "event_types": [
            {
                "id": event_type.value,
                "name": event_type.value.replace("_", " ").replace(".", " - ").title(),
                "description": _get_event_description(event_type),
                "category": _get_event_category(event_type)
            }
            for event_type in EventType
        ],
        "delivery_methods": [
            {
                "id": method.value,
                "name": method.value.replace("_", " ").title(),
                "description": _get_delivery_method_description(method)
            }
            for method in DeliveryMethod
        ]
    }

# Helper functions
def _get_event_description(event_type: EventType) -> str:
    """Get description for event type"""
    descriptions = {
        EventType.CUSTOMER_CREATED: "Triggered when a new customer is created",
        EventType.CUSTOMER_UPDATED: "Triggered when customer information is updated",
        EventType.CUSTOMER_DELETED: "Triggered when a customer is deleted",
        EventType.CAMPAIGN_STARTED: "Triggered when a marketing campaign starts",
        EventType.CAMPAIGN_COMPLETED: "Triggered when a marketing campaign completes",
        EventType.PURCHASE_COMPLETED: "Triggered when a customer completes a purchase",
        EventType.SEGMENT_UPDATED: "Triggered when customer segment membership changes",
        EventType.ALERT_TRIGGERED: "Triggered when system alerts are generated",
        EventType.REPORT_GENERATED: "Triggered when reports are generated",
        EventType.AB_TEST_COMPLETED: "Triggered when A/B tests complete",
        EventType.ATTRIBUTION_CALCULATED: "Triggered when revenue attribution is calculated",
        EventType.BEHAVIOR_EVENT: "Triggered for behavioral tracking events",
        EventType.CUSTOM_EVENT: "Custom events defined by organization"
    }
    return descriptions.get(event_type, "Custom event")

def _get_event_category(event_type: EventType) -> str:
    """Get category for event type"""
    categories = {
        EventType.CUSTOMER_CREATED: "customer",
        EventType.CUSTOMER_UPDATED: "customer",
        EventType.CUSTOMER_DELETED: "customer",
        EventType.CAMPAIGN_STARTED: "marketing",
        EventType.CAMPAIGN_COMPLETED: "marketing",
        EventType.PURCHASE_COMPLETED: "commerce",
        EventType.SEGMENT_UPDATED: "segmentation",
        EventType.ALERT_TRIGGERED: "system",
        EventType.REPORT_GENERATED: "analytics",
        EventType.AB_TEST_COMPLETED: "testing",
        EventType.ATTRIBUTION_CALCULATED: "revenue",
        EventType.BEHAVIOR_EVENT: "behavioral",
        EventType.CUSTOM_EVENT: "custom"
    }
    return categories.get(event_type, "other")

def _get_delivery_method_description(method: DeliveryMethod) -> str:
    """Get description for delivery method"""
    descriptions = {
        DeliveryMethod.HTTP_POST: "HTTP POST request with JSON payload",
        DeliveryMethod.HTTP_PUT: "HTTP PUT request with JSON payload",
        DeliveryMethod.WEBHOOK: "Standard webhook delivery",
        DeliveryMethod.API_CALLBACK: "API callback to specified endpoint"
    }
    return descriptions.get(method, "Custom delivery method")