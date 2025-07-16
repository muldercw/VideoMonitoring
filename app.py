from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import uvicorn
import os

from src.database import get_db, init_db
from src.models import VideoStream, VideoEvent, VideoAnalytics, SystemMetrics
from src.stream_manager import StreamManager
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Monitoring System", version="1.0.0")

# Initialize stream manager
stream_manager = StreamManager()

# Pydantic models
class StreamCreate(BaseModel):
    stream_name: str
    stream_url: str
    stream_type: str = "rtsp"

class StreamResponse(BaseModel):
    stream_id: int
    stream_name: str
    stream_url: str
    stream_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EventResponse(BaseModel):
    event_id: int
    stream_id: int
    event_time: datetime
    event_type: str
    confidence: Optional[float]
    bounding_box: Optional[dict]
    event_metadata: Optional[dict]
    frame_path: Optional[str]

class AnalyticsResponse(BaseModel):
    analytics_id: int
    stream_id: int
    timestamp: datetime
    fps: Optional[float]
    frame_count: Optional[int]
    motion_detected: bool
    object_count: int
    quality_score: Optional[float]
    processing_time_ms: Optional[int]

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        stream_manager.start()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    stream_manager.stop()
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    return {"message": "Video Monitoring System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Stream management endpoints
@app.post("/streams", response_model=StreamResponse)
async def create_stream(stream_data: StreamCreate, db: Session = Depends(get_db)):
    try:
        # Create stream in database
        new_stream = VideoStream(
            stream_name=stream_data.stream_name,
            stream_url=stream_data.stream_url,
            stream_type=stream_data.stream_type,
            is_active=True
        )
        db.add(new_stream)
        db.commit()
        db.refresh(new_stream)
        
        # Add to stream manager
        success = stream_manager.add_stream(
            new_stream.stream_id,
            stream_data.stream_url,
            stream_data.stream_name
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to initialize stream")
        
        return new_stream
    except Exception as e:
        logger.error(f"Error creating stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams", response_model=List[StreamResponse])
async def get_streams(db: Session = Depends(get_db)):
    try:
        streams = db.query(VideoStream).all()
        return streams
    except Exception as e:
        logger.error(f"Error fetching streams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams/{stream_id}", response_model=StreamResponse)
async def get_stream(stream_id: int, db: Session = Depends(get_db)):
    try:
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        return stream
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/streams/{stream_id}/start")
async def start_stream(stream_id: int, db: Session = Depends(get_db)):
    try:
        # Verify stream exists
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        success = stream_manager.start_stream(stream_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start stream")
        
        return {"message": f"Stream {stream_id} started successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/streams/{stream_id}/stop")
async def stop_stream(stream_id: int):
    try:
        success = stream_manager.stop_stream(stream_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to stop stream")
        
        return {"message": f"Stream {stream_id} stopped successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/streams/{stream_id}")
async def delete_stream(stream_id: int, db: Session = Depends(get_db)):
    try:
        # Stop stream first
        stream_manager.stop_stream(stream_id)
        
        # Remove from stream manager
        stream_manager.remove_stream(stream_id)
        
        # Update database
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if stream:
            stream.is_active = False
            stream.updated_at = datetime.utcnow()
            db.commit()
        
        return {"message": f"Stream {stream_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.get("/streams/{stream_id}/analytics", response_model=List[AnalyticsResponse])
async def get_stream_analytics(
    stream_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        analytics = db.query(VideoAnalytics).filter(
            VideoAnalytics.stream_id == stream_id,
            VideoAnalytics.timestamp >= start_time
        ).order_by(VideoAnalytics.timestamp.desc()).limit(1000).all()
        
        return analytics
    except Exception as e:
        logger.error(f"Error fetching analytics for stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams/{stream_id}/events", response_model=List[EventResponse])
async def get_stream_events(
    stream_id: int,
    event_type: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        query = db.query(VideoEvent).filter(
            VideoEvent.stream_id == stream_id,
            VideoEvent.event_time >= start_time
        )
        
        if event_type:
            query = query.filter(VideoEvent.event_type == event_type)
        
        events = query.order_by(VideoEvent.event_time.desc()).limit(1000).all()
        return events
    except Exception as e:
        logger.error(f"Error fetching events for stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System monitoring endpoints
@app.get("/system/status")
async def get_system_status():
    try:
        stream_status = stream_manager.get_stream_status()
        return {
            "system_status": "running",
            "timestamp": datetime.utcnow(),
            "stream_manager": stream_status
        }
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/metrics")
async def get_system_metrics(hours: int = 24, db: Session = Depends(get_db)):
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(SystemMetrics).filter(
            SystemMetrics.timestamp >= start_time
        ).order_by(SystemMetrics.timestamp.desc()).limit(1000).all()
        
        return metrics
    except Exception as e:
        logger.error(f"Error fetching system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard endpoints
@app.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    try:
        # Get stream counts
        total_streams = db.query(VideoStream).count()
        active_streams = db.query(VideoStream).filter(VideoStream.is_active == True).count()
        
        # Get recent events count
        recent_events = db.query(VideoEvent).filter(
            VideoEvent.event_time >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Get recent analytics
        recent_analytics = db.query(VideoAnalytics).filter(
            VideoAnalytics.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return {
            "total_streams": total_streams,
            "active_streams": active_streams,
            "recent_events_24h": recent_events,
            "recent_analytics_1h": recent_analytics,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)