import React from 'react';
import { Activity } from 'lucide-react';

const Navbar = () => {
  return (
    <nav style={{
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      padding: '1rem 2rem',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Activity size={32} color="#667eea" />
        <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#1f2937' }}>
          Vibration Fault Detection System
        </h1>
      </div>
    </nav>
  );
};

export default Navbar;
