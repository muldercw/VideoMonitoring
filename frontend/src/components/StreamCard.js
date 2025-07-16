import React from 'react';

const StreamCard = ({ stream, onStart, onStop, onDelete, onView, viewMode, isLoading }) => {
  const isActive = stream.is_active;
  const streamTypeIcons = {
    rtsp: '📡',
    webcam: '📷',
    file: '🎬',
    http: '🌐'
  };

  if (viewMode === 'list') {
    return (
      <div className="stream-list-item">
        <div className="stream-info">
          <div className="stream-icon">
            {streamTypeIcons[stream.stream_type] || '🎥'}
          </div>
          <div className="stream-details">
            <h3>{stream.stream_name}</h3>
            <p className="stream-url">{stream.stream_url}</p>
            <div className="stream-meta">
              <span className="stream-type">{stream.stream_type.toUpperCase()}</span>
              <span className={`status-badge ${isActive ? 'status-active' : 'status-inactive'}`}>
                {isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
        <div className="stream-actions">
          <button className="btn btn-secondary" onClick={onView}>
            View Details
          </button>
          {isActive ? (
            <button 
              className="btn btn-danger" 
              onClick={onStop}
              disabled={isLoading}
            >
              ⏸️ Stop
            </button>
          ) : (
            <button 
              className="btn btn-success" 
              onClick={onStart}
              disabled={isLoading}
            >
              ▶️ Start
            </button>
          )}
          <button 
            className="btn btn-danger" 
            onClick={onDelete}
            disabled={isLoading}
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stream-card">
      <div className="stream-header">
        <div className="stream-icon">
          {streamTypeIcons[stream.stream_type] || '🎥'}
        </div>
        <div className="stream-status">
          <span className={`status-badge ${isActive ? 'status-active' : 'status-inactive'}`}>
            {isActive ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
      
      <div className="stream-content">
        <h3 className="stream-name">{stream.stream_name}</h3>
        <p className="stream-url">{stream.stream_url}</p>
        <div className="stream-meta">
          <span className="stream-type">{stream.stream_type.toUpperCase()}</span>
          <span className="stream-id">ID: {stream.stream_id}</span>
        </div>
      </div>

      <div className="stream-actions">
        <button className="btn btn-secondary" onClick={onView}>
          View Details
        </button>
        <div className="action-buttons">
          {isActive ? (
            <button 
              className="btn btn-danger" 
              onClick={onStop}
              disabled={isLoading}
            >
              ⏸️ Stop
            </button>
          ) : (
            <button 
              className="btn btn-success" 
              onClick={onStart}
              disabled={isLoading}
            >
              ▶️ Start
            </button>
          )}
          <button 
            className="btn btn-danger" 
            onClick={onDelete}
            disabled={isLoading}
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};

export default StreamCard;