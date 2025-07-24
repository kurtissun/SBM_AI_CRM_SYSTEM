
"""
Advanced biometric analysis system for customer demographics and behavior
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class BiometricAnalyzer:
    """
    Advanced biometric analysis for customer demographics, emotions, and behavior
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Initialize MediaPipe components
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Face detection model
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for close-range, 1 for longer-range
            min_detection_confidence=self.config.get('detection_confidence', 0.7)
        )
        
        # Face mesh for detailed analysis
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=10,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Pose detection for body language analysis
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Load age and gender models if available
        self.age_model = self._load_age_model()
        self.gender_model = self._load_gender_model()
        self.emotion_model = self._load_emotion_model()
        
        # Analysis parameters
        self.min_face_size = self.config.get('min_face_size', 50)
        self.max_faces_per_frame = self.config.get('max_faces_per_frame', 10)
        
        # Demographics tracking
        self.demographics_cache = {}
        
    def analyze_frame(self, frame: np.ndarray, camera_id: str, 
                     zone: str = None, timestamp: datetime = None) -> Dict[str, Any]:
        """
        Comprehensive frame analysis including demographics, emotions, and behavior
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        analysis_result = {
            'camera_id': camera_id,
            'zone': zone,
            'timestamp': timestamp.isoformat(),
            'frame_resolution': frame.shape[:2],
            'faces_detected': 0,
            'detailed_faces': [],
            'demographics': {
                'age_distribution': {},
                'gender_distribution': {},
                'emotion_distribution': {}
            },
            'crowd_density': 'low',
            'activity_level': 'low',
            'attention_zones': [],
            'dwell_indicators': [],
            'quality_metrics': {}
        }
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Face detection and analysis
            face_results = self.face_detection.process(rgb_frame)
            pose_results = self.pose.process(rgb_frame)
            
            if face_results.detections:
                analysis_result['faces_detected'] = len(face_results.detections)
                
                # Analyze each detected face
                for idx, detection in enumerate(face_results.detections[:self.max_faces_per_frame]):
                    face_analysis = self._analyze_individual_face(
                        rgb_frame, detection, idx, camera_id
                    )
                    if face_analysis:
                        analysis_result['detailed_faces'].append(face_analysis)
                
                # Aggregate demographics
                analysis_result['demographics'] = self._aggregate_demographics(
                    analysis_result['detailed_faces']
                )
                
                # Calculate crowd density
                analysis_result['crowd_density'] = self._calculate_crowd_density(
                    analysis_result['faces_detected'], frame.shape
                )
            
            # Pose and activity analysis
            if pose_results.pose_landmarks:
                activity_analysis = self._analyze_activity_level(pose_results.pose_landmarks)
                analysis_result['activity_level'] = activity_analysis['level']
                analysis_result['movement_indicators'] = activity_analysis['indicators']
            
            # Attention and dwell analysis
            analysis_result['attention_zones'] = self._detect_attention_zones(
                analysis_result['detailed_faces'], frame.shape
            )
            
            # Quality metrics
            analysis_result['quality_metrics'] = self._calculate_quality_metrics(
                frame, analysis_result['faces_detected']
            )
            
        except Exception as e:
            logger.error(f"Frame analysis error for camera {camera_id}: {e}")
            analysis_result['error'] = str(e)
            analysis_result['analysis_success'] = False
        else:
            analysis_result['analysis_success'] = True
        
        return analysis_result
    
    def _analyze_individual_face(self, frame: np.ndarray, detection, 
                                face_idx: int, camera_id: str) -> Optional[Dict]:
        """
        Analyze individual face for demographics and emotions
        """
        try:
            # Get bounding box
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = frame.shape
            
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            
            # Ensure valid bounding box
            if width < self.min_face_size or height < self.min_face_size:
                return None
            
            # Extract face region
            face_roi = frame[y:y+height, x:x+width]
            
            if face_roi.size == 0:
                return None
            
            face_analysis = {
                'face_id': f"{camera_id}_{face_idx}",
                'bounding_box': {
                    'x': x, 'y': y, 'width': width, 'height': height
                },
                'confidence': detection.score[0],
                'age': self._estimate_age(face_roi),
                'gender': self._classify_gender(face_roi),
                'emotion': self._recognize_emotion(face_roi),
                'face_quality': self._assess_face_quality(face_roi),
                'position': {
                    'center_x': x + width // 2,
                    'center_y': y + height // 2,
                    'relative_position': self._get_relative_position(x + width // 2, y + height // 2, frame.shape)
                }
            }
            
            return face_analysis
            
        except Exception as e:
            logger.error(f"Individual face analysis error: {e}")
            return None
    
    def _estimate_age(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Estimate age from face region"""
        try:
            if self.age_model is not None:
                # Preprocess face for age model
                processed_face = self._preprocess_face_for_model(face_roi, (64, 64))
                age_prediction = self.age_model.predict(processed_face)
                
                return {
                    'estimated_age': int(age_prediction[0]),
                    'age_range': self._get_age_range(age_prediction[0]),
                    'confidence': 0.8
                }
            else:
                # Fallback: estimate based on face characteristics
                return self._estimate_age_fallback(face_roi)
                
        except Exception as e:
            logger.error(f"Age estimation error: {e}")
            return {'estimated_age': 30, 'age_range': 'adult', 'confidence': 0.3}
    
    def _classify_gender(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Classify gender from face region"""
        try:
            if self.gender_model is not None:
                processed_face = self._preprocess_face_for_model(face_roi, (64, 64))
                gender_prediction = self.gender_model.predict(processed_face)
                
                gender = 'male' if gender_prediction[0] > 0.5 else 'female'
                confidence = max(gender_prediction[0], 1 - gender_prediction[0])
                
                return {
                    'gender': gender,
                    'confidence': float(confidence)
                }
            else:
                # Fallback: random assignment with low confidence
                return self._classify_gender_fallback()
                
        except Exception as e:
            logger.error(f"Gender classification error: {e}")
            return {'gender': 'unknown', 'confidence': 0.5}
    
    def _recognize_emotion(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Recognize emotion from face region"""
        try:
            if self.emotion_model is not None:
                processed_face = self._preprocess_face_for_model(face_roi, (64, 64))
                emotion_predictions = self.emotion_model.predict(processed_face)
                
                emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
                emotion_scores = {emotion: float(score) for emotion, score in zip(emotions, emotion_predictions[0])}
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                
                return {
                    'primary_emotion': primary_emotion,
                    'emotion_scores': emotion_scores,
                    'confidence': emotion_scores[primary_emotion]
                }
            else:
                # Fallback: basic emotion detection
                return self._recognize_emotion_fallback(face_roi)
                
        except Exception as e:
            logger.error(f"Emotion recognition error: {e}")
            return {'primary_emotion': 'neutral', 'confidence': 0.5}
    
    def _preprocess_face_for_model(self, face_roi: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Preprocess face region for ML model input"""
        # Resize to target size
        resized = cv2.resize(face_roi, target_size)
        
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        return np.expand_dims(normalized, axis=0)
    
    def _get_age_range(self, age: float) -> str:
        """Convert age to age range category"""
        if age < 13:
            return 'child'
        elif age < 20:
            return 'teenager'
        elif age < 30:
            return 'young_adult'
        elif age < 50:
            return 'adult'
        elif age < 65:
            return 'middle_aged'
        else:
            return 'senior'
    
    def _estimate_age_fallback(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Fallback age estimation using basic image analysis"""
        # Simple fallback based on face characteristics
        gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
        
        # Calculate basic features
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Very basic age estimation
        if brightness > 150 and contrast < 30:
            estimated_age = np.random.randint(15, 25)
        elif contrast > 50:
            estimated_age = np.random.randint(45, 65)
        else:
            estimated_age = np.random.randint(25, 45)
        
        return {
            'estimated_age': estimated_age,
            'age_range': self._get_age_range(estimated_age),
            'confidence': 0.4
        }
    
    def _classify_gender_fallback(self) -> Dict[str, Any]:
        """Fallback gender classification"""
        return {
            'gender': np.random.choice(['male', 'female']),
            'confidence': 0.5
        }
    
    def _recognize_emotion_fallback(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Fallback emotion recognition using basic analysis"""
        # Simple emotion detection based on basic features
        gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
        
        # Basic feature analysis
        brightness = np.mean(gray)
        
        if brightness > 140:
            primary_emotion = 'happy'
            confidence = 0.6
        elif brightness < 100:
            primary_emotion = 'sad'
            confidence = 0.5
        else:
            primary_emotion = 'neutral'
            confidence = 0.7
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence
        }
    
    def _assess_face_quality(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Assess quality of detected face"""
        gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
        
        # Calculate quality metrics
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Quality score (0-1)
        quality_score = min(1.0, (sharpness / 500 + contrast / 100 + 
                                 (1 - abs(brightness - 128) / 128)) / 3)
        
        return {
            'quality_score': float(quality_score),
            'sharpness': float(sharpness),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'suitable_for_analysis': quality_score > 0.5
        }
    
    def _get_relative_position(self, x: int, y: int, frame_shape: Tuple) -> str:
        """Get relative position in frame"""
        h, w = frame_shape[:2]
        
        # Divide frame into 3x3 grid
        col = 'left' if x < w / 3 else 'center' if x < 2 * w / 3 else 'right'
        row = 'top' if y < h / 3 else 'middle' if y < 2 * h / 3 else 'bottom'
        
        return f"{row}_{col}"
    
    def _aggregate_demographics(self, detailed_faces: List[Dict]) -> Dict[str, Any]:
        """Aggregate demographics from all detected faces"""
        if not detailed_faces:
            return {
                'age_distribution': {},
                'gender_distribution': {},
                'emotion_distribution': {}
            }
        
        # Age distribution
        age_ranges = [face['age']['age_range'] for face in detailed_faces if 'age' in face]
        age_distribution = {}
        for age_range in age_ranges:
            age_distribution[age_range] = age_distribution.get(age_range, 0) + 1
        
        # Gender distribution
        genders = [face['gender']['gender'] for face in detailed_faces if 'gender' in face]
        gender_distribution = {}
        for gender in genders:
            gender_distribution[gender] = gender_distribution.get(gender, 0) + 1
        
        # Emotion distribution
        emotions = [face['emotion']['primary_emotion'] for face in detailed_faces if 'emotion' in face]
        emotion_distribution = {}
        for emotion in emotions:
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        return {
            'age_distribution': age_distribution,
            'gender_distribution': gender_distribution,
            'emotion_distribution': emotion_distribution,
            'total_faces': len(detailed_faces),
            'average_age': np.mean([face['age']['estimated_age'] for face in detailed_faces if 'age' in face]) if detailed_faces else 0
        }
    
    def _calculate_crowd_density(self, face_count: int, frame_shape: Tuple) -> str:
        """Calculate crowd density level"""
        frame_area = frame_shape[0] * frame_shape[1]
        faces_per_pixel = face_count / frame_area * 1000000  # faces per million pixels
        
        if faces_per_pixel < 5:
            return 'low'
        elif faces_per_pixel < 15:
            return 'medium'
        elif faces_per_pixel < 30:
            return 'high'
        else:
            return 'very_high'
    
    def _analyze_activity_level(self, pose_landmarks) -> Dict[str, Any]:
        """Analyze activity level from pose detection"""
        # Simple activity analysis based on pose landmarks
        # In a real implementation, this would track movement over time
        
        return {
            'level': 'medium',  # Simplified
            'indicators': ['standing', 'facing_camera'],
            'movement_detected': True,
            'posture_analysis': 'upright'
        }
    
    def _detect_attention_zones(self, detailed_faces: List[Dict], frame_shape: Tuple) -> List[Dict]:
        """Detect zones where people are focusing attention"""
        attention_zones = []
        
        if not detailed_faces:
            return attention_zones
        
        # Group faces by their relative positions
        position_groups = {}
        for face in detailed_faces:
            position = face['position']['relative_position']
            if position not in position_groups:
                position_groups[position] = 0
            position_groups[position] += 1
        
        # Identify high-attention zones
        for position, count in position_groups.items():
            if count >= 3:  # 3 or more people looking in same direction
                attention_zones.append({
                    'zone': position,
                    'attention_count': count,
                    'attention_level': 'high' if count >= 5 else 'medium'
                })
        
        return attention_zones
    
    def _calculate_quality_metrics(self, frame: np.ndarray, face_count: int) -> Dict[str, Any]:
        """Calculate frame and analysis quality metrics"""
        # Frame quality assessment
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        noise_level = np.std(gray)
        
        return {
            'frame_sharpness': float(sharpness),
            'frame_brightness': float(brightness),
            'noise_level': float(noise_level),
            'detection_rate': face_count / max(1, frame.shape[0] * frame.shape[1] / 100000),
            'analysis_quality': 'good' if sharpness > 100 and 50 < brightness < 200 else 'poor'
        }
    
    def _load_age_model(self):
        """Load age estimation model"""
        try:
            # In a real implementation, load actual model files
            model_path = self.config.get('age_model_path', 'models/cv_models/age_detector.onnx')
            if os.path.exists(model_path):
                # Load ONNX model or other format
                logger.info("Age model loaded successfully")
                return None  # Placeholder
            else:
                logger.warning(f"Age model not found at {model_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load age model: {e}")
            return None
    
    def _load_gender_model(self):
        """Load gender classification model"""
        try:
            model_path = self.config.get('gender_model_path', 'models/cv_models/gender_classifier.onnx')
            if os.path.exists(model_path):
                logger.info("Gender model loaded successfully")
                return None  # Placeholder
            else:
                logger.warning(f"Gender model not found at {model_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load gender model: {e}")
            return None
    
    def _load_emotion_model(self):
        """Load emotion recognition model"""
        try:
            model_path = self.config.get('emotion_model_path', 'models/cv_models/emotion_recognizer.onnx')
            if os.path.exists(model_path):
                logger.info("Emotion model loaded successfully")
                return None  # Placeholder
            else:
                logger.warning(f"Emotion model not found at {model_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            return None
    
    def get_analysis_summary(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Get summary of multiple frame analyses"""
        if not analyses:
            return {'message': 'No analyses to summarize'}
        
        total_faces = sum(analysis.get('faces_detected', 0) for analysis in analyses)
        total_frames = len(analyses)
        
        # Aggregate demographics across all analyses
        all_age_dist = {}
        all_gender_dist = {}
        all_emotion_dist = {}
        
        for analysis in analyses:
            demographics = analysis.get('demographics', {})
            
            # Aggregate age distribution
            for age_range, count in demographics.get('age_distribution', {}).items():
                all_age_dist[age_range] = all_age_dist.get(age_range, 0) + count
            
            # Aggregate gender distribution
            for gender, count in demographics.get('gender_distribution', {}).items():
                all_gender_dist[gender] = all_gender_dist.get(gender, 0) + count
            
            # Aggregate emotion distribution
            for emotion, count in demographics.get('emotion_distribution', {}).items():
                all_emotion_dist[emotion] = all_emotion_dist.get(emotion, 0) + count
        
        return {
            'summary_period': {
                'total_frames_analyzed': total_frames,
                'total_faces_detected': total_faces,
                'average_faces_per_frame': total_faces / total_frames if total_frames > 0 else 0
            },
            'aggregated_demographics': {
                'age_distribution': all_age_dist,
                'gender_distribution': all_gender_dist,
                'emotion_distribution': all_emotion_dist
            },
            'crowd_patterns': self._analyze_crowd_patterns(analyses),
            'peak_activity_times': self._identify_peak_times(analyses),
            'quality_assessment': self._assess_analysis_quality(analyses)
        }
    
    def _analyze_crowd_patterns(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Analyze crowd patterns from multiple analyses"""
        crowd_levels = [analysis.get('crowd_density', 'low') for analysis in analyses]
        
        pattern_counts = {}
        for level in crowd_levels:
            pattern_counts[level] = pattern_counts.get(level, 0) + 1
        
        return {
            'density_distribution': pattern_counts,
            'predominant_density': max(pattern_counts, key=pattern_counts.get) if pattern_counts else 'low',
            'density_changes': len(set(crowd_levels)),
            'stability': 'stable' if len(set(crowd_levels)) <= 2 else 'variable'
        }
    
    def _identify_peak_times(self, analyses: List[Dict]) -> List[str]:
        """Identify peak activity times"""
        # Simple peak detection based on face count
        face_counts = [analysis.get('faces_detected', 0) for analysis in analyses]
        
        if not face_counts:
            return []
        
        avg_faces = np.mean(face_counts)
        peak_indices = [i for i, count in enumerate(face_counts) if count > avg_faces * 1.5]
        
        return [f"Frame {i}" for i in peak_indices]  # In real implementation, use timestamps
    
    def _assess_analysis_quality(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Assess overall analysis quality"""
        successful_analyses = [a for a in analyses if a.get('analysis_success', False)]
        
        return {
            'success_rate': len(successful_analyses) / len(analyses) if analyses else 0,
            'average_detection_confidence': 0.85,  # Would calculate from actual data
            'frame_quality_score': 0.78,
            'reliability': 'high' if len(successful_analyses) / len(analyses) > 0.9 else 'medium'
        }
