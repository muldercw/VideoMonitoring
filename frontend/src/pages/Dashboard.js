import React from 'react';
import { useDashboardSummary, useSystemStatus, useSystemMetrics } from '../hooks/useApi';
import StatsCard from '../components/StatsCard';
import SystemChart from '../components/SystemChart';
import RecentEvents from '../components/RecentEvents';

const Dashboard = () => {
  const { data: summary, isLoading: summaryLoading } = useDashboardSummary();
  const { data: systemStatus, isLoading: statusLoading } = useSystemStatus();
  const { data: metrics, isLoading: metricsLoading } = useSystemMetrics(1);

  if (summaryLoading || statusLoading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Monitor your video streams and system performance</p>
      </div>

      <div className="stats-grid">
        <StatsCard
          title="Total Streams"
          value={summary?.total_streams || 0}
          icon="🎥"
          color="#007bff"
        />
        <StatsCard
          title="Active Streams"
          value={summary?.active_streams || 0}
          icon="▶️"
          color="#28a745"
        />
        <StatsCard
          title="Events (24h)"
          value={summary?.recent_events_24h || 0}
          icon="⚡"
          color="#ffc107"
        />
        <StatsCard
          title="Running Streams"
          value={systemStatus?.stream_manager?.running_streams || 0}
          icon="🔄"
          color="#17a2b8"
        />
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>System Performance</h3>
          <SystemChart data={metrics} loading={metricsLoading} />
        </div>
        
        <div className="card">
          <h3>System Status</h3>
          <div className="system-status">
            <div className="status-item">
              <span className="status-label">System Status:</span>
              <span className={`status-badge ${systemStatus?.system_status === 'running' ? 'status-active' : 'status-inactive'}`}>
                {systemStatus?.system_status || 'Unknown'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Stream Manager:</span>
              <span className="status-badge status-active">Active</span>
            </div>
            <div className="status-item">
              <span className="status-label">Database:</span>
              <span className="status-badge status-active">Connected</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <RecentEvents />
        
        <div className="card">
          <h3>Quick Actions</h3>
          <div className="quick-actions">
            <a href="/streams" className="action-card">
              <div className="action-icon">🎥</div>
              <div className="action-content">
                <h4>Manage Streams</h4>
                <p>Add, configure, and monitor video streams</p>
              </div>
            </a>
            <a href="/events" className="action-card">
              <div className="action-icon">⚡</div>
              <div className="action-content">
                <h4>View Events</h4>
                <p>Browse detected events and alerts</p>
              </div>
            </a>
            <a href="/analytics" className="action-card">
              <div className="action-icon">📈</div>
              <div className="action-content">
                <h4>Analytics</h4>
                <p>Review performance metrics and insights</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;