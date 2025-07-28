"""
Real-time Activity & Performance Monitoring Engine
Live activity feeds, anomaly detection, and performance monitoring for CRM
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict, deque
import numpy as np
import uuid
import time
from concurrent.futures import ThreadPoolExecutor
import websockets

logger = logging.getLogger(__name__)

class ActivityType(Enum):
    CUSTOMER_LOGIN = "customer_login"
    CUSTOMER_SIGNUP = "customer_signup"
    PURCHASE = "purchase"
    SUPPORT_TICKET = "support_ticket"
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    CAMPAIGN_STARTED = "campaign_started"
    LEAD_CREATED = "lead_created"
    LEAD_CONVERTED = "lead_converted"
    PAYMENT_PROCESSED = "payment_processed"
    CHURN_DETECTED = "churn_detected"
    HIGH_VALUE_ACTIVITY = "high_value_activity"
    SYSTEM_ERROR = "system_error"
    ANOMALY_DETECTED = "anomaly_detected"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class RealTimeActivity:
    activity_id: str
    activity_type: ActivityType
    timestamp: datetime
    customer_id: Optional[str]
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any]
    alert_level: AlertLevel
    value: Optional[float]
    location: Optional[str]
    channel: Optional[str]

@dataclass
class PerformanceMetric:
    metric_id: str
    metric_name: str
    metric_type: MetricType
    current_value: float
    previous_value: float
    change_percentage: float
    timestamp: datetime
    target_value: Optional[float]
    threshold_warning: Optional[float]
    threshold_critical: Optional[float]
    trend_direction: str
    metadata: Dict[str, Any]

@dataclass
class AnomalyDetection:
    anomaly_id: str
    anomaly_type: str
    metric_name: str
    detected_at: datetime
    severity: AlertLevel
    expected_value: float
    actual_value: float
    deviation_percentage: float
    description: str
    potential_causes: List[str]
    recommended_actions: List[str]
    auto_resolved: bool

@dataclass
class LiveDashboardData:
    timestamp: datetime
    active_users: int
    activities_last_hour: int
    revenue_today: float
    conversion_rate: float
    system_health: str
    recent_activities: List[RealTimeActivity]
    performance_metrics: List[PerformanceMetric]
    active_campaigns: int
    pending_alerts: int

class RealTimeMonitoringEngine:
    def __init__(self, db: Session):
        self.db = db
        self.activity_buffer = deque(maxlen=1000)  # Keep last 1000 activities
        self.metric_history = defaultdict(lambda: deque(maxlen=100))  # Keep 100 historical values
        self.anomaly_detectors = {}
        self.subscribers = set()  # WebSocket connections
        self.performance_targets = self._load_performance_targets()
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """Start real-time monitoring"""
        self.is_monitoring = True
        
        # Start background monitoring tasks
        await asyncio.gather(
            self._monitor_activities(),
            self._monitor_performance_metrics(),
            self._detect_anomalies(),
            self._broadcast_updates()
        )

    async def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False

    async def track_activity(self, activity_data: Dict[str, Any]) -> str:
        """Track a real-time activity"""
        try:
            activity = RealTimeActivity(
                activity_id=str(uuid.uuid4()),
                activity_type=ActivityType(activity_data["activity_type"]),
                timestamp=activity_data.get("timestamp", datetime.now()),
                customer_id=activity_data.get("customer_id"),
                user_id=activity_data.get("user_id"),
                description=activity_data["description"],
                metadata=activity_data.get("metadata", {}),
                alert_level=AlertLevel(activity_data.get("alert_level", "info")),
                value=activity_data.get("value"),
                location=activity_data.get("location"),
                channel=activity_data.get("channel")
            )
            
            # Add to buffer
            self.activity_buffer.append(activity)
            
            # Check for anomalies in this activity
            await self._check_activity_anomalies(activity)
            
            # Broadcast to subscribers
            await self._broadcast_activity(activity)
            
            logger.info(f"Activity tracked: {activity.activity_type.value} - {activity.description}")
            return activity.activity_id
            
        except Exception as e:
            logger.error(f"Failed to track activity: {e}")
            raise

    async def update_performance_metric(self, metric_data: Dict[str, Any]) -> str:
        """Update a performance metric"""
        try:
            metric_name = metric_data["metric_name"]
            current_value = metric_data["current_value"]
            
            # Get previous value
            previous_values = self.metric_history[metric_name]
            previous_value = previous_values[-1] if previous_values else current_value
            
            # Calculate change
            change_percentage = ((current_value - previous_value) / max(previous_value, 1)) * 100
            
            # Determine trend
            if change_percentage > 5:
                trend_direction = "increasing"
            elif change_percentage < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            metric = PerformanceMetric(
                metric_id=str(uuid.uuid4()),
                metric_name=metric_name,
                metric_type=MetricType(metric_data.get("metric_type", "gauge")),
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=change_percentage,
                timestamp=datetime.now(),
                target_value=metric_data.get("target_value"),
                threshold_warning=metric_data.get("threshold_warning"),
                threshold_critical=metric_data.get("threshold_critical"),
                trend_direction=trend_direction,
                metadata=metric_data.get("metadata", {})
            )
            
            # Add to history
            self.metric_history[metric_name].append(current_value)
            
            # Check for threshold violations
            await self._check_metric_thresholds(metric)
            
            # Broadcast update
            await self._broadcast_metric_update(metric)
            
            return metric.metric_id
            
        except Exception as e:
            logger.error(f"Failed to update metric: {e}")
            raise

    async def get_live_dashboard_data(self) -> LiveDashboardData:
        """Get current live dashboard data"""
        try:
            # Calculate real-time metrics
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Activities in last hour
            recent_activities = [a for a in self.activity_buffer if a.timestamp >= hour_ago]
            activities_last_hour = len(recent_activities)
            
            # Active users (simulated)
            active_users = len(set(a.customer_id for a in recent_activities if a.customer_id))
            
            # Revenue today (simulated)
            revenue_activities = [a for a in recent_activities 
                                if a.activity_type == ActivityType.PURCHASE and a.value]
            revenue_today = sum(a.value for a in revenue_activities)
            
            # Conversion rate (simulated)
            signups = len([a for a in recent_activities if a.activity_type == ActivityType.CUSTOMER_SIGNUP])
            conversions = len([a for a in recent_activities if a.activity_type == ActivityType.LEAD_CONVERTED])
            conversion_rate = (conversions / max(signups, 1)) * 100
            
            # System health
            error_activities = [a for a in recent_activities if a.alert_level == AlertLevel.CRITICAL]
            if len(error_activities) > 5:
                system_health = "degraded"
            elif len(error_activities) > 0:
                system_health = "warning"
            else:
                system_health = "healthy"
            
            # Recent performance metrics
            current_metrics = []
            for metric_name, values in self.metric_history.items():
                if values:
                    current_metrics.append(PerformanceMetric(
                        metric_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        metric_type=MetricType.GAUGE,
                        current_value=values[-1],
                        previous_value=values[-2] if len(values) > 1 else values[-1],
                        change_percentage=0.0,
                        timestamp=now,
                        target_value=self.performance_targets.get(metric_name),
                        threshold_warning=None,
                        threshold_critical=None,
                        trend_direction="stable",
                        metadata={}
                    ))
            
            # Active campaigns and pending alerts (simulated)
            active_campaigns = np.random.randint(3, 8)
            pending_alerts = len([a for a in recent_activities 
                                if a.alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]])
            
            return LiveDashboardData(
                timestamp=now,
                active_users=active_users,
                activities_last_hour=activities_last_hour,
                revenue_today=revenue_today,
                conversion_rate=conversion_rate,
                system_health=system_health,
                recent_activities=list(recent_activities)[-20:],  # Last 20 activities
                performance_metrics=current_metrics,
                active_campaigns=active_campaigns,
                pending_alerts=pending_alerts
            )
            
        except Exception as e:
            logger.error(f"Failed to get live dashboard data: {e}")
            raise

    async def detect_anomaly(self, metric_name: str, current_value: float, 
                           historical_values: List[float]) -> Optional[AnomalyDetection]:
        """Detect anomalies in metrics using statistical analysis"""
        try:
            if len(historical_values) < 10:  # Need sufficient history
                return None
            
            # Calculate statistical thresholds
            mean_value = np.mean(historical_values)
            std_dev = np.std(historical_values)
            
            # Z-score based anomaly detection
            z_score = abs(current_value - mean_value) / max(std_dev, 1)
            
            if z_score > 3:  # 3 sigma rule
                severity = AlertLevel.CRITICAL
                anomaly_type = "statistical_outlier"
            elif z_score > 2:
                severity = AlertLevel.WARNING
                anomaly_type = "statistical_deviation"
            else:
                return None  # No anomaly detected
            
            deviation_percentage = ((current_value - mean_value) / max(mean_value, 1)) * 100
            
            anomaly = AnomalyDetection(
                anomaly_id=str(uuid.uuid4()),
                anomaly_type=anomaly_type,
                metric_name=metric_name,
                detected_at=datetime.now(),
                severity=severity,
                expected_value=mean_value,
                actual_value=current_value,
                deviation_percentage=deviation_percentage,
                description=f"{metric_name} shows {anomaly_type}: {current_value:.2f} vs expected {mean_value:.2f}",
                potential_causes=self._get_potential_causes(metric_name, anomaly_type),
                recommended_actions=self._get_recommended_actions(metric_name, anomaly_type),
                auto_resolved=False
            )
            
            # Track anomaly
            await self.track_activity({
                "activity_type": ActivityType.ANOMALY_DETECTED.value,
                "description": anomaly.description,
                "alert_level": severity.value,
                "metadata": {
                    "metric_name": metric_name,
                    "anomaly_id": anomaly.anomaly_id,
                    "deviation_percentage": deviation_percentage
                }
            })
            
            return anomaly
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for {metric_name}: {e}")
            return None

    async def get_activity_feed(self, limit: int = 50, 
                              activity_types: Optional[List[str]] = None) -> List[RealTimeActivity]:
        """Get recent activity feed"""
        try:
            activities = list(self.activity_buffer)
            
            # Filter by activity types if specified
            if activity_types:
                activities = [a for a in activities if a.activity_type.value in activity_types]
            
            # Sort by timestamp (most recent first)
            activities.sort(key=lambda a: a.timestamp, reverse=True)
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get activity feed: {e}")
            raise

    async def get_performance_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Filter activities within time period
            period_activities = [a for a in self.activity_buffer if a.timestamp >= cutoff_time]
            
            # Calculate summary metrics
            summary = {
                "time_period": f"Last {hours_back} hours",
                "total_activities": len(period_activities),
                "activity_breakdown": {},
                "alert_breakdown": {},
                "top_customers": [],
                "revenue_metrics": {},
                "system_metrics": {},
                "trend_analysis": {}
            }
            
            # Activity type breakdown
            activity_counts = defaultdict(int)
            alert_counts = defaultdict(int)
            customer_activity = defaultdict(int)
            
            for activity in period_activities:
                activity_counts[activity.activity_type.value] += 1
                alert_counts[activity.alert_level.value] += 1
                if activity.customer_id:
                    customer_activity[activity.customer_id] += 1
            
            summary["activity_breakdown"] = dict(activity_counts)
            summary["alert_breakdown"] = dict(alert_counts)
            
            # Top active customers
            top_customers = sorted(customer_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            summary["top_customers"] = [{"customer_id": cid, "activity_count": count} 
                                       for cid, count in top_customers]
            
            # Revenue metrics
            revenue_activities = [a for a in period_activities 
                                if a.activity_type == ActivityType.PURCHASE and a.value]
            summary["revenue_metrics"] = {
                "total_revenue": sum(a.value for a in revenue_activities),
                "transaction_count": len(revenue_activities),
                "avg_transaction_value": np.mean([a.value for a in revenue_activities]) if revenue_activities else 0
            }
            
            # System health metrics
            error_count = len([a for a in period_activities if a.alert_level == AlertLevel.CRITICAL])
            warning_count = len([a for a in period_activities if a.alert_level == AlertLevel.WARNING])
            
            summary["system_metrics"] = {
                "error_rate": (error_count / max(len(period_activities), 1)) * 100,
                "warning_rate": (warning_count / max(len(period_activities), 1)) * 100,
                "uptime_percentage": max(0, 100 - (error_count * 2) - warning_count)
            }
            
            # Trend analysis (compare with previous period)
            prev_cutoff = cutoff_time - timedelta(hours=hours_back)
            prev_activities = [a for a in self.activity_buffer 
                             if prev_cutoff <= a.timestamp < cutoff_time]
            
            current_count = len(period_activities)
            previous_count = len(prev_activities)
            
            if previous_count > 0:
                growth_rate = ((current_count - previous_count) / previous_count) * 100
            else:
                growth_rate = 100 if current_count > 0 else 0
            
            summary["trend_analysis"] = {
                "activity_growth_rate": growth_rate,
                "trend_direction": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable"
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            raise

    # Background monitoring tasks
    async def _monitor_activities(self):
        """Background task to monitor activities"""
        while self.is_monitoring:
            try:
                # Simulate random activities for demonstration
                await self._simulate_random_activity()
                await asyncio.sleep(np.random.uniform(1, 5))  # Random interval
            except Exception as e:
                logger.error(f"Activity monitoring error: {e}")
                await asyncio.sleep(5)

    async def _monitor_performance_metrics(self):
        """Background task to monitor performance metrics"""
        while self.is_monitoring:
            try:
                # Update various performance metrics
                await self._update_system_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)

    async def _detect_anomalies(self):
        """Background task to detect anomalies"""
        while self.is_monitoring:
            try:
                # Check all metrics for anomalies
                for metric_name, values in self.metric_history.items():
                    if len(values) > 10:
                        current_value = values[-1]
                        historical_values = list(values)[:-1]
                        
                        anomaly = await self.detect_anomaly(metric_name, current_value, historical_values)
                        if anomaly:
                            logger.warning(f"Anomaly detected: {anomaly.description}")
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(60)

    async def _broadcast_updates(self):
        """Background task to broadcast updates to subscribers"""
        while self.is_monitoring:
            try:
                if self.subscribers:
                    dashboard_data = await self.get_live_dashboard_data()
                    message = {
                        "type": "dashboard_update",
                        "data": asdict(dashboard_data),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Broadcast to all subscribers
                    await self._broadcast_to_subscribers(message)
                
                await asyncio.sleep(10)  # Broadcast every 10 seconds
            except Exception as e:
                logger.error(f"Broadcasting error: {e}")
                await asyncio.sleep(10)

    # Helper methods
    async def _simulate_random_activity(self):
        """Simulate random activity for demonstration"""
        activity_types = [
            ActivityType.CUSTOMER_LOGIN,
            ActivityType.PURCHASE,
            ActivityType.EMAIL_OPENED,
            ActivityType.LEAD_CREATED,
            ActivityType.SUPPORT_TICKET
        ]
        
        activity_type = np.random.choice(activity_types)
        
        activity_data = {
            "activity_type": activity_type.value,
            "description": f"Simulated {activity_type.value.replace('_', ' ')}",
            "customer_id": f"customer_{np.random.randint(1, 1000)}",
            "alert_level": np.random.choice(["info", "warning", "critical"], p=[0.8, 0.15, 0.05]),
            "metadata": {
                "simulation": True,
                "random_value": np.random.randint(1, 100)
            }
        }
        
        if activity_type == ActivityType.PURCHASE:
            activity_data["value"] = np.random.uniform(50, 500)
        
        await self.track_activity(activity_data)

    async def _update_system_metrics(self):
        """Update system performance metrics"""
        metrics = [
            ("response_time_ms", np.random.uniform(50, 200)),
            ("cpu_usage_percent", np.random.uniform(30, 80)),
            ("memory_usage_percent", np.random.uniform(40, 70)),
            ("active_connections", np.random.randint(100, 500)),
            ("requests_per_minute", np.random.randint(200, 800)),
            ("error_rate_percent", np.random.uniform(0, 5))
        ]
        
        for metric_name, value in metrics:
            await self.update_performance_metric({
                "metric_name": metric_name,
                "current_value": value,
                "metric_type": "gauge"
            })

    async def _check_activity_anomalies(self, activity: RealTimeActivity):
        """Check if an activity represents an anomaly"""
        # Check for unusual activity patterns
        if activity.activity_type == ActivityType.PURCHASE and activity.value and activity.value > 1000:
            await self.track_activity({
                "activity_type": ActivityType.HIGH_VALUE_ACTIVITY.value,
                "description": f"High-value purchase detected: ${activity.value:.2f}",
                "customer_id": activity.customer_id,
                "alert_level": "warning",
                "metadata": {"original_activity_id": activity.activity_id}
            })

    async def _check_metric_thresholds(self, metric: PerformanceMetric):
        """Check if metric violates thresholds"""
        if metric.threshold_critical and metric.current_value > metric.threshold_critical:
            await self.track_activity({
                "activity_type": ActivityType.SYSTEM_ERROR.value,
                "description": f"Critical threshold violated for {metric.metric_name}: {metric.current_value}",
                "alert_level": "critical",
                "metadata": {"metric_id": metric.metric_id}
            })
        elif metric.threshold_warning and metric.current_value > metric.threshold_warning:
            await self.track_activity({
                "activity_type": ActivityType.SYSTEM_ERROR.value,
                "description": f"Warning threshold exceeded for {metric.metric_name}: {metric.current_value}",
                "alert_level": "warning",
                "metadata": {"metric_id": metric.metric_id}
            })

    async def _broadcast_activity(self, activity: RealTimeActivity):
        """Broadcast activity to subscribers"""
        if self.subscribers:
            message = {
                "type": "new_activity",
                "data": asdict(activity),
                "timestamp": datetime.now().isoformat()
            }
            await self._broadcast_to_subscribers(message)

    async def _broadcast_metric_update(self, metric: PerformanceMetric):
        """Broadcast metric update to subscribers"""
        if self.subscribers:
            message = {
                "type": "metric_update",
                "data": asdict(metric),
                "timestamp": datetime.now().isoformat()
            }
            await self._broadcast_to_subscribers(message)

    async def _broadcast_to_subscribers(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket subscribers"""
        if not self.subscribers:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = set()
        
        for websocket in self.subscribers:
            try:
                await websocket.send(message_json)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected subscribers
        self.subscribers -= disconnected

    def _load_performance_targets(self) -> Dict[str, float]:
        """Load performance targets for metrics"""
        return {
            "response_time_ms": 100.0,
            "cpu_usage_percent": 70.0,
            "memory_usage_percent": 80.0,
            "error_rate_percent": 1.0,
            "conversion_rate": 15.0,
            "customer_satisfaction": 4.5
        }

    def _get_potential_causes(self, metric_name: str, anomaly_type: str) -> List[str]:
        """Get potential causes for anomalies"""
        causes_map = {
            "response_time_ms": ["High server load", "Database performance issues", "Network latency"],
            "cpu_usage_percent": ["Resource-intensive processes", "Memory leaks", "Infinite loops"],
            "error_rate_percent": ["Code bugs", "External service failures", "Configuration issues"],
            "conversion_rate": ["Poor user experience", "Technical issues", "Market changes"]
        }
        
        return causes_map.get(metric_name, ["Unknown cause", "System overload", "External factors"])

    def _get_recommended_actions(self, metric_name: str, anomaly_type: str) -> List[str]:
        """Get recommended actions for anomalies"""
        actions_map = {
            "response_time_ms": ["Scale server resources", "Optimize database queries", "Review caching"],
            "cpu_usage_percent": ["Monitor processes", "Restart services", "Scale horizontally"],
            "error_rate_percent": ["Check logs", "Review recent deployments", "Contact development team"],
            "conversion_rate": ["Analyze user feedback", "Review checkout process", "A/B test changes"]
        }
        
        return actions_map.get(metric_name, ["Monitor closely", "Investigate further", "Contact support"])

    # WebSocket connection management
    async def subscribe_to_updates(self, websocket):
        """Add WebSocket subscriber for real-time updates"""
        self.subscribers.add(websocket)
        logger.info(f"New subscriber added. Total subscribers: {len(self.subscribers)}")

    async def unsubscribe_from_updates(self, websocket):
        """Remove WebSocket subscriber"""
        self.subscribers.discard(websocket)
        logger.info(f"Subscriber removed. Total subscribers: {len(self.subscribers)}")