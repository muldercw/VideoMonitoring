import React, { useState } from 'react';

const StreamForm = ({ onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    stream_name: '',
    stream_url: '',
    stream_type: 'rtsp'
  });

  const [errors, setErrors] = useState({});

  const streamTypes = [
    { value: 'rtsp', label: 'RTSP Stream' },
    { value: 'webcam', label: 'Webcam' },
    { value: 'file', label: 'Video File' },
    { value: 'http', label: 'HTTP Stream' }
  ];

  const validateForm = () => {
    const newErrors = {};

    if (!formData.stream_name.trim()) {
      newErrors.stream_name = 'Stream name is required';
    }

    if (!formData.stream_url.trim()) {
      newErrors.stream_url = 'Stream URL is required';
    } else if (formData.stream_type === 'rtsp' && !formData.stream_url.startsWith('rtsp://')) {
      newErrors.stream_url = 'RTSP URL must start with rtsp://';
    } else if (formData.stream_type === 'http' && !formData.stream_url.startsWith('http')) {
      newErrors.stream_url = 'HTTP URL must start with http:// or https://';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const getPlaceholder = () => {
    switch (formData.stream_type) {
      case 'rtsp':
        return 'rtsp://username:password@camera-ip:554/stream';
      case 'webcam':
        return '0 (for default camera) or /dev/video0';
      case 'file':
        return '/path/to/video.mp4';
      case 'http':
        return 'http://example.com/stream.mjpg';
      default:
        return 'Enter stream URL';
    }
  };

  return (
    <form onSubmit={handleSubmit} className="stream-form">
      <div className="form-group">
        <label htmlFor="stream_name" className="form-label">
          Stream Name *
        </label>
        <input
          type="text"
          id="stream_name"
          name="stream_name"
          value={formData.stream_name}
          onChange={handleChange}
          className={`form-control ${errors.stream_name ? 'error' : ''}`}
          placeholder="Enter a descriptive name for the stream"
        />
        {errors.stream_name && <div className="error-message">{errors.stream_name}</div>}
      </div>

      <div className="form-group">
        <label htmlFor="stream_type" className="form-label">
          Stream Type *
        </label>
        <select
          id="stream_type"
          name="stream_type"
          value={formData.stream_type}
          onChange={handleChange}
          className="form-control"
        >
          {streamTypes.map(type => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="stream_url" className="form-label">
          Stream URL *
        </label>
        <input
          type="text"
          id="stream_url"
          name="stream_url"
          value={formData.stream_url}
          onChange={handleChange}
          className={`form-control ${errors.stream_url ? 'error' : ''}`}
          placeholder={getPlaceholder()}
        />
        {errors.stream_url && <div className="error-message">{errors.stream_url}</div>}
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Stream'}
        </button>
      </div>
    </form>
  );
};

export default StreamForm;