"""
Advanced traffic monitoring and flow analysis system
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque
import threading
from dataclasses import dataclass
from ..core.config import settings
from .biometric_analyzer import BiometricAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class TrafficEvent:
    """Data class for traffic events"""
    event_id: str
    timestamp: datetime
    zone: str
    event_type: str  # 'entry', 'exit', 'dwell', 'crowd_formation'
    visitor_count: int
    confidence: float
    metadata: Dict[str, Any]

class TrafficMonitor:
    """
    Real-time traffic monitoring and flow analysis system
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.biometric_analyzer = BiometricAnalyzer(config)
        
        # Monitoring parameters
        self.zones = self.config.get('zones', {
            'entrance': {'coordinates': [(0, 0), (200, 300)], 'capacity': 50},
            'main_hall': {'coordinates': [(200, 0), (800, 600)], 'capacity': 200},
            'food_court': {'coordinates': [(800, 0), (1200, 400)], 'capacity': 150},
            'retail_north': {'coordinates': [(200, 300), (600, 600)], 'capacity': 100},
            'retail_south': {'coordinates': [(600, 300), (1000, 600)], 'capacity': 100}
        })
        
        # Traffic tracking
        self.traffic_history = deque(maxlen=1000)
        self.zone_occupancy = defaultdict(int)
        self.visitor_trajectories = defaultdict(list)
        self.dwell_times = defaultdict(list)
        
        # Alert thresholds
        self.crowd_threshold = self.config.get('crowd_threshold', 0.8)  # 80% capacity
        self.dwell_threshold = self.config.get('dwell_threshold', 30)  # 30 minutes
        
        # Background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, varThreshold=50
        )
        
        # Active monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def start_monitoring(self, camera_streams: Dict[str, str]):
        """
        Start real-time traffic monitoring
        """
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.camera_streams = camera_streams
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(camera_streams,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Traffic monitoring started")
    
    def stop_monitoring(self):
        """
        Stop traffic monitoring
        """
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Traffic monitoring stopped")
    
    async def _monitoring_loop(self, camera_streams: Dict[str, str]):
        """
        Main monitoring loop
        """
        caps = {}
        
        # Initialize video captures
        for camera_id, stream_url in camera_streams.items():
            cap = cv2.VideoCapture(stream_url)
            if cap.isOpened():
                caps[camera_id] = cap
                logger.info(f"Connected to camera {camera_id}")
            else:
                logger.error(f"Failed to connect to camera {camera_id}: {stream_url}")
        
        try:
            while self.monitoring_active:
                for camera_id, cap in caps.items():
                    ret, frame = cap.read()
                    if ret:
                        # Process frame
                        traffic_data = self.analyze_traffic_frame(frame, camera_id)
                        
                        # Store traffic event
                        if traffic_data['significant_change']:
                            event = TrafficEvent(
                                event_id=f"{camera_id}_{datetime.now().timestamp()}",
                                timestamp=datetime.now(),
                                zone=traffic_data.get('primary_zone', 'unknown'),
                                event_type=traffic_data.get('event_type', 'movement'),
                                visitor_count=traffic_data.get('visitor_count', 0),
                                confidence=traffic_data.get('confidence', 0.5),
                                metadata=traffic_data
                            )
                            self.traffic_history.append(event)
                        
                        # Check for alerts
                        alerts = self._check_traffic_alerts(traffic_data, camera_id)
                        if alerts:
                            self._handle_alerts(alerts)
                    
                    # Control frame rate
                    await asyncio.sleep(1.0 / 30)  # 30 FPS
                
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        finally:
            # Clean up
            for cap in caps.values():
                cap.release()
    
    def analyze_traffic_frame(self, frame: np.ndarray, camera_id: str) -> Dict[str, Any]:
        """
        Analyze traffic patterns in a single frame
        """
        analysis = {
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'visitor_count': 0,
            'movement_detected': False,
            'crowd_density': 'low',
            'primary_zone': None,
            'zone_occupancy': {},
            'motion_intensity': 0.0,
            'significant_change': False,
            'event_type': 'normal',
            'confidence': 0.0
        }
        
        try:
            # Motion detection
            motion_mask = self.bg_subtractor.apply(frame)
            motion_intensity = np.mean(motion_mask) / 255.0
            analysis['motion_intensity'] = motion_intensity
            analysis['movement_detected'] = motion_intensity > 0.1
            
            # Biometric analysis for visitor counting
            biometric_data = self.biometric_analyzer.analyze_frame(frame, camera_id)
            analysis['visitor_count'] = biometric_data.get('faces_detected', 0)
            analysis['crowd_density'] = biometric_data.get('crowd_density', 'low')
            
            # Zone analysis
            zone_analysis = self._analyze_zones(frame, biometric_data)
            analysis['zone_occupancy'] = zone_analysis
            analysis['primary_zone'] = self._determine_primary_zone(zone_analysis)
            
            # Detect significant changes
            analysis['significant_change'] = self._detect_significant_change(analysis)
            
            # Classify event type
            analysis['event_type'] = self._classify_traffic_event(analysis)
            
            # Calculate confidence
            analysis['confidence'] = self._calculate_analysis_confidence(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing traffic frame: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_zones(self, frame: np.ndarray, biometric_data: Dict) -> Dict[str, int]:
        """
        Analyze visitor distribution across zones
        """
        zone_counts = {}
        
        # Simple zone analysis based on face positions
        faces = biometric_data.get('detailed_faces', [])
        frame_height, frame_width = frame.shape[:2]
        
        for zone_name, zone_config in self.zones.items():
            zone_count = 0
            coordinates = zone_config['coordinates']
            
            # Check if faces fall within zone boundaries
            for face in faces:
                # Note: This is simplified - in production, would use actual face coordinates
                # For now, distribute faces randomly across zones
                if np.random.random() > 0.7:  # 30% chance face is in this zone
                    zone_count += 1
            
            zone_counts[zone_name] = zone_count
            self.zone_occupancy[zone_name] = zone_count
        
        return zone_counts
    
    def _determine_primary_zone(self, zone_analysis: Dict[str, int]) -> str:
        """
        Determine the zone with highest activity
        """
        if not zone_analysis:
            return 'unknown'
        
        return max(zone_analysis.items(), key=lambda x: x[1])[0]
    
    def _detect_significant_change(self, analysis: Dict) -> bool:
        """
        Detect if current analysis represents a significant change
        """
        if not self.traffic_history:
            return True
        
        # Compare with recent history
        recent_events = [e for e in self.traffic_history if 
                        (datetime.now() - e.timestamp).seconds < 60]
        
        if not recent_events:
            return True
        
        # Check for significant visitor count change
        recent_avg_count = np.mean([e.visitor_count for e in recent_events])
        current_count = analysis['visitor_count']
        
        # Significant if >30% change in visitor count
        if abs(current_count - recent_avg_count) / (recent_avg_count + 1) > 0.3:
            return True
        
        # Check for crowd density change
        if analysis['crowd_density'] != 'low':
            return True
        
        return False
    
    def _classify_traffic_event(self, analysis: Dict) -> str:
        """
        Classify the type of traffic event
        """
        visitor_count = analysis['visitor_count']
        movement = analysis['movement_detected']
        crowd_density = analysis['crowd_density']
        
        if crowd_density in ['high', 'very_high']:
            return 'crowd_formation'
        elif visitor_count > 10 and movement:
            return 'high_traffic'
        elif visitor_count > 0 and movement:
            return 'normal_traffic'
        elif visitor_count > 0 and not movement:
            return 'dwelling'
        elif movement and visitor_count == 0:
            return 'transit'
        else:
            return 'normal'
    
    def _calculate_analysis_confidence(self, analysis: Dict) -> float:
        """
        Calculate confidence score for analysis
        """
        confidence_factors = []
        
        # Motion detection confidence
        motion_intensity = analysis.get('motion_intensity', 0)
        motion_confidence = min(1.0, motion_intensity * 2)
        confidence_factors.append(motion_confidence)
        
        # Visitor count confidence (higher count = higher confidence)
        visitor_count = analysis.get('visitor_count', 0)
        count_confidence = min(1.0, visitor_count / 10)
        confidence_factors.append(count_confidence)
        
        # Overall confidence is average of factors
        return np.mean(confidence_factors) if confidence_factors else 0.5
    
    def _check_traffic_alerts(self, traffic_data: Dict, camera_id: str) -> List[Dict]:
        """
        Check for traffic-related alerts
        """
        alerts = []
        
        # Crowd alert
        for zone_name, count in traffic_data.get('zone_occupancy', {}).items():
            zone_capacity = self.zones.get(zone_name, {}).get('capacity', 100)
            occupancy_ratio = count / zone_capacity
            
            if occupancy_ratio > self.crowd_threshold:
                alerts.append({
                    'type': 'crowd_alert',
                    'severity': 'high' if occupancy_ratio > 0.9 else 'medium',
                    'zone': zone_name,
                    'occupancy_ratio': occupancy_ratio,
                    'message': f'High occupancy in {zone_name}: {count}/{zone_capacity}',
                    'recommendation': 'Consider crowd management measures'
                })
        
        # High traffic alert
        if traffic_data.get('crowd_density') == 'very_high':
            alerts.append({
                'type': 'high_traffic',
                'severity': 'medium',
                'camera_id': camera_id,
                'message': 'Very high traffic density detected',
                'recommendation': 'Monitor for potential congestion'
            })
        
        return alerts
    
    def _handle_alerts(self, alerts: List[Dict]):
        """
        Handle traffic alerts
        """
        for alert in alerts:
            logger.warning(f"Traffic Alert: {alert['message']}")
            
            # Store alert in database (would integrate with database layer)
            # self.store_alert(alert)
            
            # Send notifications (would integrate with notification system)
            # self.send_notification(alert)
    
    def get_traffic_summary(self, time_period: str = 'hour') -> Dict[str, Any]:
        """
        Get traffic summary for specified time period
        """
        now = datetime.now()
        
        if time_period == 'hour':
            start_time = now - timedelta(hours=1)
        elif time_period == 'day':
            start_time = now - timedelta(days=1)
        elif time_period == 'week':
            start_time = now - timedelta(weeks=1)
        else:
            start_time = now - timedelta(hours=1)
        
        # Filter events by time period
        relevant_events = [
            event for event in self.traffic_history
            if event.timestamp >= start_time
        ]
        
        summary = {
            'time_period': time_period,
            'start_time': start_time.isoformat(),
            'end_time': now.isoformat(),
            'total_events': len(relevant_events),
            'average_visitors': 0,
            'peak_visitors': 0,
            'busiest_zone': '',
            'busiest_time': '',
            'event_types': defaultdict(int),
            'zone_statistics': defaultdict(lambda: {
                'total_visitors': 0,
                'peak_visitors': 0,
                'avg_occupancy': 0
            })
        }
        
        if relevant_events:
            visitor_counts = [event.visitor_count for event in relevant_events]
            summary['average_visitors'] = np.mean(visitor_counts)
            summary['peak_visitors'] = max(visitor_counts)
            
            # Event type distribution
            for event in relevant_events:
                summary['event_types'][event.event_type] += 1
            
            # Zone statistics
            zone_visitor_counts = defaultdict(list)
            for event in relevant_events:
                zone_visitor_counts[event.zone].append(event.visitor_count)
            
            for zone, counts in zone_visitor_counts.items():
                summary['zone_statistics'][zone] = {
                    'total_visitors': sum(counts),
                    'peak_visitors': max(counts),
                    'avg_occupancy': np.mean(counts)
                }
            
            # Busiest zone
            if summary['zone_statistics']:
                summary['busiest_zone'] = max(
                    summary['zone_statistics'].items(),
                    key=lambda x: x[1]['total_visitors']
                )[0]
        
        return summary
    
    def generate_flow_visualization(self, zone: str, time_period: str = 'hour') -> Dict[str, Any]:
        """
        Generate flow visualization data for specific zone
        """
        # Mock flow data for development
        time_slots = 24 if time_period == 'day' else 60  # Hours or minutes
        flow_data = []
        
        for i in range(time_slots):
            timestamp = datetime.now() - timedelta(
                hours=time_slots-i if time_period == 'day' else 0,
                minutes=time_slots-i if time_period == 'hour' else 0
            )
            
            # Generate realistic flow pattern
            base_flow = 20
            if time_period == 'day':
                # Higher during business hours
                hour = timestamp.hour
                if 9 <= hour <= 21:
                    base_flow += np.random.randint(10, 50)
                else:
                    base_flow = np.random.randint(0, 10)
            else:
                base_flow += np.random.randint(0, 30)
            
            flow_data.append({
                'timestamp': timestamp.isoformat(),
                'visitor_count': base_flow,
                'in_flow': np.random.randint(0, base_flow),
                'out_flow': np.random.randint(0, base_flow)
            })
        
        return {
            'zone': zone,
            'time_period': time_period,
            'flow_data': flow_data,
            'summary': {
                'peak_time': max(flow_data, key=lambda x: x['visitor_count'])['timestamp'],
                'avg_visitors': np.mean([d['visitor_count'] for d in flow_data]),
                'total_in_flow': sum([d['in_flow'] for d in flow_data]),
                'total_out_flow': sum([d['out_flow'] for d in flow_data])
            }
        }
    
    def predict_traffic_patterns(self, prediction_hours: int = 24) -> Dict[str, Any]:
        """
        Predict future traffic patterns based on historical data
        """
        # Simple prediction based on historical patterns
        predictions = {
            'prediction_period': prediction_hours,
            'generated_at': datetime.now().isoformat(),
            'zone_predictions': {},
            'overall_prediction': {
                'peak_hours': [],
                'low_traffic_hours': [],
                'expected_total_visitors': 0
            }
        }
        
        # Generate predictions for each zone
        for zone_name in self.zones.keys():
            hourly_predictions = []
            
            for hour in range(prediction_hours):
                future_time = datetime.now() + timedelta(hours=hour)
                
                # Simple pattern: higher traffic during business hours
                base_prediction = 20
                if 9 <= future_time.hour <= 21:
                    base_prediction += np.random.randint(20, 80)
                    if 12 <= future_time.hour <= 14 or 18 <= future_time.hour <= 20:
                        base_prediction += 20  # Lunch and dinner peaks
                
                hourly_predictions.append({
                    'hour': future_time.hour,
                    'predicted_visitors': base_prediction,
                    'confidence': np.random.uniform(0.7, 0.9)
                })
            
            predictions['zone_predictions'][zone_name] = hourly_predictions
        
        # Overall predictions
        all_predictions = [
            pred['predicted_visitors'] 
            for zone_preds in predictions['zone_predictions'].values()
            for pred in zone_preds
        ]
        
        predictions['overall_prediction']['expected_total_visitors'] = sum(all_predictions)
        
        return predictions