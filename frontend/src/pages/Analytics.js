import React, { useState } from 'react';
import { useStreams, useStreamAnalytics } from '../hooks/useApi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Analytics = () => {
  const [selectedStream, setSelectedStream] = useState('');
  const [timeRange, setTimeRange] = useState(24);

  const { data: streams, isLoading: streamsLoading } = useStreams();
  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useStreamAnalytics(
    selectedStream ? parseInt(selectedStream) : null,
    timeRange
  );

  // Select first stream by default
  React.useEffect(() => {
    if (streams && streams.length > 0 && !selectedStream) {
      setSelectedStream(streams[0].stream_id.toString());
    }
  }, [streams, selectedStream]);

  const processAnalyticsData = (data) => {
    if (!data || data.length === 0) return [];
    
    return data.map(item => ({
      time: new Date(item.timestamp).toLocaleTimeString(),
      fps: item.fps || 0,
      frameCount: item.frame_count || 0,
      motionDetected: item.motion_detected ? 1 : 0,
      objectCount: item.object_count || 0,
      qualityScore: item.quality_score || 0,
      processingTime: item.processing_time_ms || 0
    }));
  };

  const getStreamStats = (data) => {
    if (!data || data.length === 0) return null;
    
    const totalFrames = data.reduce((sum, item) => sum + (item.frame_count || 0), 0);
    const avgFps = data.reduce((sum, item) => sum + (item.fps || 0), 0) / data.length;
    const avgQuality = data.reduce((sum, item) => sum + (item.quality_score || 0), 0) / data.length;
    const avgProcessingTime = data.reduce((sum, item) => sum + (item.processing_time_ms || 0), 0) / data.length;
    const motionEvents = data.filter(item => item.motion_detected).length;
    const totalObjects = data.reduce((sum, item) => sum + (item.object_count || 0), 0);
    
    return {
      totalFrames,
      avgFps: avgFps.toFixed(1),
      avgQuality: (avgQuality * 100).toFixed(1),
      avgProcessingTime: avgProcessingTime.toFixed(1),
      motionEvents,
      totalObjects
    };
  };

  if (streamsLoading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (!streams || streams.length === 0) {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Analytics</h1>
          <p>Performance metrics and insights for your video streams</p>
        </div>
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>No streams available</h3>
          <p>Add video streams to view analytics</p>
        </div>
      </div>
    );
  }

  if (analyticsError) {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Analytics</h1>
          <p>Performance metrics and insights for your video streams</p>
        </div>
        <div className="error">
          Failed to load analytics: {analyticsError.message}
        </div>
      </div>
    );
  }

  const chartData = processAnalyticsData(analytics);
  const stats = getStreamStats(analytics);
  const selectedStreamData = streams.find(s => s.stream_id === parseInt(selectedStream));

  return (
    <div className="container">
      <div className="page-header">
        <h1>Analytics</h1>
        <p>Performance metrics and insights for your video streams</p>
      </div>

      <div className="filters-section">
        <div className="filters-row">
          <div className="filter-group">
            <label>Stream:</label>
            <select 
              value={selectedStream} 
              onChange={(e) => setSelectedStream(e.target.value)}
              className="form-control"
            >
              {streams.map(stream => (
                <option key={stream.stream_id} value={stream.stream_id}>
                  {stream.stream_name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Time Range:</label>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
              className="form-control"
            >
              <option value={1}>Last 1 Hour</option>
              <option value={6}>Last 6 Hours</option>
              <option value={24}>Last 24 Hours</option>
              <option value={168}>Last 7 Days</option>
            </select>
          </div>
        </div>
      </div>

      {selectedStreamData && (
        <div className="stream-info-card">
          <h3>{selectedStreamData.stream_name}</h3>
          <div className="stream-details">
            <span className="detail-item">
              <strong>Type:</strong> {selectedStreamData.stream_type}
            </span>
            <span className="detail-item">
              <strong>Status:</strong> 
              <span className={`status-badge ${selectedStreamData.is_active ? 'status-active' : 'status-inactive'}`}>
                {selectedStreamData.is_active ? 'Active' : 'Inactive'}
              </span>
            </span>
          </div>
        </div>
      )}

      {analyticsLoading ? (
        <div className="loading">Loading analytics data...</div>
      ) : stats ? (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{stats.totalFrames}</div>
              <div className="stat-label">Total Frames</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.avgFps}</div>
              <div className="stat-label">Average FPS</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.avgQuality}%</div>
              <div className="stat-label">Average Quality</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.avgProcessingTime}ms</div>
              <div className="stat-label">Avg Processing Time</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.motionEvents}</div>
              <div className="stat-label">Motion Events</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.totalObjects}</div>
              <div className="stat-label">Objects Detected</div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Performance Metrics</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="fps" 
                    stroke="#007bff" 
                    name="FPS" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="qualityScore" 
                    stroke="#28a745" 
                    name="Quality Score" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="processingTime" 
                    stroke="#ffc107" 
                    name="Processing Time (ms)" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h3>Detection Activity</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="motionDetected" fill="#ffc107" name="Motion Detected" />
                  <Bar dataKey="objectCount" fill="#17a2b8" name="Objects Detected" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>No analytics data</h3>
          <p>No analytics data available for the selected stream and time range</p>
        </div>
      )}
    </div>
  );
};

export default Analytics;