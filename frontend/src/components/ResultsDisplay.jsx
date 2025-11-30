import React from 'react';
import { CheckCircle, AlertTriangle } from 'lucide-react';

const ResultsDisplay = ({ prediction }) => {
  if (!prediction) return null;

  const getStatusColor = () => {
    if (prediction.prediction === 'normal') return '#10b981';
    return '#ef4444';
  };

  const getStatusIcon = () => {
    if (prediction.prediction === 'normal') {
      return <CheckCircle size={48} color="#10b981" />;
    }
    return <AlertTriangle size={48} color="#ef4444" />;
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginTop: 0 }}>Diagnosis Result</h2>
      
      <div style={{ textAlign: 'center', padding: '2rem 0' }}>
        {getStatusIcon()}
        <h3 style={{ 
          fontSize: '2rem', 
          margin: '1rem 0',
          color: getStatusColor(),
          textTransform: 'uppercase'
        }}>
          {prediction.prediction.replace('_', ' ')}
        </h3>
        <p style={{ fontSize: '1.25rem', color: '#6b7280' }}>
          Confidence: <strong>{(prediction.confidence * 100).toFixed(1)}%</strong>
        </p>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h4 style={{ marginBottom: '1rem' }}>Probabilities:</h4>
        {Object.entries(prediction.probabilities).map(([key, value]) => (
          <div key={key} style={{ marginBottom: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
              <span style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>
              <span style={{ fontWeight: '600' }}>{(value * 100).toFixed(1)}%</span>
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              background: '#e5e7eb', 
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{ 
                width: `${value * 100}%`, 
                height: '100%', 
                background: '#667eea',
                transition: 'width 0.3s ease'
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsDisplay;
