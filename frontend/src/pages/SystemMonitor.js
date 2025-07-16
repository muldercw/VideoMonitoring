import React from 'react';
import { useSystemStatus, useSystemMetrics } from '../hooks/useApi';
import SystemChart from '../components/SystemChart';

const SystemMonitor = () => {
  const { data: systemStatus, isLoading: statusLoading } = useSystemStatus();
  const { data: metrics, isLoading: metricsLoading } = useSystemMetrics(24);

  const getSystemHealth = () => {
    if (!metrics || metrics.length === 0) return 'Unknown';
    
    const latest = metrics[metrics.length - 1];
    const avgCpu = latest.cpu_usage || 0;
    const avgMemory = latest.memory_usage || 0;
    const avgDisk = latest.disk_usage || 0;
    
    if (avgCpu > 80 || avgMemory > 80 || avgDisk > 80) return 'Critical';
    if (avgCpu > 60 || avgMemory > 60 || avgDisk > 60) return 'Warning';
    return 'Good';
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'Good':
        return '#28a745';
      case 'Warning':
        return '#ffc107';
      case 'Critical':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getLatestMetrics = () => {
    if (!metrics || metrics.length === 0) return null;
    return metrics[metrics.length - 1];
  };

  if (statusLoading) {
    return <div className="loading">Loading system status...</div>;
  }

  const systemHealth = getSystemHealth();
  const latestMetrics = getLatestMetrics();

  return (
    <div className="container">
      <div className="page-header">
        <h1>System Monitor</h1>
        <p>Monitor system health and performance metrics</p>
      </div>

      <div className="system-overview">
        <div className="health-card">
          <h3>System Health</h3>
          <div className="health-status">
            <div 
              className="health-indicator"
              style={{ backgroundColor: getHealthColor(systemHealth) }}
            >
              {systemHealth}
            </div>
            <div className="health-details">
              <div className="health-item">
                <span className="health-label">Status:</span>
                <span className={`status-badge ${systemStatus?.system_status === 'running' ? 'status-active' : 'status-inactive'}`}>
                  {systemStatus?.system_status || 'Unknown'}
                </span>
              </div>
              <div className="health-item">
                <span className="health-label">Uptime:</span>
                <span>Running</span>
              </div>
              <div className="health-item">
                <span className="health-label">Last Updated:</span>
                <span>{new Date().toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="streams-status">
          <h3>Stream Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <div className="status-number">{systemStatus?.stream_manager?.active_streams || 0}</div>
              <div className="status-label">Active Streams</div>
            </div>
            <div className="status-item">
              <div className="status-number">{systemStatus?.stream_manager?.running_streams || 0}</div>
              <div className="status-label">Running Streams</div>
            </div>
          </div>
        </div>
      </div>

      {latestMetrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>CPU Usage</h4>
            <div className="metric-value">{latestMetrics.cpu_usage?.toFixed(1) || 0}%</div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${latestMetrics.cpu_usage || 0}%`,
                  backgroundColor: latestMetrics.cpu_usage > 80 ? '#dc3545' : latestMetrics.cpu_usage > 60 ? '#ffc107' : '#28a745'
                }}
              />
            </div>
          </div>

          <div className="metric-card">
            <h4>Memory Usage</h4>
            <div className="metric-value">{latestMetrics.memory_usage?.toFixed(1) || 0}%</div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${latestMetrics.memory_usage || 0}%`,
                  backgroundColor: latestMetrics.memory_usage > 80 ? '#dc3545' : latestMetrics.memory_usage > 60 ? '#ffc107' : '#28a745'
                }}
              />
            </div>
          </div>

          <div className="metric-card">
            <h4>Disk Usage</h4>
            <div className="metric-value">{latestMetrics.disk_usage?.toFixed(1) || 0}%</div>
            <div className="metric-bar">
              <div 
                className="metric-fill"
                style={{ 
                  width: `${latestMetrics.disk_usage || 0}%`,
                  backgroundColor: latestMetrics.disk_usage > 80 ? '#dc3545' : latestMetrics.disk_usage > 60 ? '#ffc107' : '#28a745'
                }}
              />
            </div>
          </div>

          <div className="metric-card">
            <h4>Active Streams</h4>
            <div className="metric-value">{latestMetrics.active_streams || 0}</div>
            <div className="metric-label">Currently Processing</div>
          </div>
        </div>
      )}

      <div className="charts-section">
        <div className="card">
          <h3>System Performance (24 Hours)</h3>
          <SystemChart data={metrics} loading={metricsLoading} />
        </div>
      </div>

      <div className="system-info">
        <div className="card">
          <h3>System Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">System Status:</span>
              <span className="info-value">{systemStatus?.system_status || 'Unknown'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Database:</span>
              <span className="info-value">TimescaleDB - Connected</span>
            </div>
            <div className="info-item">
              <span className="info-label">Cache:</span>
              <span className="info-value">Redis - Connected</span>
            </div>
            <div className="info-item">
              <span className="info-label">API Version:</span>
              <span className="info-value">v1.0.0</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-time">{new Date().toLocaleTimeString()}</div>
              <div className="activity-description">System monitoring active</div>
            </div>
            <div className="activity-item">
              <div className="activity-time">{new Date(Date.now() - 60000).toLocaleTimeString()}</div>
              <div className="activity-description">Performance metrics collected</div>
            </div>
            <div className="activity-item">
              <div className="activity-time">{new Date(Date.now() - 120000).toLocaleTimeString()}</div>
              <div className="activity-description">Stream manager status updated</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;