import React from 'react';

const StatsCard = ({ title, value, icon, color = '#007bff' }) => {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ color }}>
        {icon}
      </div>
      <div className="stat-content">
        <div className="stat-number" style={{ color }}>
          {value}
        </div>
        <div className="stat-label">
          {title}
        </div>
      </div>
    </div>
  );
};

export default StatsCard;