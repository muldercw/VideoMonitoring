import React from 'react';
import { useQuery } from 'react-query';
import { apiEndpoints } from '../utils/api';

const RecentEvents = () => {
  const { data: streams } = useQuery('streams', apiEndpoints.getStreams);
  
  // Get recent events from all streams
  const { data: allEvents, isLoading } = useQuery(
    ['recentEvents'],
    async () => {
      if (!streams || streams.length === 0) return [];
      
      const eventPromises = streams.map(stream => 
        apiEndpoints.getStreamEvents(stream.stream_id, null, 24)
          .then(response => response.data.map(event => ({
            ...event,
            stream_name: stream.stream_name
          })))
          .catch(() => [])
      );
      
      const results = await Promise.all(eventPromises);
      return results.flat().sort((a, b) => 
        new Date(b.event_time) - new Date(a.event_time)
      ).slice(0, 10);
    },
    {
      enabled: !!streams,
      refetchInterval: 30000,
    }
  );

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'motion_detected':
        return '🏃';
      case 'object_detected':
        return '📦';
      case 'person_detected':
        return '👤';
      case 'vehicle_detected':
        return '🚗';
      default:
        return '⚡';
    }
  };

  const getEventColor = (eventType) => {
    switch (eventType) {
      case 'motion_detected':
        return '#ffc107';
      case 'object_detected':
        return '#17a2b8';
      case 'person_detected':
        return '#28a745';
      case 'vehicle_detected':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  if (isLoading) {
    return (
      <div className="card">
        <h3>Recent Events</h3>
        <div className="loading">Loading events...</div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>Recent Events</h3>
      <div className="events-list">
        {allEvents && allEvents.length > 0 ? (
          allEvents.map((event, index) => (
            <div key={`${event.event_id}-${index}`} className="event-item">
              <div className="event-icon" style={{ color: getEventColor(event.event_type) }}>
                {getEventIcon(event.event_type)}
              </div>
              <div className="event-content">
                <div className="event-header">
                  <span className="event-type">{event.event_type.replace('_', ' ')}</span>
                  <span className="event-time">
                    {new Date(event.event_time).toLocaleString()}
                  </span>
                </div>
                <div className="event-details">
                  <span className="event-stream">Stream: {event.stream_name}</span>
                  {event.confidence && (
                    <span className="event-confidence">
                      Confidence: {(event.confidence * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="no-events">
            <div className="no-events-icon">⚡</div>
            <p>No recent events</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentEvents;