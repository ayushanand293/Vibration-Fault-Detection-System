import React from 'react';
import { Clock, TrendingUp } from 'lucide-react';

const HistoryTable = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '2rem',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        marginBottom: '2rem',
        textAlign: 'center',
        color: '#9ca3af'
      }}>
        <Clock size={48} style={{ margin: '0 auto 1rem' }} />
        <p>No prediction history yet. Run a diagnosis to see results here.</p>
      </div>
    );
  }

  const getStatusColor = (prediction) => {
    if (prediction === 'normal') return '#10b981';
    if (prediction === 'ball') return '#ef4444';
    if (prediction === 'inner_race') return '#f59e0b';
    if (prediction === 'outer_race') return '#3b82f6';
    return '#6b7280';
  };

  const getStatusBadge = (prediction) => {
    const color = getStatusColor(prediction);
    return (
      <span style={{
        background: color + '20',
        color: color,
        padding: '0.25rem 0.75rem',
        borderRadius: '9999px',
        fontSize: '0.875rem',
        fontWeight: '600'
      }}>
        {prediction.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <h2 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <TrendingUp size={24} color="#667eea" />
        Prediction History
      </h2>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#6b7280' }}>Timestamp</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#6b7280' }}>Prediction</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#6b7280' }}>Confidence</th>
              <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#6b7280' }}>Samples</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>
                  {new Date(item.timestamp).toLocaleString()}
                </td>
                <td style={{ padding: '0.75rem' }}>
                  {getStatusBadge(item.prediction)}
                </td>
                <td style={{ padding: '0.75rem', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{
                      flex: 1,
                      height: '8px',
                      background: '#e5e7eb',
                      borderRadius: '4px',
                      overflow: 'hidden',
                      maxWidth: '100px'
                    }}>
                      <div style={{
                        width: `${item.confidence * 100}%`,
                        height: '100%',
                        background: getStatusColor(item.prediction),
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                    <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>
                      {(item.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>
                  {item.sampleCount}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryTable;
