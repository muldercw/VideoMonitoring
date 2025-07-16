import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Streams', href: '/streams', icon: '🎥' },
    { name: 'Events', href: '/events', icon: '⚡' },
    { name: 'Analytics', href: '/analytics', icon: '📈' },
    { name: 'System', href: '/system', icon: '🖥️' },
  ];

  return (
    <div className="layout">
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>Video Monitor</h2>
          <button 
            className="sidebar-toggle mobile-only"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ✕
          </button>
        </div>
        
        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`nav-item ${location.pathname === item.href ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-text">{item.name}</span>
            </Link>
          ))}
        </nav>
      </div>

      <div className="main-content">
        <header className="header">
          <div className="header-left">
            <button 
              className="sidebar-toggle mobile-only"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              ☰
            </button>
            <h1>Video Monitoring System</h1>
          </div>
          <div className="header-right">
            <div className="status-indicator">
              <span className="status-dot online"></span>
              <span>System Online</span>
            </div>
          </div>
        </header>

        <main className="content">
          {children}
        </main>
      </div>

      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>}
    </div>
  );
};

export default Layout;