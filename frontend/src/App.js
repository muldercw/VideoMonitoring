import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Streams from './pages/Streams';
import Events from './pages/Events';
import Analytics from './pages/Analytics';
import SystemMonitor from './pages/SystemMonitor';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/streams" element={<Streams />} />
        <Route path="/events" element={<Events />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/system" element={<SystemMonitor />} />
      </Routes>
    </Layout>
  );
}

export default App;