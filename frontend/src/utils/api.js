import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints
export const apiEndpoints = {
  // System endpoints
  health: () => api.get('/health'),
  systemStatus: () => api.get('/system/status'),
  systemMetrics: (hours = 24) => api.get(`/system/metrics?hours=${hours}`),
  dashboardSummary: () => api.get('/dashboard/summary'),

  // Stream endpoints
  getStreams: () => api.get('/streams'),
  getStream: (streamId) => api.get(`/streams/${streamId}`),
  createStream: (streamData) => api.post('/streams', streamData),
  startStream: (streamId) => api.post(`/streams/${streamId}/start`),
  stopStream: (streamId) => api.post(`/streams/${streamId}/stop`),
  deleteStream: (streamId) => api.delete(`/streams/${streamId}`),

  // Analytics endpoints
  getStreamAnalytics: (streamId, hours = 24) => 
    api.get(`/streams/${streamId}/analytics?hours=${hours}`),
  getStreamEvents: (streamId, eventType = null, hours = 24) => {
    const params = new URLSearchParams({ hours: hours.toString() });
    if (eventType) params.append('event_type', eventType);
    return api.get(`/streams/${streamId}/events?${params}`);
  },
};

export default api;