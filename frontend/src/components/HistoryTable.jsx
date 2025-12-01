import React from 'react';
import { Clock, TrendingUp, Download } from 'lucide-react';
import axios from 'axios';

const HistoryTable = ({ history }) => {
  const [downloadingIndex, setDownloadingIndex] = React.useState(null);

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

  const handleDownloadReport = async (item, index) => {
    setDownloadingIndex(index);
    try {
      // Make sure signal is an array
      const signalArray = Array.isArray(item.signal) ? item.signal : [];
      
      if (signalArray.length === 0) {
        alert('No signal data available for this prediction');
        return;
      }

      // Send request with correct format
      const response = await axios.post(
        'http://localhost:8000/diagnostic-report',
        {
          signal: signalArray,
          sampling_rate: 12000
        },
        {
          responseType: 'blob'
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bearing_diagnostic_report_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download report:', err);
      alert('Failed to generate report. Please try again.');
    } finally {
      setDownloadingIndex(null);
    }
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
              <th style={{ padding: '0.75rem', textAlign: 'center', fontSize: '0.875rem', fontWeight: '600', color: '#6b7280' }}>Report</th>
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
                <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                  <button
                    onClick={() => handleDownloadReport(item, index)}
                    disabled={downloadingIndex === index}
                    style={{
                      padding: '0.5rem 1rem',
                      background: downloadingIndex === index ? '#9ca3af' : '#6366f1',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: downloadingIndex === index ? 'not-allowed' : 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (downloadingIndex !== index) {
                        e.target.style.background = '#4f46e5';
                        e.target.style.transform = 'translateY(-2px)';
                        e.target.style.boxShadow = '0 4px 8px rgba(99, 102, 241, 0.3)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (downloadingIndex !== index) {
                        e.target.style.background = '#6366f1';
                        e.target.style.transform = 'translateY(0)';
                        e.target.style.boxShadow = 'none';
                      }
                    }}
                  >
                    <Download size={16} />
                    {downloadingIndex === index ? 'Generating...' : 'PDF'}
                  </button>
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