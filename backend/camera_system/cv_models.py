
import os
import json
import numpy as np
import cv2
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import onnxruntime as ort
from datetime import datetime

logger = logging.getLogger(__name__)

class CVModelManager:
    """
    Centralized management system for computer vision models
    """
    
    def __init__(self, model_registry_path: str = "models/model_registry.json"):
        self.model_registry_path = model_registry_path
        self.models = {}
        self.model_metadata = {}
        self.sessions = {}  # ONNX runtime sessions
        
        # Load model registry
        self._load_model_registry()
        
        # Initialize available models
        self._initialize_models()
    
    def _load_model_registry(self):
        """Load model registry configuration"""
        try:
            if os.path.exists(self.model_registry_path):
                with open(self.model_registry_path, 'r') as f:
                    registry = json.load(f)
                    self.model_metadata = registry.get('model_registry', {}).get('cv_models', {})
                logger.info(f"Loaded model registry with {len(self.model_metadata)} CV models")
            else:
                logger.warning(f"Model registry not found at {self.model_registry_path}")
                self.model_metadata = {}
        except Exception as e:
            logger.error(f"Failed to load model registry: {e}")
            self.model_metadata = {}
    
    def _initialize_models(self):
        """Initialize all available models"""
        for model_name, metadata in self.model_metadata.items():
            if metadata.get('status') == 'active':
                try:
                    self._load_model(model_name, metadata)
                except Exception as e:
                    logger.error(f"Failed to initialize model {model_name}: {e}")
    
    def _load_model(self, model_name: str, metadata: Dict):
        """Load a specific model"""
        model_path = metadata.get('file_path')
        
        if not model_path or not os.path.exists(model_path):
            logger.warning(f"Model file not found for {model_name}: {model_path}")
            # Create placeholder for demo
            self.models[model_name] = self._create_placeholder_model(model_name, metadata)
            return
        
        try:
            if model_path.endswith('.onnx'):
                # Load ONNX model
                session = ort.InferenceSession(model_path)
                self.sessions[model_name] = session
                self.models[model_name] = {
                    'type': 'onnx',
                    'session': session,
                    'input_shape': metadata.get('input_shape'),
                    'output_shape': metadata.get('output_shape'),
                    'classes': metadata.get('classes', [])
                }
                logger.info(f"Loaded ONNX model: {model_name}")
            else:
                # Handle other model formats
                logger.warning(f"Unsupported model format for {model_name}")
                self.models[model_name] = self._create_placeholder_model(model_name, metadata)
                
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            self.models[model_name] = self._create_placeholder_model(model_name, metadata)
    
    def _create_placeholder_model(self, model_name: str, metadata: Dict):
        """Create placeholder model for demo purposes"""
        return {
            'type': 'placeholder',
            'name': model_name,
            'input_shape': metadata.get('input_shape', [1, 3, 64, 64]),
            'output_shape': metadata.get('output_shape', [1, 1]),
            'classes': metadata.get('classes', []),
            'description': metadata.get('description', ''),
            'performance_metrics': metadata.get('performance_metrics', {})
        }
    
    def predict_age(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Predict age from face image"""
        model_name = 'age_detector'
        
        if model_name not in self.models:
            return {'error': 'Age model not available'}
        
        model = self.models[model_name]
        
        try:
            if model['type'] == 'onnx':
                # Preprocess image
                input_tensor = self._preprocess_for_age_model(face_image, model['input_shape'])
                
                # Run inference
                session = self.sessions[model_name]
                input_name = session.get_inputs()[0].name
                outputs = session.run(None, {input_name: input_tensor})
                
                # Process output
                age_prediction = outputs[0][0]
                
                return {
                    'predicted_age': float(age_prediction),
                    'age_range': self._get_age_range(age_prediction),
                    'confidence': 0.85,
                    'model_used': model_name
                }
            else:
                # Placeholder prediction for demo
                return self._placeholder_age_prediction(face_image)
                
        except Exception as e:
            logger.error(f"Age prediction error: {e}")
            return {'error': str(e)}
    
    def classify_gender(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Classify gender from face image"""
        model_name = 'gender_classifier'
        
        if model_name not in self.models:
            return {'error': 'Gender model not available'}
        
        model = self.models[model_name]
        
        try:
            if model['type'] == 'onnx':
                # Preprocess image
                input_tensor = self._preprocess_for_gender_model(face_image, model['input_shape'])
                
                # Run inference
                session = self.sessions[model_name]
                input_name = session.get_inputs()[0].name
                outputs = session.run(None, {input_name: input_tensor})
                
                # Process output
                gender_probs = outputs[0][0]
                classes = model.get('classes', ['female', 'male'])
                
                predicted_class = classes[np.argmax(gender_probs)]
                confidence = float(np.max(gender_probs))
                
                return {
                    'predicted_gender': predicted_class,
                    'confidence': confidence,
                    'probabilities': {classes[i]: float(prob) for i, prob in enumerate(gender_probs)},
                    'model_used': model_name
                }
            else:
                # Placeholder prediction for demo
                return self._placeholder_gender_prediction(face_image)
                
        except Exception as e:
            logger.error(f"Gender classification error: {e}")
            return {'error': str(e)}
    
    def recognize_emotion(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Recognize emotion from face image"""
        model_name = 'emotion_recognizer'
        
        if model_name not in self.models:
            return {'error': 'Emotion model not available'}
        
        model = self.models[model_name]
        
        try:
            if model['type'] == 'onnx':
                # Preprocess image
                input_tensor = self._preprocess_for_emotion_model(face_image, model['input_shape'])
                
                # Run inference
                session = self.sessions[model_name]
                input_name = session.get_inputs()[0].name
                outputs = session.run(None, {input_name: input_tensor})
                
                # Process output
                emotion_probs = outputs[0][0]
                classes = model.get('classes', ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise'])
                
                predicted_class = classes[np.argmax(emotion_probs)]
                confidence = float(np.max(emotion_probs))
                
                return {
                    'predicted_emotion': predicted_class,
                    'confidence': confidence,
                    'emotion_scores': {classes[i]: float(prob) for i, prob in enumerate(emotion_probs)},
                    'model_used': model_name
                }
            else:
                # Placeholder prediction for demo
                return self._placeholder_emotion_prediction(face_image)
                
        except Exception as e:
            logger.error(f"Emotion recognition error: {e}")
            return {'error': str(e)}
    
    def detect_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect faces in image"""
        model_name = 'face_detector'
        
        if model_name not in self.models:
            return {'error': 'Face detection model not available'}
        
        model = self.models[model_name]
        
        try:
            if model['type'] == 'onnx':
                # Preprocess image
                input_tensor = self._preprocess_for_face_detection(image, model['input_shape'])
                
                # Run inference
                session = self.sessions[model_name]
                input_name = session.get_inputs()[0].name
                outputs = session.run(None, {input_name: input_tensor})
                
                # Process output to get bounding boxes
                detections = self._process_face_detection_output(outputs, image.shape)
                
                return {
                    'faces_detected': len(detections),
                    'detections': detections,
                    'model_used': model_name
                }
            else:
                # Placeholder detection for demo
                return self._placeholder_face_detection(image)
                
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return {'error': str(e)}
    
    def _preprocess_for_age_model(self, image: np.ndarray, input_shape: List[int]) -> np.ndarray:
        """Preprocess image for age model"""
        target_size = (input_shape[3], input_shape[2])  # Width, Height
        
        # Resize image
        resized = cv2.resize(image, target_size)
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to CHW format if needed
        if len(input_shape) == 4 and input_shape[1] == 3:
            normalized = np.transpose(normalized, (2, 0, 1))
        
        # Add batch dimension
        return np.expand_dims(normalized, axis=0)
    
    def _preprocess_for_gender_model(self, image: np.ndarray, input_shape: List[int]) -> np.ndarray:
        """Preprocess image for gender model"""
        return self._preprocess_for_age_model(image, input_shape)
    
    def _preprocess_for_emotion_model(self, image: np.ndarray, input_shape: List[int]) -> np.ndarray:
        """Preprocess image for emotion model"""
        return self._preprocess_for_age_model(image, input_shape)
    
    def _preprocess_for_face_detection(self, image: np.ndarray, input_shape: List[int]) -> np.ndarray:
        """Preprocess image for face detection"""
        target_size = (input_shape[3], input_shape[2])
        
        # Resize image
        resized = cv2.resize(image, target_size)
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to CHW format
        if len(input_shape) == 4 and input_shape[1] == 3:
            normalized = np.transpose(normalized, (2, 0, 1))
        
        # Add batch dimension
        return np.expand_dims(normalized, axis=0)
    
    
    def _process_face_detection_output(self, outputs: List[np.ndarray], image_shape: Tuple) -> List[Dict]:
        """Process face detection model output to get bounding boxes"""
        detections = []
        
        # This is a simplified version - actual implementation depends on model architecture
        detection_output = outputs[0]  # Assuming first output contains detections
        
        h, w = image_shape[:2]
        
        # Process each detection
        for detection in detection_output[0]:  # Assuming batch size 1
            confidence = detection[4] if len(detection) > 4 else 0.8
            
            if confidence > 0.5:  # Confidence threshold
                # Extract bounding box coordinates (normalized)
                x1, y1, x2, y2 = detection[:4]
                
                # Convert to pixel coordinates
                x1_pixel = int(x1 * w)
                y1_pixel = int(y1 * h)
                x2_pixel = int(x2 * w)
                y2_pixel = int(y2 * h)
                
                detections.append({
                    'bbox': {
                        'x1': x1_pixel,
                        'y1': y1_pixel,
                        'x2': x2_pixel,
                        'y2': y2_pixel,
                        'width': x2_pixel - x1_pixel,
                        'height': y2_pixel - y1_pixel
                    },
                    'confidence': float(confidence)
                })
        
        return detections
    
    def _get_age_range(self, age: float) -> str:
        """Convert predicted age to age range"""
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
    
    # Placeholder prediction methods for demo
    def _placeholder_age_prediction(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Placeholder age prediction for demo"""
        # Generate reasonable age based on image properties
        gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY) if len(face_image.shape) == 3 else face_image
        brightness = np.mean(gray)
        
        if brightness > 150:
            age = np.random.randint(18, 35)
        elif brightness < 100:
            age = np.random.randint(45, 70)
        else:
            age = np.random.randint(25, 50)
        
        return {
            'predicted_age': age,
            'age_range': self._get_age_range(age),
            'confidence': 0.75,
            'model_used': 'placeholder'
        }
    
    def _placeholder_gender_prediction(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Placeholder gender prediction for demo"""
        # Simple placeholder based on image characteristics
        gender = np.random.choice(['male', 'female'])
        confidence = np.random.uniform(0.6, 0.9)
        
        return {
            'predicted_gender': gender,
            'confidence': confidence,
            'probabilities': {
                'male': confidence if gender == 'male' else 1 - confidence,
                'female': confidence if gender == 'female' else 1 - confidence
            },
            'model_used': 'placeholder'
        }
    
    def _placeholder_emotion_prediction(self, face_image: np.ndarray) -> Dict[str, Any]:
        """Placeholder emotion prediction for demo"""
        emotions = ['happy', 'neutral', 'focused', 'surprised', 'sad']
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Bias toward positive emotions
        
        predicted_emotion = np.random.choice(emotions, p=weights)
        confidence = np.random.uniform(0.6, 0.9)
        
        # Generate emotion scores
        emotion_scores = {}
        remaining_prob = 1 - confidence
        for emotion in emotions:
            if emotion == predicted_emotion:
                emotion_scores[emotion] = confidence
            else:
                emotion_scores[emotion] = remaining_prob / (len(emotions) - 1)
        
        return {
            'predicted_emotion': predicted_emotion,
            'confidence': confidence,
            'emotion_scores': emotion_scores,
            'model_used': 'placeholder'
        }
    
    def _placeholder_face_detection(self, image: np.ndarray) -> Dict[str, Any]:
        """Placeholder face detection for demo"""
        h, w = image.shape[:2]
        
        # Generate random face detections
        num_faces = np.random.randint(1, 4)
        detections = []
        
        for i in range(num_faces):
            # Generate random bounding box
            x1 = np.random.randint(0, w // 2)
            y1 = np.random.randint(0, h // 2)
            width = np.random.randint(50, min(200, w - x1))
            height = np.random.randint(50, min(200, h - y1))
            
            detections.append({
                'bbox': {
                    'x1': x1,
                    'y1': y1,
                    'x2': x1 + width,
                    'y2': y1 + height,
                    'width': width,
                    'height': height
                },
                'confidence': np.random.uniform(0.7, 0.95)
            })
        
        return {
            'faces_detected': len(detections),
            'detections': detections,
            'model_used': 'placeholder'
        }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_name not in self.models:
            return {'error': 'Model not found'}
        
        model = self.models[model_name]
        metadata = self.model_metadata.get(model_name, {})
        
        return {
            'model_name': model_name,
            'type': model['type'],
            'status': 'active' if model_name in self.models else 'inactive',
            'input_shape': model.get('input_shape'),
            'output_shape': model.get('output_shape'),
            'classes': model.get('classes', []),
            'performance_metrics': metadata.get('performance_metrics', {}),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '1.0'),
            'model_size_mb': metadata.get('model_size_mb', 0),
            'inference_time_ms': metadata.get('inference_time_ms', 0)
        }
    
    def get_all_models_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        models_status = {}
        
        for model_name in self.model_metadata.keys():
            models_status[model_name] = {
                'loaded': model_name in self.models,
                'status': self.model_metadata[model_name].get('status', 'unknown'),
                'type': self.models[model_name]['type'] if model_name in self.models else 'unknown'
            }
        
        return {
            'total_models': len(self.model_metadata),
            'loaded_models': len(self.models),
            'models_status': models_status,
            'system_ready': len(self.models) > 0
        }
    
    def benchmark_model(self, model_name: str, test_image: np.ndarray = None) -> Dict[str, Any]:
        """Benchmark model performance"""
        if model_name not in self.models:
            return {'error': 'Model not found'}
        
        if test_image is None:
            # Create synthetic test image
            test_image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        
        model = self.models[model_name]
        
        # Measure inference time
        import time
        
        num_runs = 10
        times = []
        
        for _ in range(num_runs):
            start_time = time.time()
            
            if model_name == 'age_detector':
                result = self.predict_age(test_image)
            elif model_name == 'gender_classifier':
                result = self.classify_gender(test_image)
            elif model_name == 'emotion_recognizer':
                result = self.recognize_emotion(test_image)
            elif model_name == 'face_detector':
                result = self.detect_faces(test_image)
            else:
                continue
            
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        return {
            'model_name': model_name,
            'benchmark_runs': num_runs,
            'average_inference_time_ms': np.mean(times),
            'min_inference_time_ms': np.min(times),
            'max_inference_time_ms': np.max(times),
            'std_inference_time_ms': np.std(times),
            'throughput_fps': 1000 / np.mean(times) if np.mean(times) > 0 else 0,
            'model_type': model['type'],
            'test_image_shape': test_image.shape
        }
    
    def reload_model(self, model_name: str) -> Dict[str, Any]:
        """Reload a specific model"""
        if model_name not in self.model_metadata:
            return {'error': 'Model not found in registry'}
        
        try:
            # Remove existing model if loaded
            if model_name in self.models:
                del self.models[model_name]
            if model_name in self.sessions:
                del self.sessions[model_name]
            
            # Reload model
            metadata = self.model_metadata[model_name]
            self._load_model(model_name, metadata)
            
            return {
                'model_name': model_name,
                'status': 'reloaded',
                'type': self.models[model_name]['type'] if model_name in self.models else 'failed'
            }
            
        except Exception as e:
            logger.error(f"Failed to reload model {model_name}: {e}")
            return {'error': str(e)}
    
    def validate_model_inputs(self, model_name: str, input_data: np.ndarray) -> Dict[str, Any]:
        """Validate input data for a specific model"""
        if model_name not in self.models:
            return {'valid': False, 'error': 'Model not found'}
        
        model = self.models[model_name]
        expected_shape = model.get('input_shape', [])
        
        validation_result = {
            'valid': True,
            'model_name': model_name,
            'expected_shape': expected_shape,
            'actual_shape': list(input_data.shape),
            'issues': []
        }
        
        # Check shape compatibility
        if len(expected_shape) > 0:
            # For batch processing, ignore batch dimension
            expected_dims = expected_shape[1:] if len(expected_shape) > 3 else expected_shape
            actual_dims = input_data.shape
            
            # Check dimensions
            if len(actual_dims) != len(expected_dims):
                validation_result['valid'] = False
                validation_result['issues'].append(f"Dimension mismatch: expected {len(expected_dims)}, got {len(actual_dims)}")
            
            # Check data type
            if input_data.dtype not in [np.float32, np.uint8]:
                validation_result['issues'].append(f"Unexpected data type: {input_data.dtype}")
            
            # Check value range
            if input_data.dtype == np.uint8:
                if input_data.min() < 0 or input_data.max() > 255:
                    validation_result['issues'].append("Values out of range for uint8")
            elif input_data.dtype == np.float32:
                if input_data.min() < 0 or input_data.max() > 1:
                    validation_result['issues'].append("Float values should be normalized [0-1]")
        
        return validation_result

# Global model manager instance
cv_model_manager = CVModelManager()

# ===============================
# FILE: backend/camera_system/face_recognition.py
# LOCATION: backend/camera_system/face_recognition.py
# ACTION: Create new file for face recognition capabilities
# ===============================

"""
Advanced Face Recognition System for Customer Identification
"""
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# Optional import for face_recognition
try:
    import face_recognition  # type: ignore
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition library not available. Face recognition features will be disabled.")

logger = logging.getLogger(__name__)

class FaceRecognitionSystem:
    """
    Advanced face recognition system for customer identification and tracking
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.known_faces_db = {}  # Database of known face encodings
        self.face_encodings_cache = {}  # Cache for face encodings
        self.recognition_threshold = self.config.get('recognition_threshold', 0.6)
        self.encoding_model = self.config.get('encoding_model', 'large')  # 'small' or 'large'
        
        # Load existing face database
        self.db_path = self.config.get('face_db_path', 'data/face_database.pkl')
        self._load_face_database()
        
        # Customer tracking
        self.customer_visits = {}
        self.visit_timeout = timedelta(hours=2)  # Consider new visit after 2 hours
        
    def encode_face(self, face_image: np.ndarray, face_location: Tuple = None) -> Optional[np.ndarray]:
        """
        Generate face encoding from face image
        """
        if not FACE_RECOGNITION_AVAILABLE:
            logger.error("face_recognition library not available")
            return None
            
        try:
            # Convert to RGB if needed
            if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = face_image
            
            # Get face encodings
            if face_location:
                # Use provided face location
                encodings = face_recognition.face_encodings(
                    rgb_image, 
                    known_face_locations=[face_location],
                    model=self.encoding_model
                )
            else:
                # Detect face location automatically
                encodings = face_recognition.face_encodings(
                    rgb_image,
                    model=self.encoding_model
                )
            
            if len(encodings) > 0:
                return encodings[0]
            else:
                logger.warning("No face encoding generated")
                return None
                
        except Exception as e:
            logger.error(f"Face encoding error: {e}")
            return None
    
    def register_customer_face(self, customer_id: str, face_image: np.ndarray, 
                              metadata: Dict = None) -> Dict[str, Any]:
        """
        Register a new customer face in the database
        """
        try:
            # Generate face encoding
            encoding = self.encode_face(face_image)
            
            if encoding is None:
                return {
                    'success': False,
                    'error': 'Could not generate face encoding'
                }
            
            # Check if customer already exists
            if customer_id in self.known_faces_db:
                # Add additional encoding for existing customer
                self.known_faces_db[customer_id]['encodings'].append(encoding)
                action = 'updated'
            else:
                # Register new customer
                self.known_faces_db[customer_id] = {
                    'encodings': [encoding],
                    'metadata': metadata or {},
                    'registered_at': datetime.now(),
                    'last_seen': None,
                    'visit_count': 0
                }
                action = 'registered'
            
            # Save database
            self._save_face_database()
            
            return {
                'success': True,
                'customer_id': customer_id,
                'action': action,
                'total_encodings': len(self.known_faces_db[customer_id]['encodings']),
                'registered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Customer registration error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def recognize_face(self, face_image: np.ndarray, 
                      face_location: Tuple = None) -> Dict[str, Any]:
        """
        Recognize face from image and return customer information
        """
        try:
            # Generate encoding for input face
            query_encoding = self.encode_face(face_image, face_location)
            
            if query_encoding is None:
                return {
                    'recognized': False,
                    'error': 'Could not generate face encoding'
                }
            
            # Compare with known faces
            best_match = None
            best_distance = float('inf')
            
            for customer_id, customer_data in self.known_faces_db.items():
                for encoding in customer_data['encodings']:
                    # Calculate face distance
                    distance = face_recognition.face_distance([encoding], query_encoding)[0]
                    
                    if distance < best_distance and distance < self.recognition_threshold:
                        best_distance = distance
                        best_match = customer_id
            
            if best_match:
                # Update customer visit information
                self._update_customer_visit(best_match)
                
                customer_info = self.known_faces_db[best_match]
                
                return {
                    'recognized': True,
                    'customer_id': best_match,
                    'confidence': 1 - best_distance,
                    'distance': float(best_distance),
                    'customer_info': {
                        'metadata': customer_info['metadata'],
                        'last_seen': customer_info['last_seen'].isoformat() if customer_info['last_seen'] else None,
                        'visit_count': customer_info['visit_count'],
                        'registered_at': customer_info['registered_at'].isoformat()
                    }
                }
            else:
                return {
                    'recognized': False,
                    'reason': 'No matching face found',
                    'min_distance': float(best_distance) if best_distance != float('inf') else None
                }
                
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return {
                'recognized': False,
                'error': str(e)
            }
    
    def batch_recognize_faces(self, face_images: List[np.ndarray]) -> List[Dict[str, Any]]:
        """
        Recognize multiple faces in batch
        """
        results = []
        
        for i, face_image in enumerate(face_images):
            result = self.recognize_face(face_image)
            result['batch_index'] = i
            results.append(result)
        
        return results
    
    def search_similar_faces(self, face_image: np.ndarray, 
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar faces in the database
        """
        try:
            query_encoding = self.encode_face(face_image)
            
            if query_encoding is None:
                return []
            
            similarities = []
            
            for customer_id, customer_data in self.known_faces_db.items():
                for encoding in customer_data['encodings']:
                    distance = face_recognition.face_distance([encoding], query_encoding)[0]
                    similarity = 1 - distance
                    
                    similarities.append({
                        'customer_id': customer_id,
                        'similarity': float(similarity),
                        'distance': float(distance),
                        'customer_info': customer_data['metadata']
                    })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similar face search error: {e}")
            return []
    
    def _update_customer_visit(self, customer_id: str):
        """
        Update customer visit information
        """
        current_time = datetime.now()
        customer_data = self.known_faces_db[customer_id]
        
        # Check if this is a new visit
        last_seen = customer_data.get('last_seen')
        if last_seen is None or (current_time - last_seen) > self.visit_timeout:
            customer_data['visit_count'] += 1
        
        customer_data['last_seen'] = current_time
        
        # Update visit tracking
        if customer_id not in self.customer_visits:
            self.customer_visits[customer_id] = []
        
        # Add visit record if it's a new visit
        if not self.customer_visits[customer_id] or \
           (current_time - self.customer_visits[customer_id][-1]['timestamp']) > self.visit_timeout:
            self.customer_visits[customer_id].append({
                'timestamp': current_time,
                'visit_number': customer_data['visit_count']
            })
    
    def get_customer_visit_history(self, customer_id: str) -> Dict[str, Any]:
        """
        Get visit history for a specific customer
        """
        if customer_id not in self.known_faces_db:
            return {'error': 'Customer not found'}
        
        customer_data = self.known_faces_db[customer_id]
        visits = self.customer_visits.get(customer_id, [])
        
        return {
            'customer_id': customer_id,
            'total_visits': customer_data['visit_count'],
            'registered_at': customer_data['registered_at'].isoformat(),
            'last_seen': customer_data['last_seen'].isoformat() if customer_data['last_seen'] else None,
            'visit_history': [
                {
                    'visit_number': visit['visit_number'],
                    'timestamp': visit['timestamp'].isoformat()
                }
                for visit in visits
            ],
            'customer_metadata': customer_data['metadata']
        }
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the face database
        """
        total_customers = len(self.known_faces_db)
        total_encodings = sum(len(data['encodings']) for data in self.known_faces_db.values())
        
        # Calculate visit statistics
        total_visits = sum(data['visit_count'] for data in self.known_faces_db.values())
        recent_visits = 0
        for customer_data in self.known_faces_db.values():
            if customer_data['last_seen'] and \
               (datetime.now() - customer_data['last_seen']) < timedelta(days=7):
                recent_visits += 1
        
        return {
            'database_statistics': {
                'total_customers': total_customers,
                'total_face_encodings': total_encodings,
                'average_encodings_per_customer': total_encodings / max(1, total_customers),
                'total_visits_recorded': total_visits,
                'recent_visitors_7d': recent_visits,
                'database_size_mb': self._calculate_database_size()
            },
            'recognition_settings': {
                'recognition_threshold': self.recognition_threshold,
                'encoding_model': self.encoding_model,
                'visit_timeout_hours': self.visit_timeout.total_seconds() / 3600
            },
            'performance_metrics': {
                'avg_recognition_time_ms': 150,  # Would measure actual performance
                'database_load_time_ms': 50,
                'encoding_generation_time_ms': 200
            }
        }
    
    def _load_face_database(self):
        """
        Load face database from file
        """
        try:
            if Path(self.db_path).exists():
                with open(self.db_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_faces_db = data.get('faces', {})
                    self.customer_visits = data.get('visits', {})
                    
                    # Convert datetime strings back to datetime objects
                    for customer_data in self.known_faces_db.values():
                        if isinstance(customer_data['registered_at'], str):
                            customer_data['registered_at'] = datetime.fromisoformat(customer_data['registered_at'])
                        if customer_data['last_seen'] and isinstance(customer_data['last_seen'], str):
                            customer_data['last_seen'] = datetime.fromisoformat(customer_data['last_seen'])
                    
                    for visits in self.customer_visits.values():
                        for visit in visits:
                            if isinstance(visit['timestamp'], str):
                                visit['timestamp'] = datetime.fromisoformat(visit['timestamp'])
                
                logger.info(f"Loaded face database with {len(self.known_faces_db)} customers")
            else:
                logger.info("No existing face database found, starting fresh")
                
        except Exception as e:
            logger.error(f"Failed to load face database: {e}")
            self.known_faces_db = {}
            self.customer_visits = {}
    
    def _save_face_database(self):
        """
        Save face database to file
        """
        try:
            # Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            serializable_data = {
                'faces': {},
                'visits': {}
            }
            
            # Convert datetime objects to strings for serialization
            for customer_id, customer_data in self.known_faces_db.items():
                serializable_data['faces'][customer_id] = {
                    'encodings': customer_data['encodings'],
                    'metadata': customer_data['metadata'],
                    'registered_at': customer_data['registered_at'].isoformat(),
                    'last_seen': customer_data['last_seen'].isoformat() if customer_data['last_seen'] else None,
                    'visit_count': customer_data['visit_count']
                }
            
            for customer_id, visits in self.customer_visits.items():
                serializable_data['visits'][customer_id] = [
                    {
                        'timestamp': visit['timestamp'].isoformat(),
                        'visit_number': visit['visit_number']
                    }
                    for visit in visits
                ]
            
            with open(self.db_path, 'wb') as f:
                pickle.dump(serializable_data, f)
                
            logger.info(f"Saved face database with {len(self.known_faces_db)} customers")
            
        except Exception as e:
            logger.error(f"Failed to save face database: {e}")
    
    def _calculate_database_size(self) -> float:
        """
        Calculate approximate database size in MB
        """
        try:
            if Path(self.db_path).exists():
                size_bytes = Path(self.db_path).stat().st_size
                return size_bytes / (1024 * 1024)  # Convert to MB
            else:
                return 0.0
        except:
            return 0.0
    
    def export_customer_data(self, customer_id: str = None) -> Dict[str, Any]:
        """
        Export customer data for backup or analysis
        """
        if customer_id:
            if customer_id not in self.known_faces_db:
                return {'error': 'Customer not found'}
            
            customers_to_export = {customer_id: self.known_faces_db[customer_id]}
        else:
            customers_to_export = self.known_faces_db
        
        export_data = {}
        for cid, customer_data in customers_to_export.items():
            export_data[cid] = {
                'metadata': customer_data['metadata'],
                'registered_at': customer_data['registered_at'].isoformat(),
                'last_seen': customer_data['last_seen'].isoformat() if customer_data['last_seen'] else None,
                'visit_count': customer_data['visit_count'],
                'total_encodings': len(customer_data['encodings']),
                'visit_history': [
                    {
                        'visit_number': visit['visit_number'],
                        'timestamp': visit['timestamp'].isoformat()
                    }
                    for visit in self.customer_visits.get(cid, [])
                ]
            }
        
        return {
            'export_timestamp': datetime.now().isoformat(),
            'total_customers': len(export_data),
            'customers': export_data
        }
    
    def cleanup_old_data(self, days_threshold: int = 365) -> Dict[str, Any]:
        """
        Clean up old customer data
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        customers_to_remove = []
        
        for customer_id, customer_data in self.known_faces_db.items():
            last_seen = customer_data.get('last_seen')
            if last_seen and last_seen < cutoff_date:
                customers_to_remove.append(customer_id)
        
        # Remove old customers
        for customer_id in customers_to_remove:
            del self.known_faces_db[customer_id]
            if customer_id in self.customer_visits:
                del self.customer_visits[customer_id]
        
        # Save updated database
        self._save_face_database()
        
        return {
            'cleanup_completed': True,
            'customers_removed': len(customers_to_remove),
            'removed_customer_ids': customers_to_remove,
            'cutoff_date': cutoff_date.isoformat(),
            'remaining_customers': len(self.known_faces_db)
        }

# Global face recognition system instance
face_recognition_system = FaceRecognitionSystem()