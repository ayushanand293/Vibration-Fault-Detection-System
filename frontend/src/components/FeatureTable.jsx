import React from 'react';
import { Database } from 'lucide-react';

const FeatureTable = ({ features }) => {
  if (!features) return null;

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <h2 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Database size={24} color="#667eea" />
        Extracted Features
      </h2>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Feature</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>Value</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(features).map(([key, value]) => (
              <tr key={key} style={{ borderBottom: '1px solid #e5e7eb' }}>
                <td style={{ padding: '0.75rem', textTransform: 'capitalize' }}>
                  {key.replace(/_/g, ' ')}
                </td>
                <td style={{ padding: '0.75rem', textAlign: 'right', fontFamily: 'monospace' }}>
                  {typeof value === 'number' ? value.toFixed(6) : value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FeatureTable;
