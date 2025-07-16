import cv2
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os
import json

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
        # Simplified object detection using contours
        # In a real implementation, you'd use YOLO, SSD, or similar
        objects = []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'type': 'object',
                        'confidence': 0.8,
                        'bounding_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                        'area': int(area)
                    })
        except Exception as e:
            logger.error(f"Object detection error: {e}")
        
        return objects
    
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