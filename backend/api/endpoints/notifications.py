"""
Real-time Notifications & Alerts API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...notifications.alert_engine import (
    NotificationEngine,
    AlertSeverity,
    NotificationChannel,
    AlertStatus,
    TriggerType,
    AggregationMethod,
    AlertContext
)

router = APIRouter()

class AlertRuleRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    data_source: Optional[str] = None
    query_config: Dict[str, Any] = {}
    severity: str = AlertSeverity.MEDIUM.value
    channels: List[str]
    template_id: Optional[str] = None
    check_interval_seconds: int = 300
    aggregation_method: str = AggregationMethod.NONE.value
    aggregation_window_seconds: int = 3600
    recipient_config: Dict[str, Any]
    escalation_rules: List[Dict[str, Any]] = []
    rate_limit_count: int = 10
    rate_limit_window_seconds: int = 3600
    quiet_hours: Dict[str, Any] = {}

class NotificationTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    subject_template: Optional[str] = None
    body_template: str
    html_template: Optional[str] = None
    channel: str
    template_variables: List[str] = []
    default_values: Dict[str, Any] = {}
    formatting_options: Dict[str, Any] = {}
    localization: Dict[str, Any] = {}
    category: Optional[str] = None
    tags: List[str] = []

class TriggerAlertRequest(BaseModel):
    rule_id: str
    trigger_data: Dict[str, Any]
    severity: Optional[str] = AlertSeverity.MEDIUM.value
    title: str
    message: str
    additional_context: Dict[str, Any] = {}

class NotificationPreferenceRequest(BaseModel):
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    push_tokens: List[str] = []
    severity_preferences: Dict[str, str] = {}
    quiet_hours: Dict[str, Any] = {}
    timezone: str = "UTC"
    alert_categories: Dict[str, bool] = {}
    frequency_limits: Dict[str, int] = {}
    delivery_options: Dict[str, Any] = {}
    escalation_enabled: bool = True

class NotificationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/alert-rules", response_model=NotificationResponse)
async def create_alert_rule(
    request: AlertRuleRequest,
    current_user: dict = Depends(require_permission("manage_alerts")),
    db: Session = Depends(get_db)
):
    """Create a new alert rule"""
    try:
        notification_engine = NotificationEngine(db)
        
        rule_config = {
            "name": request.name,
            "description": request.description,
            "trigger_type": request.trigger_type,
            "trigger_conditions": request.trigger_conditions,
            "data_source": request.data_source,
            "query_config": request.query_config,
            "severity": request.severity,
            "channels": request.channels,
            "template_id": request.template_id,
            "check_interval_seconds": request.check_interval_seconds,
            "aggregation_method": request.aggregation_method,
            "aggregation_window_seconds": request.aggregation_window_seconds,
            "recipient_config": request.recipient_config,
            "escalation_rules": request.escalation_rules,
            "rate_limit_count": request.rate_limit_count,
            "rate_limit_window_seconds": request.rate_limit_window_seconds,
            "quiet_hours": request.quiet_hours,
            "created_by": current_user.get("username", "unknown")
        }
        
        rule_id = notification_engine.create_alert_rule(rule_config)
        
        return NotificationResponse(
            success=True,
            message="Alert rule created successfully",
            data={"rule_id": rule_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")

@router.get("/alert-rules")
async def list_alert_rules(
    active_only: bool = Query(True),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_alerts")),
    db: Session = Depends(get_db)
):
    """List alert rules"""
    try:
        from ...notifications.alert_engine import AlertRule
        
        query = db.query(AlertRule)
        
        if active_only:
            query = query.filter(AlertRule.is_active == True)
        
        rules = query.order_by(AlertRule.created_at.desc()).offset(offset).limit(limit).all()
        
        rule_data = []
        for rule in rules:
            rule_data.append({
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "trigger_type": rule.trigger_type,
                "severity": rule.severity,
                "channels": rule.channels,
                "is_active": rule.is_active,
                "trigger_count": rule.trigger_count,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None,
                "created_at": rule.created_at.isoformat(),
                "avg_response_time": rule.avg_response_time,
                "false_positive_rate": rule.false_positive_rate
            })
        
        return {
            "rules": rule_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(rule_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list alert rules: {str(e)}")

@router.get("/alert-rules/{rule_id}")
async def get_alert_rule(
    rule_id: str,
    current_user: dict = Depends(require_permission("view_alerts")),
    db: Session = Depends(get_db)
):
    """Get detailed alert rule information"""
    try:
        from ...notifications.alert_engine import AlertRule
        
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        return {
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "trigger_type": rule.trigger_type,
            "trigger_conditions": rule.trigger_conditions,
            "data_source": rule.data_source,
            "query_config": rule.query_config,
            "severity": rule.severity,
            "channels": rule.channels,
            "template_id": rule.template_id,
            "check_interval_seconds": rule.check_interval_seconds,
            "aggregation_method": rule.aggregation_method,
            "aggregation_window_seconds": rule.aggregation_window_seconds,
            "recipient_config": rule.recipient_config,
            "escalation_rules": rule.escalation_rules,
            "rate_limit_count": rule.rate_limit_count,
            "rate_limit_window_seconds": rule.rate_limit_window_seconds,
            "quiet_hours": rule.quiet_hours,
            "is_active": rule.is_active,
            "trigger_count": rule.trigger_count,
            "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None,
            "last_checked": rule.last_checked.isoformat() if rule.last_checked else None,
            "avg_response_time": rule.avg_response_time,
            "false_positive_rate": rule.false_positive_rate,
            "created_by": rule.created_by,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert rule: {str(e)}")

@router.put("/alert-rules/{rule_id}/toggle")
async def toggle_alert_rule(
    rule_id: str,
    current_user: dict = Depends(require_permission("manage_alerts")),
    db: Session = Depends(get_db)
):
    """Toggle alert rule active status"""
    try:
        from ...notifications.alert_engine import AlertRule
        
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        rule.is_active = not rule.is_active
        rule.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Alert rule {'activated' if rule.is_active else 'deactivated'}",
            "is_active": rule.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to toggle alert rule: {str(e)}")

@router.post("/templates", response_model=NotificationResponse)
async def create_notification_template(
    request: NotificationTemplateRequest,
    current_user: dict = Depends(require_permission("manage_alerts")),
    db: Session = Depends(get_db)
):
    """Create a notification template"""
    try:
        notification_engine = NotificationEngine(db)
        
        template_config = {
            "name": request.name,
            "description": request.description,
            "subject_template": request.subject_template,
            "body_template": request.body_template,
            "html_template": request.html_template,
            "channel": request.channel,
            "template_variables": request.template_variables,
            "default_values": request.default_values,
            "formatting_options": request.formatting_options,
            "localization": request.localization,
            "category": request.category,
            "tags": request.tags
        }
        
        template_id = notification_engine.create_notification_template(template_config)
        
        return NotificationResponse(
            success=True,
            message="Notification template created successfully",
            data={"template_id": template_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@router.get("/templates")
async def list_notification_templates(
    channel: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notification templates"""
    try:
        from ...notifications.alert_engine import NotificationTemplate
        
        query = db.query(NotificationTemplate)
        
        if active_only:
            query = query.filter(NotificationTemplate.is_active == True)
        
        if channel:
            query = query.filter(NotificationTemplate.channel == channel)
        
        if category:
            query = query.filter(NotificationTemplate.category == category)
        
        templates = query.order_by(NotificationTemplate.created_at.desc()).all()
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "channel": template.channel,
                "category": template.category,
                "tags": template.tags,
                "template_variables": template.template_variables,
                "usage_count": template.usage_count,
                "last_used": template.last_used.isoformat() if template.last_used else None,
                "is_active": template.is_active,
                "created_at": template.created_at.isoformat()
            })
        
        return {
            "templates": template_data,
            "total": len(template_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")

@router.post("/alerts/trigger", response_model=NotificationResponse)
async def trigger_alert(
    request: TriggerAlertRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger an alert"""
    try:
        notification_engine = NotificationEngine(db)
        
        alert_context = AlertContext(
            rule_id=request.rule_id,
            trigger_data=request.trigger_data,
            severity=AlertSeverity(request.severity),
            title=request.title,
            message=request.message,
            additional_context=request.additional_context
        )
        
        alert_id = await notification_engine.trigger_alert(alert_context)
        
        if alert_id:
            # Start background queue processing
            background_tasks.add_task(notification_engine.process_notification_queue)
            
            return NotificationResponse(
                success=True,
                message="Alert triggered successfully",
                data={"alert_id": alert_id}
            )
        else:
            return NotificationResponse(
                success=False,
                message="Alert was suppressed (rate limited or aggregated)"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger alert: {str(e)}")

@router.get("/alerts")
async def list_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    rule_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_permission("view_alerts")),
    db: Session = Depends(get_db)
):
    """List alerts with filtering options"""
    try:
        from ...notifications.alert_engine import Alert
        
        query = db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if rule_id:
            query = query.filter(Alert.rule_id == rule_id)
        
        if start_date:
            query = query.filter(Alert.triggered_at >= start_date)
        
        if end_date:
            query = query.filter(Alert.triggered_at <= end_date)
        
        alerts = query.order_by(Alert.triggered_at.desc()).offset(offset).limit(limit).all()
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "rule_id": alert.rule_id,
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity,
                "status": alert.status,
                "aggregated_count": alert.aggregated_count,
                "triggered_at": alert.triggered_at.isoformat(),
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "acknowledged_by": alert.acknowledged_by,
                "resolved_by": alert.resolved_by,
                "time_to_acknowledge": alert.time_to_acknowledge,
                "time_to_resolve": alert.time_to_resolve,
                "delivery_attempts": alert.delivery_attempts,
                "successful_deliveries": alert.successful_deliveries,
                "failed_deliveries": alert.failed_deliveries
            })
        
        return {
            "alerts": alert_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(alert_data)
            },
            "filters": {
                "status": status,
                "severity": severity,
                "rule_id": rule_id,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list alerts: {str(e)}")

@router.get("/alerts/{alert_id}")
async def get_alert_details(
    alert_id: str,
    current_user: dict = Depends(require_permission("view_alerts")),
    db: Session = Depends(get_db)
):
    """Get detailed alert information"""
    try:
        from ...notifications.alert_engine import Alert, NotificationDelivery
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Get delivery information
        deliveries = db.query(NotificationDelivery).filter(
            NotificationDelivery.alert_id == alert_id
        ).all()
        
        delivery_data = []
        for delivery in deliveries:
            delivery_data.append({
                "id": delivery.id,
                "channel": delivery.channel,
                "recipient": delivery.recipient,
                "status": delivery.status,
                "attempted_at": delivery.attempted_at.isoformat(),
                "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
                "read_at": delivery.read_at.isoformat() if delivery.read_at else None,
                "clicked_at": delivery.clicked_at.isoformat() if delivery.clicked_at else None,
                "provider": delivery.provider,
                "external_id": delivery.external_id,
                "error_message": delivery.error_message,
                "retry_count": delivery.retry_count,
                "delivery_time_ms": delivery.delivery_time_ms,
                "cost": delivery.cost
            })
        
        return {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "status": alert.status,
            "alert_data": alert.alert_data,
            "context": alert.context,
            "source_data": alert.source_data,
            "aggregated_count": alert.aggregated_count,
            "aggregated_alerts": alert.aggregated_alerts,
            "parent_alert_id": alert.parent_alert_id,
            "triggered_at": alert.triggered_at.isoformat(),
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "resolved_by": alert.resolved_by,
            "resolution_notes": alert.resolution_notes,
            "time_to_acknowledge": alert.time_to_acknowledge,
            "time_to_resolve": alert.time_to_resolve,
            "impact_score": alert.impact_score,
            "delivery_attempts": alert.delivery_attempts,
            "deliveries": delivery_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert details: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(require_permission("manage_alerts")),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    try:
        notification_engine = NotificationEngine(db)
        
        success = await notification_engine.acknowledge_alert(
            alert_id=alert_id,
            user_id=current_user.get("username", "unknown"),
            notes=notes
        )
        
        if success:
            return {
                "success": True,
                "message": "Alert acknowledged successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Alert could not be acknowledged")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(require_permission("manage_alerts")),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    try:
        notification_engine = NotificationEngine(db)
        
        success = await notification_engine.resolve_alert(
            alert_id=alert_id,
            user_id=current_user.get("username", "unknown"),
            notes=notes
        )
        
        if success:
            return {
                "success": True,
                "message": "Alert resolved successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Alert could not be resolved")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.get("/metrics")
async def get_notification_metrics(
    timeframe_hours: int = Query(24, ge=1, le=8760),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get notification system metrics"""
    try:
        notification_engine = NotificationEngine(db)
        metrics = notification_engine.get_alert_metrics(timeframe_hours)
        
        return {
            "timeframe_hours": timeframe_hours,
            "metrics": {
                "total_alerts": metrics.total_alerts,
                "alerts_by_severity": metrics.alerts_by_severity,
                "alerts_by_status": metrics.alerts_by_status,
                "avg_response_time_seconds": metrics.avg_response_time,
                "avg_resolution_time_seconds": metrics.avg_resolution_time,
                "delivery_success_rate_percent": metrics.delivery_success_rate,
                "active_rules": metrics.active_rules
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/dashboard")
async def get_notifications_dashboard(
    timeframe: str = Query("24h", regex="^(1h|6h|24h|7d|30d)$"),
    current_user: dict = Depends(require_permission("view_alerts")),
    db: Session = Depends(get_db)
):
    """Get comprehensive notifications dashboard"""
    try:
        from ...notifications.alert_engine import Alert, AlertRule, NotificationDelivery
        from collections import defaultdict
        
        # Calculate time range
        time_mapping = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        end_time = datetime.now()
        start_time = end_time - time_mapping[timeframe]
        
        # Get alerts in timeframe
        alerts = db.query(Alert).filter(
            Alert.triggered_at.between(start_time, end_time)
        ).all()
        
        # Get deliveries in timeframe
        deliveries = db.query(NotificationDelivery).join(Alert).filter(
            Alert.triggered_at.between(start_time, end_time)
        ).all()
        
        # Calculate overview metrics
        total_alerts = len(alerts)
        active_alerts = len([a for a in alerts if a.status in [AlertStatus.PENDING.value, AlertStatus.ACKNOWLEDGED.value]])
        
        # Severity distribution
        severity_counts = defaultdict(int)
        for alert in alerts:
            severity_counts[alert.severity] += 1
        
        # Status distribution
        status_counts = defaultdict(int)
        for alert in alerts:
            status_counts[alert.status] += 1
        
        # Channel performance
        channel_stats = defaultdict(lambda: {"total": 0, "delivered": 0, "failed": 0})
        for delivery in deliveries:
            stats = channel_stats[delivery.channel]
            stats["total"] += 1
            if delivery.status == AlertStatus.DELIVERED.value:
                stats["delivered"] += 1
            elif delivery.status == AlertStatus.FAILED.value:
                stats["failed"] += 1
        
        # Calculate delivery rates
        channel_performance = {}
        for channel, stats in channel_stats.items():
            success_rate = (stats["delivered"] / max(1, stats["total"])) * 100
            channel_performance[channel] = {
                "total_deliveries": stats["total"],
                "successful_deliveries": stats["delivered"],
                "failed_deliveries": stats["failed"],
                "success_rate": success_rate
            }
        
        # Top alert rules
        rule_counts = defaultdict(int)
        for alert in alerts:
            rule_counts[alert.rule_id] += 1
        
        top_rules = []
        for rule_id, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
            if rule:
                top_rules.append({
                    "rule_id": rule_id,
                    "rule_name": rule.name,
                    "alert_count": count,
                    "severity": rule.severity
                })
        
        # Time series data
        daily_alerts = defaultdict(int)
        for alert in alerts:
            day = alert.triggered_at.date().isoformat()
            daily_alerts[day] += 1
        
        # Response time analysis
        response_times = [a.time_to_acknowledge for a in alerts if a.time_to_acknowledge]
        resolution_times = [a.time_to_resolve for a in alerts if a.time_to_resolve]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # System health indicators
        failed_deliveries = len([d for d in deliveries if d.status == AlertStatus.FAILED.value])
        total_deliveries = len(deliveries)
        overall_delivery_rate = ((total_deliveries - failed_deliveries) / max(1, total_deliveries)) * 100
        
        # Active rules
        active_rules = db.query(AlertRule).filter(AlertRule.is_active == True).count()
        total_rules = db.query(AlertRule).count()
        
        return {
            "timeframe": timeframe,
            "analysis_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "overview_metrics": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "resolved_alerts": status_counts.get(AlertStatus.RESOLVED.value, 0),
                "critical_alerts": severity_counts.get(AlertSeverity.CRITICAL.value, 0) + 
                                 severity_counts.get(AlertSeverity.EMERGENCY.value, 0),
                "avg_response_time_minutes": avg_response_time / 60 if avg_response_time else 0,
                "avg_resolution_time_minutes": avg_resolution_time / 60 if avg_resolution_time else 0,
                "overall_delivery_rate": overall_delivery_rate
            },
            "alert_distribution": {
                "by_severity": dict(severity_counts),
                "by_status": dict(status_counts)
            },
            "channel_performance": channel_performance,
            "top_alert_rules": top_rules,
            "time_series": {
                "daily_alerts": dict(daily_alerts)
            },
            "system_health": {
                "active_rules": active_rules,
                "total_rules": total_rules,
                "rule_utilization_rate": (active_rules / max(1, total_rules)) * 100,
                "total_deliveries": total_deliveries,
                "failed_deliveries": failed_deliveries,
                "delivery_success_rate": overall_delivery_rate
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@router.post("/preferences", response_model=NotificationResponse)
async def create_notification_preferences(
    request: NotificationPreferenceRequest,
    current_user: dict = Depends(require_permission("manage_preferences")),
    db: Session = Depends(get_db)
):
    """Create or update notification preferences for a user"""
    try:
        from ...notifications.alert_engine import NotificationPreference
        
        # Check if preferences already exist
        existing = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == request.user_id
        ).first()
        
        if existing:
            # Update existing preferences
            existing.email_enabled = request.email_enabled
            existing.sms_enabled = request.sms_enabled
            existing.push_enabled = request.push_enabled
            existing.in_app_enabled = request.in_app_enabled
            existing.email_address = request.email_address
            existing.phone_number = request.phone_number
            existing.push_tokens = request.push_tokens
            existing.severity_preferences = request.severity_preferences
            existing.quiet_hours = request.quiet_hours
            existing.timezone = request.timezone
            existing.alert_categories = request.alert_categories
            existing.frequency_limits = request.frequency_limits
            existing.delivery_options = request.delivery_options
            existing.escalation_enabled = request.escalation_enabled
            existing.updated_at = datetime.now()
            
            message = "Notification preferences updated successfully"
        else:
            # Create new preferences
            preferences = NotificationPreference(
                user_id=request.user_id,
                email_enabled=request.email_enabled,
                sms_enabled=request.sms_enabled,
                push_enabled=request.push_enabled,
                in_app_enabled=request.in_app_enabled,
                email_address=request.email_address,
                phone_number=request.phone_number,
                push_tokens=request.push_tokens,
                severity_preferences=request.severity_preferences,
                quiet_hours=request.quiet_hours,
                timezone=request.timezone,
                alert_categories=request.alert_categories,
                frequency_limits=request.frequency_limits,
                delivery_options=request.delivery_options,
                escalation_enabled=request.escalation_enabled
            )
            
            db.add(preferences)
            message = "Notification preferences created successfully"
        
        db.commit()
        
        return NotificationResponse(
            success=True,
            message=message,
            data={"user_id": request.user_id}
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save preferences: {str(e)}")

@router.get("/preferences/{user_id}")
async def get_notification_preferences(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for a user"""
    try:
        from ...notifications.alert_engine import NotificationPreference
        
        # Users can only access their own preferences unless they have admin permission
        if user_id != current_user.get("username") and not current_user.get("permissions", {}).get("manage_preferences"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        preferences = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not preferences:
            # Return default preferences
            return {
                "user_id": user_id,
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "in_app_enabled": True,
                "email_address": None,
                "phone_number": None,
                "push_tokens": [],
                "severity_preferences": {},
                "quiet_hours": {},
                "timezone": "UTC",
                "alert_categories": {},
                "frequency_limits": {},
                "delivery_options": {},
                "escalation_enabled": True,
                "created_at": None,
                "updated_at": None
            }
        
        return {
            "user_id": preferences.user_id,
            "email_enabled": preferences.email_enabled,
            "sms_enabled": preferences.sms_enabled,
            "push_enabled": preferences.push_enabled,
            "in_app_enabled": preferences.in_app_enabled,
            "email_address": preferences.email_address,
            "phone_number": preferences.phone_number,
            "push_tokens": preferences.push_tokens,
            "severity_preferences": preferences.severity_preferences,
            "quiet_hours": preferences.quiet_hours,
            "timezone": preferences.timezone,
            "alert_categories": preferences.alert_categories,
            "frequency_limits": preferences.frequency_limits,
            "delivery_options": preferences.delivery_options,
            "escalation_enabled": preferences.escalation_enabled,
            "created_at": preferences.created_at.isoformat() if preferences.created_at else None,
            "updated_at": preferences.updated_at.isoformat() if preferences.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")

@router.get("/channels")
async def get_notification_channels(
    current_user: dict = Depends(get_current_user)
):
    """Get available notification channels and their capabilities"""
    return {
        "channels": [
            {
                "id": NotificationChannel.EMAIL.value,
                "name": "Email",
                "description": "Email notifications with rich HTML content",
                "supports_html": True,
                "supports_attachments": True,
                "delivery_time": "1-5 minutes",
                "cost_per_message": 0.01
            },
            {
                "id": NotificationChannel.SMS.value,
                "name": "SMS",
                "description": "Text message notifications",
                "supports_html": False,
                "supports_attachments": False,
                "delivery_time": "1-30 seconds",
                "cost_per_message": 0.05
            },
            {
                "id": NotificationChannel.PUSH.value,
                "name": "Push Notification",
                "description": "Mobile and browser push notifications",
                "supports_html": False,
                "supports_attachments": False,
                "delivery_time": "1-10 seconds",
                "cost_per_message": 0.001
            },
            {
                "id": NotificationChannel.IN_APP.value,
                "name": "In-App",
                "description": "Real-time in-application notifications",
                "supports_html": True,
                "supports_attachments": False,
                "delivery_time": "Instant",
                "cost_per_message": 0.0
            },
            {
                "id": NotificationChannel.WEBHOOK.value,
                "name": "Webhook",
                "description": "HTTP webhook for system integrations",
                "supports_html": False,
                "supports_attachments": False,
                "delivery_time": "1-5 seconds",
                "cost_per_message": 0.0
            }
        ],
        "severity_levels": [
            {
                "id": AlertSeverity.INFO.value,
                "name": "Info",
                "description": "Informational messages",
                "color": "#2196F3"
            },
            {
                "id": AlertSeverity.LOW.value,
                "name": "Low",
                "description": "Low priority alerts",
                "color": "#4CAF50"
            },
            {
                "id": AlertSeverity.MEDIUM.value,
                "name": "Medium",
                "description": "Medium priority alerts",
                "color": "#FF9800"
            },
            {
                "id": AlertSeverity.HIGH.value,
                "name": "High",
                "description": "High priority alerts",
                "color": "#FF5722"
            },
            {
                "id": AlertSeverity.CRITICAL.value,
                "name": "Critical",
                "description": "Critical system alerts",
                "color": "#F44336"
            },
            {
                "id": AlertSeverity.EMERGENCY.value,
                "name": "Emergency",
                "description": "Emergency alerts requiring immediate attention",
                "color": "#9C27B0"
            }
        ]
    }