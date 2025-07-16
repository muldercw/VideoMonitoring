import React, { useState } from 'react';
import { useStreams } from '../hooks/useApi';
import { useQuery } from 'react-query';
import { apiEndpoints } from '../utils/api';

const Events = () => {
  const [selectedStream, setSelectedStream] = useState('all');
  const [selectedEventType, setSelectedEventType] = useState('face_detected');
  const [timeRange, setTimeRange] = useState(24);

  const { data: streams, isLoading: streamsLoading } = useStreams();

  const { data: events, isLoading: eventsLoading, error: eventsError } = useQuery(
    ['allEvents', selectedStream, selectedEventType, timeRange],
    async () => {
      if (!streams) return [];
      
      const streamsToQuery = selectedStream === 'all' 
        ? streams 
        : streams.filter(s => s.stream_id === parseInt(selectedStream));
      
      const eventPromises = streamsToQuery.map(stream => 
        apiEndpoints.getStreamEvents(
          stream.stream_id, 
          selectedEventType === 'all' ? null : selectedEventType, 
          timeRange
        )
          .then(response => response.data.map(event => ({
            ...event,
            stream_name: stream.stream_name
          })))
          .catch(() => [])
      );
      
      const results = await Promise.all(eventPromises);
      return results.flat().sort((a, b) => 
        new Date(b.event_time) - new Date(a.event_time)
      );
    },
    {
      enabled: !!streams,
      refetchInterval: 30000,
    }
  );

  const eventTypes = [
    { value: 'all', label: 'All Events' },
    { value: 'face_detected', label: 'Face Detected' },
    { value: 'person_detected', label: 'Person Detected' },
    { value: 'motion_detected', label: 'Motion Detected' },
    { value: 'object_detected', label: 'Object Detected' }
  ];

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'face_detected':
        return '😊';
      case 'person_detected':
        return '👤';
      case 'motion_detected':
        return '🏃';
      case 'object_detected':
        return '📦';
      default:
        return '⚡';
    }
  };

  const getEventColor = (eventType) => {
    switch (eventType) {
      case 'face_detected':
        return '#ff6b6b';
      case 'person_detected':
        return '#28a745';
      case 'motion_detected':
        return '#ffc107';
      case 'object_detected':
        return '#17a2b8';
      default:
        return '#6c757d';
    }
  };

  if (streamsLoading) {
    return <div className="loading">Loading events...</div>;
  }

  if (eventsError) {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Events</h1>
          <p>Monitor detected events across all video streams</p>
        </div>
        <div className="error">
          Failed to load events: {eventsError.message}
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Events</h1>
        <p>Monitor detected events across all video streams</p>
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
              <option value="all">All Streams</option>
              {streams?.map(stream => (
                <option key={stream.stream_id} value={stream.stream_id}>
                  {stream.stream_name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Event Type:</label>
            <select 
              value={selectedEventType} 
              onChange={(e) => setSelectedEventType(e.target.value)}
              className="form-control"
            >
              {eventTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
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

      <div className="events-container">
        {eventsLoading ? (
          <div className="loading">Loading events...</div>
        ) : events && events.length > 0 ? (
          <div className="events-grid">
            {events.map((event, index) => (
              <div key={`${event.event_id}-${index}`} className="event-card-compact">
                <div className="event-preview">
                  {event.clip_path ? (
                    <div className="event-thumbnail">
                      <img 
                        src={`/api/clips/${event.clip_path}`} 
                        alt="Detected object"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <div className="event-overlay">
                        <div className="event-icon" style={{ color: getEventColor(event.event_type) }}>
                          {getEventIcon(event.event_type)}
                        </div>
                      </div>
                    </div>
                  ) : event.frame_path && (
                    <div className="event-thumbnail">
                      <img 
                        src={`/api/frames/${event.frame_path}`} 
                        alt="Event frame"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <div className="event-overlay">
                        <div className="event-icon" style={{ color: getEventColor(event.event_type) }}>
                          {getEventIcon(event.event_type)}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="event-info-compact">
                  <div className="event-title">
                    <h4>{event.event_type.replace('_', ' ')}</h4>
                    <span className="event-confidence">
                      {event.confidence ? `${(event.confidence * 100).toFixed(0)}%` : 'N/A'}
                    </span>
                  </div>
                  
                  <div className="event-meta">
                    <span className="event-stream">{event.stream_name}</span>
                    <span className="event-time">
                      {new Date(event.event_time).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  {event.bounding_box && (
                    <div className="event-location">
                      📍 {event.bounding_box.x}, {event.bounding_box.y} 
                      ({event.bounding_box.w}×{event.bounding_box.h})
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">⚡</div>
            <h3>No events found</h3>
            <p>No events match your current filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Events;