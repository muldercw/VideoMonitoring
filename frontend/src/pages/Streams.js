import React, { useState } from 'react';
import { useStreams, useCreateStream, useStartStream, useStopStream, useDeleteStream } from '../hooks/useApi';
import StreamForm from '../components/StreamForm';
import StreamCard from '../components/StreamCard';
import Modal from '../components/Modal';
import VideoPlayer from '../components/VideoPlayer';

const Streams = () => {
  const [showForm, setShowForm] = useState(false);
  const [selectedStream, setSelectedStream] = useState(null);
  const [watchingStream, setWatchingStream] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  const { data: streams, isLoading, error } = useStreams();
  const createStreamMutation = useCreateStream();
  const startStreamMutation = useStartStream();
  const stopStreamMutation = useStopStream();
  const deleteStreamMutation = useDeleteStream();

  const handleCreateStream = async (streamData) => {
    try {
      await createStreamMutation.mutateAsync(streamData);
      setShowForm(false);
    } catch (error) {
      console.error('Failed to create stream:', error);
    }
  };

  const handleStartStream = async (streamId) => {
    try {
      await startStreamMutation.mutateAsync(streamId);
    } catch (error) {
      console.error('Failed to start stream:', error);
    }
  };

  const handleStopStream = async (streamId) => {
    try {
      await stopStreamMutation.mutateAsync(streamId);
    } catch (error) {
      console.error('Failed to stop stream:', error);
    }
  };

  const handleDeleteStream = async (streamId) => {
    if (window.confirm('Are you sure you want to delete this stream?')) {
      try {
        await deleteStreamMutation.mutateAsync(streamId);
      } catch (error) {
        console.error('Failed to delete stream:', error);
      }
    }
  };

  if (isLoading) {
    return <div className="loading">Loading streams...</div>;
  }

  if (error) {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Video Streams</h1>
          <p>Manage your video streams and monitoring sources</p>
        </div>
        <div className="error">Failed to load streams: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <div className="header-content">
          <h1>Video Streams</h1>
          <p>Manage your video streams and monitoring sources</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`btn ${viewMode === 'grid' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </button>
            <button 
              className={`btn ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('list')}
            >
              List
            </button>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowForm(true)}
          >
            ➕ Add Stream
          </button>
        </div>
      </div>

      {streams && streams.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🎥</div>
          <h3>No streams configured</h3>
          <p>Add your first video stream to start monitoring</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowForm(true)}
          >
            Add Stream
          </button>
        </div>
      ) : (
        <div className={`streams-container ${viewMode}`}>
          {streams?.map((stream) => (
            <StreamCard
              key={stream.stream_id}
              stream={stream}
              onStart={() => handleStartStream(stream.stream_id)}
              onStop={() => handleStopStream(stream.stream_id)}
              onDelete={() => handleDeleteStream(stream.stream_id)}
              onView={() => setSelectedStream(stream)}
              onWatch={() => setWatchingStream(stream)}
              viewMode={viewMode}
              isLoading={
                startStreamMutation.isLoading || 
                stopStreamMutation.isLoading || 
                deleteStreamMutation.isLoading
              }
            />
          ))}
        </div>
      )}

      {showForm && (
        <Modal
          title="Add New Stream"
          onClose={() => setShowForm(false)}
        >
          <StreamForm
            onSubmit={handleCreateStream}
            onCancel={() => setShowForm(false)}
            isLoading={createStreamMutation.isLoading}
          />
        </Modal>
      )}

      {selectedStream && (
        <Modal
          title={`Stream: ${selectedStream.stream_name}`}
          onClose={() => setSelectedStream(null)}
        >
          <div className="stream-details">
            <div className="detail-group">
              <label>Stream ID:</label>
              <span>{selectedStream.stream_id}</span>
            </div>
            <div className="detail-group">
              <label>Stream Name:</label>
              <span>{selectedStream.stream_name}</span>
            </div>
            <div className="detail-group">
              <label>Stream URL:</label>
              <span className="url">{selectedStream.stream_url}</span>
            </div>
            <div className="detail-group">
              <label>Stream Type:</label>
              <span>{selectedStream.stream_type}</span>
            </div>
            <div className="detail-group">
              <label>Status:</label>
              <span className={`status-badge ${selectedStream.is_active ? 'status-active' : 'status-inactive'}`}>
                {selectedStream.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="detail-group">
              <label>Created:</label>
              <span>{new Date(selectedStream.created_at).toLocaleString()}</span>
            </div>
            <div className="detail-group">
              <label>Updated:</label>
              <span>{new Date(selectedStream.updated_at).toLocaleString()}</span>
            </div>
          </div>
        </Modal>
      )}

      {watchingStream && (
        <Modal
          title="Video Player"
          onClose={() => setWatchingStream(null)}
          size="large"
        >
          <VideoPlayer
            streamId={watchingStream.stream_id}
            streamUrl={watchingStream.stream_url}
            streamType={watchingStream.stream_type}
            streamName={watchingStream.stream_name}
            onClose={() => setWatchingStream(null)}
          />
        </Modal>
      )}
    </div>
  );
};

export default Streams;