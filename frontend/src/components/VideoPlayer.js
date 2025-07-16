import React, { useRef, useEffect, useState } from 'react';
import './VideoPlayer.css';

const VideoPlayer = ({ streamId, streamUrl, streamType, streamName, onClose }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadStart = () => {
      setIsLoading(true);
      setError(null);
    };

    const handleLoadedData = () => {
      setIsLoading(false);
    };

    const handleError = (e) => {
      setIsLoading(false);
      setError('Failed to load video stream');
      console.error('Video error:', e);
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);

    video.addEventListener('loadstart', handleLoadStart);
    video.addEventListener('loadeddata', handleLoadedData);
    video.addEventListener('error', handleError);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);

    return () => {
      video.removeEventListener('loadstart', handleLoadStart);
      video.removeEventListener('loadeddata', handleLoadedData);
      video.removeEventListener('error', handleError);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
    };
  }, []);

  const getVideoSrc = () => {
    // For different stream types, we need different approaches
    switch (streamType) {
      case 'http':
        return streamUrl;
      case 'rtsp':
        // RTSP streams need to be converted to HLS or similar web-compatible format
        // For now, we'll use a placeholder approach
        return `/api/streams/${streamId}/hls/playlist.m3u8`;
      case 'webcam':
        // Webcam streams would need to be served as a video stream
        return `/api/streams/${streamId}/video`;
      case 'file':
        // File streams can be served directly if they're web-compatible
        return streamUrl.startsWith('http') ? streamUrl : `/api/streams/${streamId}/video`;
      default:
        return streamUrl;
    }
  };

  const handlePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play().catch(e => {
        setError('Failed to play video');
        console.error('Play error:', e);
      });
    }
  };

  const handleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (video.requestFullscreen) {
      video.requestFullscreen();
    } else if (video.webkitRequestFullscreen) {
      video.webkitRequestFullscreen();
    } else if (video.mozRequestFullScreen) {
      video.mozRequestFullScreen();
    }
  };

  return (
    <div className="video-player">
      <div className="video-header">
        <h3>{streamName}</h3>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>
      
      <div className="video-container">
        {isLoading && (
          <div className="video-loading">
            <div className="loading-spinner"></div>
            <p>Loading video stream...</p>
          </div>
        )}
        
        {error && (
          <div className="video-error">
            <div className="error-icon">⚠️</div>
            <p>{error}</p>
            <button 
              className="btn btn-secondary"
              onClick={() => {
                setError(null);
                setIsLoading(true);
                videoRef.current?.load();
              }}
            >
              Retry
            </button>
          </div>
        )}
        
        <video
          ref={videoRef}
          className="video-element"
          controls
          autoPlay
          muted
          playsInline
          style={{ display: error ? 'none' : 'block' }}
        >
          <source src={getVideoSrc()} type="video/mp4" />
          {streamType === 'rtsp' && (
            <source src={getVideoSrc()} type="application/x-mpegURL" />
          )}
          Your browser does not support the video tag.
        </video>
      </div>
      
      <div className="video-controls">
        <button 
          className="btn btn-primary"
          onClick={handlePlayPause}
          disabled={error || isLoading}
        >
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>
        
        <button 
          className="btn btn-secondary"
          onClick={handleFullscreen}
          disabled={error || isLoading}
        >
          🔍 Fullscreen
        </button>
        
        <div className="video-info">
          <span className="stream-type">{streamType.toUpperCase()}</span>
          <span className="stream-status">
            {isLoading ? 'Loading...' : error ? 'Error' : isPlaying ? 'Playing' : 'Paused'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;