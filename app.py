from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import uvicorn
import os
import cv2
import io
import time

from src.database import get_db, init_db
from src.models import VideoStream, VideoEvent, VideoAnalytics, SystemMetrics
from src.stream_manager import StreamManager
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Monitoring System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    is_running: Optional[bool] = False
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
    clip_path: Optional[str]

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
            logger.warning(f"Failed to initialize stream manager for stream {new_stream.stream_id}")
            # Don't fail the request, just log the warning
        else:
            # Automatically start the stream processing
            start_success = stream_manager.start_stream(new_stream.stream_id)
            if start_success:
                logger.info(f"Stream {new_stream.stream_id} started automatically after creation")
            else:
                logger.warning(f"Failed to auto-start stream {new_stream.stream_id}")
        
        # Return stream with running status
        stream_dict = {
            "stream_id": new_stream.stream_id,
            "stream_name": new_stream.stream_name,
            "stream_url": new_stream.stream_url,
            "stream_type": new_stream.stream_type,
            "is_active": new_stream.is_active,
            "is_running": stream_manager.active_streams.get(new_stream.stream_id, {}).get('running', False),
            "created_at": new_stream.created_at,
            "updated_at": new_stream.updated_at
        }
        
        return stream_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating stream: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create stream: {str(e)}")

@app.get("/streams", response_model=List[StreamResponse])
async def get_streams(db: Session = Depends(get_db)):
    try:
        streams = db.query(VideoStream).all()
        
        # Add running status from stream manager
        result = []
        for stream in streams:
            stream_dict = {
                "stream_id": stream.stream_id,
                "stream_name": stream.stream_name,
                "stream_url": stream.stream_url,
                "stream_type": stream.stream_type,
                "is_active": stream.is_active,
                "is_running": stream_manager.active_streams.get(stream.stream_id, {}).get('running', False),
                "created_at": stream.created_at,
                "updated_at": stream.updated_at
            }
            result.append(stream_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error fetching streams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams/{stream_id}", response_model=StreamResponse)
async def get_stream(stream_id: int, db: Session = Depends(get_db)):
    try:
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # Add running status from stream manager
        stream_dict = {
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "stream_url": stream.stream_url,
            "stream_type": stream.stream_type,
            "is_active": stream.is_active,
            "is_running": stream_manager.active_streams.get(stream.stream_id, {}).get('running', False),
            "created_at": stream.created_at,
            "updated_at": stream.updated_at
        }
        
        return stream_dict
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
        
        # Get all events for this stream to find associated files
        events = db.query(VideoEvent).filter(VideoEvent.stream_id == stream_id).all()
        
        # Delete associated files
        deleted_files = {"frames": 0, "clips": 0}
        for event in events:
            # Delete frame files
            if event.frame_path and os.path.exists(event.frame_path):
                try:
                    os.remove(event.frame_path)
                    deleted_files["frames"] += 1
                except Exception as e:
                    logger.warning(f"Failed to delete frame file {event.frame_path}: {e}")
            
            # Delete clip files
            if event.clip_path and os.path.exists(event.clip_path):
                try:
                    os.remove(event.clip_path)
                    deleted_files["clips"] += 1
                except Exception as e:
                    logger.warning(f"Failed to delete clip file {event.clip_path}: {e}")
        
        # Delete database entries
        # Delete events first (foreign key constraint)
        db.query(VideoEvent).filter(VideoEvent.stream_id == stream_id).delete()
        
        # Delete analytics
        db.query(VideoAnalytics).filter(VideoAnalytics.stream_id == stream_id).delete()
        
        # Delete stream
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if stream:
            db.delete(stream)
        
        db.commit()
        
        logger.info(f"Stream {stream_id} deleted: {deleted_files['frames']} frames, {deleted_files['clips']} clips, and all database entries removed")
        return {
            "message": f"Stream {stream_id} deleted successfully",
            "deleted_files": deleted_files
        }
    except Exception as e:
        logger.error(f"Error deleting stream {stream_id}: {e}")
        db.rollback()
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

# Video streaming endpoints
def generate_video_stream(stream_url: str, stream_type: str):
    """Generate video frames for streaming"""
    cap = None
    try:
        if stream_type == 'webcam':
            # For webcam, convert string to int if it's a number
            if stream_url.isdigit():
                cap = cv2.VideoCapture(int(stream_url))
            else:
                cap = cv2.VideoCapture(stream_url)
        else:
            cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open video stream: {stream_url}")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            if not ret:
                continue
            
            # Convert to bytes
            frame_bytes = buffer.tobytes()
            
            # Create multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Small delay to control frame rate
            time.sleep(0.033)  # ~30 FPS
    
    except Exception as e:
        logger.error(f"Error in video stream generation: {e}")
    finally:
        if cap:
            cap.release()

@app.get("/api/streams/{stream_id}/video")
async def stream_video(stream_id: int, db: Session = Depends(get_db)):
    """Stream video from a specific stream"""
    try:
        # Get stream info from database
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # For HTTP streams, we can redirect directly
        if stream.stream_type == 'http' and stream.stream_url.startswith('http'):
            # For HTTP video files, we can serve them directly
            return StreamingResponse(
                generate_video_stream(stream.stream_url, stream.stream_type),
                media_type="multipart/x-mixed-replace; boundary=frame"
            )
        else:
            # For other stream types, use OpenCV to process
            return StreamingResponse(
                generate_video_stream(stream.stream_url, stream.stream_type),
                media_type="multipart/x-mixed-replace; boundary=frame"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming video for stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streams/{stream_id}/hls/playlist.m3u8")
async def get_hls_playlist(stream_id: int, db: Session = Depends(get_db)):
    """Get HLS playlist for RTSP streams (placeholder)"""
    try:
        # Get stream info from database
        stream = db.query(VideoStream).filter(VideoStream.stream_id == stream_id).first()
        if not stream:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # This is a placeholder - in production, you'd use FFmpeg to convert RTSP to HLS
        hls_playlist = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
/api/streams/{stream_id}/video
#EXT-X-ENDLIST"""
        
        return StreamingResponse(
            io.StringIO(hls_playlist),
            media_type="application/vnd.apple.mpegurl"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating HLS playlist for stream {stream_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/frames/{frame_path:path}")
async def serve_frame(frame_path: str):
    """Serve event frame images"""
    try:
        file_path = os.path.join(frame_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Frame not found")
        
        with open(file_path, "rb") as f:
            content = f.read()
            
        return StreamingResponse(
            io.BytesIO(content),
            media_type="image/jpeg"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving frame {frame_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clips/{clip_path:path}")
async def serve_clip(clip_path: str):
    """Serve object clip images"""
    try:
        file_path = os.path.join(clip_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Clip not found")
        
        with open(file_path, "rb") as f:
            content = f.read()
            
        return StreamingResponse(
            io.BytesIO(content),
            media_type="image/jpeg"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving clip {clip_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)