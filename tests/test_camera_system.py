import pytest
import numpy as np
from unittest.mock import patch, MagicMock

def test_biometric_analyzer_initialization():
    from backend.camera_system.biometric_analyzer import BiometricAnalyzer
    
    analyzer = BiometricAnalyzer()
    
    assert analyzer.age_model is not None
    assert analyzer.gender_model is not None
    assert analyzer.emotion_model is not None

def test_frame_analysis(mock_camera_data):
    from backend.camera_system.biometric_analyzer import BiometricAnalyzer
    
    analyzer = BiometricAnalyzer()
    
    mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    result = analyzer.analyze_frame(mock_frame, "CAM_001", "entrance")
    
    assert 'camera_id' in result
    assert 'faces_detected' in result
    assert 'demographics' in result
    assert 'crowd_density' in result

@patch('cv2.CascadeClassifier')
def test_face_detection_mock(mock_cascade):
    from backend.camera_system.biometric_analyzer import BiometricAnalyzer
    
    mock_cascade_instance = MagicMock()
    mock_cascade_instance.detectMultiScale.return_value = [(10, 10, 50, 50), (100, 100, 60, 60)]
    mock_cascade.return_value = mock_cascade_instance
    
    analyzer = BiometricAnalyzer()
    
    mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = analyzer.analyze_frame(mock_frame, "CAM_001")
    
    assert result['faces_detected'] == 2

def test_traffic_monitor_initialization():
    from backend.camera_system.traffic_monitor import TrafficMonitor
    
    monitor = TrafficMonitor()
    
    assert len(monitor.zones) > 0
    assert 'entrance' in monitor.zones
    assert 'main_hall' in monitor.zones

def test_traffic_analysis():
    from backend.camera_system.traffic_monitor import TrafficMonitor
    
    monitor = TrafficMonitor()
    
    mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    result = monitor.analyze_traffic_frame(mock_frame, "CAM_001")
    
    assert 'visitor_count' in result
    assert 'movement_detected' in result
    assert 'crowd_density' in result
    assert 'primary_zone' in result

def test_cv_model_manager():
    from backend.camera_system.cv_models import CVModelManager
    
    manager = CVModelManager()
    
    assert 'age_detector' in manager.models
    assert 'gender_classifier' in manager.models
    assert 'emotion_recognizer' in manager.models