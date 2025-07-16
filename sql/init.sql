-- Create extension for TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create video_streams table
CREATE TABLE video_streams (
    stream_id SERIAL PRIMARY KEY,
    stream_name VARCHAR(255) NOT NULL,
    stream_url VARCHAR(500) NOT NULL,
    stream_type VARCHAR(50) NOT NULL DEFAULT 'rtsp',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create video_events table (hypertable for time-series data)
CREATE TABLE video_events (
    event_id SERIAL,
    stream_id INTEGER REFERENCES video_streams(stream_id),
    event_time TIMESTAMP NOT NULL DEFAULT NOW(),
    event_type VARCHAR(100) NOT NULL,
    confidence FLOAT,
    bounding_box JSONB,
    metadata JSONB,
    frame_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('video_events', 'event_time');

-- Create video_analytics table
CREATE TABLE video_analytics (
    analytics_id SERIAL,
    stream_id INTEGER REFERENCES video_streams(stream_id),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    fps FLOAT,
    frame_count INTEGER,
    motion_detected BOOLEAN DEFAULT FALSE,
    object_count INTEGER DEFAULT 0,
    quality_score FLOAT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('video_analytics', 'timestamp');

-- Create system_metrics table
CREATE TABLE system_metrics (
    metric_id SERIAL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT,
    network_usage FLOAT,
    active_streams INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('system_metrics', 'timestamp');

-- Create indexes for better performance
CREATE INDEX idx_video_events_stream_id ON video_events (stream_id);
CREATE INDEX idx_video_events_event_type ON video_events (event_type);
CREATE INDEX idx_video_analytics_stream_id ON video_analytics (stream_id);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics (timestamp);

-- Create continuous aggregates for hourly analytics
CREATE MATERIALIZED VIEW hourly_analytics
WITH (timescaledb.continuous) AS
SELECT 
    stream_id,
    time_bucket('1 hour', timestamp) AS hour,
    AVG(fps) AS avg_fps,
    SUM(frame_count) AS total_frames,
    COUNT(*) FILTER (WHERE motion_detected = TRUE) AS motion_events,
    AVG(quality_score) AS avg_quality,
    AVG(processing_time_ms) AS avg_processing_time
FROM video_analytics
GROUP BY stream_id, hour;

-- Create retention policies
SELECT add_retention_policy('video_events', INTERVAL '30 days');
SELECT add_retention_policy('video_analytics', INTERVAL '90 days');
SELECT add_retention_policy('system_metrics', INTERVAL '7 days');