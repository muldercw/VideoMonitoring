from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class VideoStream(Base):
    __tablename__ = "video_streams"
    
    stream_id = Column(Integer, primary_key=True, index=True)
    stream_name = Column(String(255), nullable=False)
    stream_url = Column(String(500), nullable=False)
    stream_type = Column(String(50), default="rtsp")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    events = relationship("VideoEvent", back_populates="stream")
    analytics = relationship("VideoAnalytics", back_populates="stream")

class VideoEvent(Base):
    __tablename__ = "video_events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("video_streams.stream_id"))
    event_time = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(100), nullable=False)
    confidence = Column(Float)
    bounding_box = Column(JSON)
    event_metadata = Column(JSON)
    frame_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stream = relationship("VideoStream", back_populates="events")

class VideoAnalytics(Base):
    __tablename__ = "video_analytics"
    
    analytics_id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("video_streams.stream_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    fps = Column(Float)
    frame_count = Column(Integer)
    motion_detected = Column(Boolean, default=False)
    object_count = Column(Integer, default=0)
    quality_score = Column(Float)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    stream = relationship("VideoStream", back_populates="analytics")

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    metric_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    network_usage = Column(Float)
    active_streams = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)