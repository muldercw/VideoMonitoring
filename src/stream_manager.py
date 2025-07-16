import asyncio
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime
import time
import psutil

from .database import SessionLocal
from .models import VideoStream, VideoEvent, VideoAnalytics, SystemMetrics
from .video_processor import VideoProcessor

logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self):
        self.active_streams: Dict[int, Dict] = {}
        self.processors: Dict[int, VideoProcessor] = {}
        self.running = False
        self.system_monitor_thread = None
        
    def add_stream(self, stream_id: int, stream_url: str, stream_name: str) -> bool:
        try:
            db = SessionLocal()
            
            # Check if stream already exists
            existing_stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
            if existing_stream:
                existing_stream.stream_url = stream_url
                existing_stream.stream_name = stream_name
                existing_stream.is_active = True
                existing_stream.updated_at = datetime.utcnow()
            else:
                new_stream = VideoStream(
                    stream_id=stream_id,
                    stream_name=stream_name,
                    stream_url=stream_url,
                    is_active=True
                )
                db.add(new_stream)
            
            db.commit()
            db.close()
            
            # Initialize processor
            processor = VideoProcessor(stream_id, stream_url)
            if processor.initialize_stream():
                self.processors[stream_id] = processor
                self.active_streams[stream_id] = {
                    'name': stream_name,
                    'url': stream_url,
                    'thread': None,
                    'running': False
                }
                logger.info(f"Stream {stream_id} added successfully")
                return True
            else:
                logger.error(f"Failed to initialize processor for stream {stream_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding stream {stream_id}: {e}")
            return False
    
    def remove_stream(self, stream_id: int) -> bool:
        try:
            if stream_id in self.active_streams:
                self.stop_stream(stream_id)
                del self.active_streams[stream_id]
                
                if stream_id in self.processors:
                    self.processors[stream_id].release()
                    del self.processors[stream_id]
                
                # Update database
                db = SessionLocal()
                stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
                if stream:
                    stream.is_active = False
                    stream.updated_at = datetime.utcnow()
                    db.commit()
                db.close()
                
                logger.info(f"Stream {stream_id} removed successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing stream {stream_id}: {e}")
            return False
    
    def start_stream(self, stream_id: int) -> bool:
        try:
            if stream_id not in self.active_streams:
                logger.error(f"Stream {stream_id} not found")
                return False
            
            if self.active_streams[stream_id]['running']:
                logger.warning(f"Stream {stream_id} is already running")
                return True
            
            thread = threading.Thread(target=self._process_stream, args=(stream_id,))
            thread.daemon = True
            self.active_streams[stream_id]['thread'] = thread
            self.active_streams[stream_id]['running'] = True
            thread.start()
            
            logger.info(f"Stream {stream_id} started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting stream {stream_id}: {e}")
            return False
    
    def stop_stream(self, stream_id: int) -> bool:
        try:
            if stream_id in self.active_streams:
                self.active_streams[stream_id]['running'] = False
                if self.active_streams[stream_id]['thread']:
                    self.active_streams[stream_id]['thread'].join(timeout=5)
                logger.info(f"Stream {stream_id} stopped successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error stopping stream {stream_id}: {e}")
            return False
    
    def _process_stream(self, stream_id: int):
        processor = self.processors.get(stream_id)
        if not processor:
            logger.error(f"No processor found for stream {stream_id}")
            return
        
        logger.info(f"Processing stream {stream_id}")
        
        while self.active_streams[stream_id]['running']:
            try:
                ret, frame = processor.read_frame()
                if not ret:
                    logger.warning(f"Failed to read frame from stream {stream_id}")
                    time.sleep(1)
                    continue
                
                # Process frame
                analytics = processor.process_frame(frame)
                
                # Store analytics
                self._store_analytics(stream_id, analytics)
                
                # Check for events
                if analytics['motion_detected']:
                    self._handle_motion_event(stream_id, frame, analytics)
                
                if analytics['object_count'] > 0:
                    self._handle_object_events(stream_id, frame, analytics)
                
                # Brief pause to prevent overwhelming the system
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing stream {stream_id}: {e}")
                time.sleep(1)
        
        processor.release()
        logger.info(f"Stream {stream_id} processing stopped")
    
    def _store_analytics(self, stream_id: int, analytics: Dict):
        try:
            db = SessionLocal()
            analytics_record = VideoAnalytics(
                stream_id=stream_id,
                fps=analytics['fps'],
                frame_count=analytics['frame_count'],
                motion_detected=analytics['motion_detected'],
                object_count=analytics['object_count'],
                quality_score=analytics['quality_score'],
                processing_time_ms=analytics['processing_time_ms']
            )
            db.add(analytics_record)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Error storing analytics: {e}")
    
    def _handle_motion_event(self, stream_id: int, frame, analytics: Dict):
        try:
            processor = self.processors[stream_id]
            frame_path = processor.save_frame(frame, "motion")
            
            db = SessionLocal()
            event = VideoEvent(
                stream_id=stream_id,
                event_type="motion_detected",
                confidence=0.9,
                event_metadata={
                    'motion_area': analytics['motion_area'],
                    'frame_dimensions': analytics['frame_dimensions']
                },
                frame_path=frame_path
            )
            db.add(event)
            db.commit()
            db.close()
            
            logger.info(f"Motion event recorded for stream {stream_id}")
        except Exception as e:
            logger.error(f"Error handling motion event: {e}")
    
    def _handle_object_events(self, stream_id: int, frame, analytics: Dict):
        try:
            processor = self.processors[stream_id]
            frame_path = processor.save_frame(frame, "objects")
            
            db = SessionLocal()
            for obj in analytics['objects']:
                event = VideoEvent(
                    stream_id=stream_id,
                    event_type="object_detected",
                    confidence=obj['confidence'],
                    bounding_box=obj['bounding_box'],
                    event_metadata={
                        'object_type': obj['type'],
                        'area': obj['area']
                    },
                    frame_path=frame_path
                )
                db.add(event)
            db.commit()
            db.close()
            
            logger.info(f"Object events recorded for stream {stream_id}")
        except Exception as e:
            logger.error(f"Error handling object events: {e}")
    
    def start_system_monitoring(self):
        if not self.system_monitor_thread:
            self.system_monitor_thread = threading.Thread(target=self._monitor_system)
            self.system_monitor_thread.daemon = True
            self.system_monitor_thread.start()
            logger.info("System monitoring started")
    
    def _monitor_system(self):
        while self.running:
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                disk_usage = psutil.disk_usage('/').percent
                network_stats = psutil.net_io_counters()
                
                db = SessionLocal()
                metrics = SystemMetrics(
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    disk_usage=disk_usage,
                    network_usage=network_stats.bytes_sent + network_stats.bytes_recv,
                    active_streams=len([s for s in self.active_streams.values() if s['running']])
                )
                db.add(metrics)
                db.commit()
                db.close()
                
                time.sleep(60)  # Collect metrics every minute
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(60)
    
    def get_stream_status(self) -> Dict:
        return {
            'active_streams': len(self.active_streams),
            'running_streams': len([s for s in self.active_streams.values() if s['running']]),
            'streams': {
                sid: {
                    'name': info['name'],
                    'url': info['url'],
                    'running': info['running']
                }
                for sid, info in self.active_streams.items()
            }
        }
    
    def start(self):
        self.running = True
        self.start_system_monitoring()
        logger.info("Stream manager started")
    
    def stop(self):
        self.running = False
        for stream_id in list(self.active_streams.keys()):
            self.stop_stream(stream_id)
        logger.info("Stream manager stopped")