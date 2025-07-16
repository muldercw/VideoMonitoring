# VideoMonitoring

A comprehensive dockerized video monitoring system that leverages TimescaleDB for time-series data storage, Python for processing, and Docker for containerization.

## Features

- **Live Video Stream Processing**: Real-time video ingestion from multiple sources (RTSP, webcam, file)
- **Motion Detection**: Automated motion detection with configurable sensitivity
- **Object Detection**: Basic object detection and tracking
- **Time-Series Analytics**: Powered by TimescaleDB for efficient time-series data storage
- **REST API**: Full REST API for stream management and data retrieval
- **System Monitoring**: Real-time system metrics and performance monitoring
- **Event Storage**: Automatic event detection and frame capture
- **Scalable Architecture**: Docker-based deployment with horizontal scaling support

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Video Streams │───▶│  Video Monitor  │───▶│   TimescaleDB   │
│  (RTSP/Webcam)  │    │   (FastAPI)     │    │  (Time-Series)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │      Redis      │    │  Frame Storage  │
                       │   (Caching)     │    │   (Local/S3)    │
                       └─────────────────┘    └─────────────────┘
```

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/muldercw/VideoMonitoring.git
   cd VideoMonitoring
   ```

2. **Start the system**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Stream Management
- `POST /streams` - Create new video stream
- `GET /streams` - List all streams
- `GET /streams/{stream_id}` - Get stream details
- `POST /streams/{stream_id}/start` - Start stream processing
- `POST /streams/{stream_id}/stop` - Stop stream processing
- `DELETE /streams/{stream_id}` - Delete stream

### Analytics & Events
- `GET /streams/{stream_id}/analytics` - Get stream analytics
- `GET /streams/{stream_id}/events` - Get stream events
- `GET /system/metrics` - Get system metrics
- `GET /dashboard/summary` - Get dashboard summary

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql://postgres:password@timescaledb:5432/video_monitoring
REDIS_URL=redis://redis:6379
LOG_LEVEL=INFO
VIDEO_STORAGE_PATH=/app/videos
MOTION_THRESHOLD=1000
```

## Testing

Run the test suite:
```bash
python test_system.py
```

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start TimescaleDB
docker-compose up -d timescaledb redis

# Run the application
python app.py
```

### Adding New Features
1. Update database models in `src/models.py`
2. Add processing logic in `src/video_processor.py`
3. Update API endpoints in `app.py`
4. Add tests in `test_system.py`

## Database Schema

### Tables
- `video_streams` - Stream configuration and metadata
- `video_events` - Time-series event data (motion, objects)
- `video_analytics` - Performance and quality metrics
- `system_metrics` - System resource usage

### Hypertables
All time-series data is stored in TimescaleDB hypertables for optimal performance:
- Automatic partitioning by time
- Continuous aggregates for analytics
- Retention policies for data management

## Monitoring

The system provides comprehensive monitoring:
- Real-time stream status
- System resource usage
- Processing performance metrics
- Event detection statistics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
