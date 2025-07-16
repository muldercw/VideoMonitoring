import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const SystemChart = ({ data, loading }) => {
  if (loading) {
    return <div className="loading">Loading metrics...</div>;
  }

  // Comprehensive data validation
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <div className="no-data">No metrics data available</div>;
  }

  // Transform data for the chart with safety checks
  const chartData = data
    .filter(item => item && typeof item === 'object' && item.timestamp)
    .map(item => ({
      time: new Date(item.timestamp).toLocaleTimeString(),
      cpu: Number(item.cpu_usage) || 0,
      memory: Number(item.memory_usage) || 0,
      disk: Number(item.disk_usage) || 0,
      activeStreams: Number(item.active_streams) || 0
    }));

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="cpu" 
            stroke="#ff7300" 
            name="CPU %" 
            strokeWidth={2}
            yAxisId="left"
          />
          <Line 
            type="monotone" 
            dataKey="memory" 
            stroke="#8884d8" 
            name="Memory %" 
            strokeWidth={2}
            yAxisId="left"
          />
          <Line 
            type="monotone" 
            dataKey="disk" 
            stroke="#82ca9d" 
            name="Disk %" 
            strokeWidth={2}
            yAxisId="left"
          />
          <Line 
            type="monotone" 
            dataKey="activeStreams" 
            stroke="#ffc658" 
            name="Active Streams" 
            strokeWidth={2}
            yAxisId="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SystemChart;