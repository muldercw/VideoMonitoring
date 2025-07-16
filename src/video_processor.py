import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import json
from skimage import measure, morphology
from skimage.segmentation import clear_border

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, stream_id: int, stream_url: str):
        self.stream_id = stream_id
        self.stream_url = stream_url
        self.cap = None
        self.fps = 0
        self.frame_count = 0
        self.is_running = False
        self.motion_threshold = 1000
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        
        # Initialize HOG descriptor for person detection
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Initialize cascade classifiers for face detection
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            logger.info(f"Face detection initialized for stream {stream_id}")
        except Exception as e:
            logger.error(f"Failed to initialize face detection for stream {stream_id}: {e}")
            self.face_cascade = None
        
        # Object detection parameters
        self.min_object_area = 500
        self.max_object_area = 50000
        
    def initialize_stream(self) -> bool:
        try:
            self.cap = cv2.VideoCapture(self.stream_url)
            if not self.cap.isOpened():
                logger.error(f"Failed to open stream {self.stream_url}")
                return False
            
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"Stream {self.stream_id} initialized with FPS: {self.fps}")
            return True
        except Exception as e:
            logger.error(f"Error initializing stream {self.stream_id}: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        start_time = time.time()
        
        # Basic analytics
        height, width = frame.shape[:2]
        quality_score = self.calculate_quality_score(frame)
        
        # Motion detection
        motion_detected, motion_area = self.detect_motion(frame)
        
        # Object detection (simplified)
        objects = self.detect_objects(frame)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'motion_detected': motion_detected,
            'motion_area': motion_area,
            'object_count': len(objects),
            'objects': objects,
            'quality_score': quality_score,
            'processing_time_ms': processing_time,
            'frame_dimensions': (width, height)
        }
    
    def detect_motion(self, frame: np.ndarray) -> Tuple[bool, int]:
        try:
            fg_mask = self.background_subtractor.apply(frame)
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_area = 0
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    motion_area += cv2.contourArea(contour)
            
            motion_detected = motion_area > self.motion_threshold
            return motion_detected, int(motion_area)
        except Exception as e:
            logger.error(f"Motion detection error: {e}")
            return False, 0
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """Enhanced object detection using OpenCV methods"""
        objects = []
        
        try:
            # 1. Person detection using HOG
            people = self.detect_people(frame)
            objects.extend(people)
            
            # 2. Face detection
            faces = self.detect_faces(frame)
            objects.extend(faces)
            
            # 3. Generic object detection using contours
            generic_objects = self.detect_generic_objects(frame)
            objects.extend(generic_objects)
            
        except Exception as e:
            logger.error(f"Object detection error: {e}")
        
        return objects
    
    def detect_people(self, frame: np.ndarray) -> List[Dict]:
        """Detect people using HOG descriptor"""
        people = []
        try:
            # Detect people
            boxes, weights = self.hog.detectMultiScale(frame, winStride=(8, 8), padding=(32, 32), scale=1.05)
            
            for (x, y, w, h), weight in zip(boxes, weights):
                if weight > 0.5:  # Confidence threshold
                    people.append({
                        'type': 'person',
                        'confidence': min(float(weight), 1.0),
                        'bounding_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                        'area': int(w * h),
                        'detection_method': 'hog'
                    })
        except Exception as e:
            logger.error(f"Person detection error: {e}")
        
        return people
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces using Haar cascades"""
        faces = []
        if self.face_cascade is None:
            return faces
            
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_rects = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            for (x, y, w, h) in face_rects:
                faces.append({
                    'type': 'face',
                    'confidence': 0.8,  # Haar cascades don't provide confidence
                    'bounding_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                    'area': int(w * h),
                    'detection_method': 'haar'
                })
        except Exception as e:
            logger.error(f"Face detection error: {e}")
        
        return faces
    
    def detect_generic_objects(self, frame: np.ndarray) -> List[Dict]:
        """Detect generic objects using contour analysis"""
        objects = []
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if self.min_object_area < area < self.max_object_area:
                    # Calculate bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate some features
                    aspect_ratio = w / h
                    extent = area / (w * h)
                    
                    # Classify object based on shape features
                    object_type = self.classify_object_by_shape(aspect_ratio, extent, area)
                    
                    objects.append({
                        'type': object_type,
                        'confidence': 0.6,
                        'bounding_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                        'area': int(area),
                        'detection_method': 'contour',
                        'features': {
                            'aspect_ratio': round(aspect_ratio, 2),
                            'extent': round(extent, 2)
                        }
                    })
        except Exception as e:
            logger.error(f"Generic object detection error: {e}")
        
        return objects
    
    def classify_object_by_shape(self, aspect_ratio: float, extent: float, area: int) -> str:
        """Classify object based on shape features"""
        # Simple heuristic classification
        if aspect_ratio > 2.0:
            return 'horizontal_object'
        elif aspect_ratio < 0.5:
            return 'vertical_object'
        elif extent > 0.8 and area > 5000:
            return 'large_rectangular_object'
        elif extent > 0.6:
            return 'rectangular_object'
        elif extent < 0.3:
            return 'irregular_object'
        else:
            return 'unknown_object'
    
    def calculate_quality_score(self, frame: np.ndarray) -> float:
        try:
            # Simple quality score based on sharpness (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            # Normalize to 0-1 range
            quality_score = min(laplacian_var / 1000, 1.0)
            return round(quality_score, 3)
        except Exception as e:
            logger.error(f"Quality calculation error: {e}")
            return 0.0
    
    def save_frame(self, frame: np.ndarray, event_type: str) -> Optional[str]:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"stream_{self.stream_id}_{event_type}_{timestamp}.jpg"
            filepath = os.path.join("videos", filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            cv2.imwrite(filepath, frame)
            
            return filepath
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
            return None
    
    def save_object_clip(self, frame: np.ndarray, bounding_box: Dict, object_type: str, event_id: str) -> Optional[str]:
        """Extract and save a clip of the detected object"""
        try:
            # Extract bounding box coordinates
            x = int(bounding_box['x'])
            y = int(bounding_box['y'])
            w = int(bounding_box['w'])
            h = int(bounding_box['h'])
            
            # Ensure coordinates are within frame bounds
            frame_height, frame_width = frame.shape[:2]
            x = max(0, min(x, frame_width - 1))
            y = max(0, min(y, frame_height - 1))
            w = min(w, frame_width - x)
            h = min(h, frame_height - y)
            
            # Extract the object region
            object_clip = frame[y:y+h, x:x+w]
            
            # Only save if the clip has reasonable dimensions
            if object_clip.shape[0] > 10 and object_clip.shape[1] > 10:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"stream_{self.stream_id}_{object_type}_clip_{timestamp}_{event_id}.jpg"
                filepath = os.path.join("clips", filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                cv2.imwrite(filepath, object_clip)
                
                return filepath
            else:
                logger.warning(f"Object clip too small: {object_clip.shape}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving object clip: {e}")
            return None
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        if not self.cap:
            return False, None
        
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
        return ret, frame
    
    def release(self):
        if self.cap:
            self.cap.release()
        self.is_running = False
        logger.info(f"Stream {self.stream_id} released")