import React, { useState } from 'react';
import { Upload, Zap, Download } from 'lucide-react';
import { predictFault, getExampleSignal, downloadDiagnosticReport } from '../services/api';

const PredictionPanel = ({ onPrediction, onSignalLoaded }) => {
  const [signal, setSignal] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    
    try {
      const signalArray = signal.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
      
      if (signalArray.length < 100) {
        setError('Signal must have at least 100 samples');
        return;
      }
      
      const result = await predictFault(signalArray);
      onPrediction(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const loadExample = async (type) => {
    setLoading(true);
    setError('');
    
    try {
      const data = await getExampleSignal(type);
      const signalArray = data.signal;
      setSignal(signalArray.join(', '));
      
      if (onSignalLoaded) {
        onSignalLoaded(signalArray);
      }
    } catch (err) {
      setError('Failed to load example');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      const signalArray = signal.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
      await downloadDiagnosticReport(signalArray);
    } catch (err) {
      setError('Failed to generate report');
    }
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Zap size={24} color="#667eea" />
        Run Diagnosis
      </h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Signal Data (comma-separated values):
        </label>
        <textarea
          value={signal}
          onChange={(e) => setSignal(e.target.value)}
          placeholder="Load an example below..."
          rows={5}
          style={{
            width: '100%',
            padding: '0.75rem',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '0.875rem',
            fontFamily: 'monospace'
          }}
        />
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <button onClick={() => loadExample('normal')} disabled={loading} style={{ padding: '0.5rem 1rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' }}>
          Load Normal
        </button>
        <button onClick={() => loadExample('fault/ball')} disabled={loading} style={{ padding: '0.5rem 1rem', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' }}>
          Load Ball Fault
        </button>
        <button onClick={() => loadExample('fault/inner_race')} disabled={loading} style={{ padding: '0.5rem 1rem', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' }}>
          Load Inner Race
        </button>
        <button onClick={() => loadExample('fault/outer_race')} disabled={loading} style={{ padding: '0.5rem 1rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem' }}>
          Load Outer Race
        </button>
      </div>

      {error && (
        <div style={{ background: '#fee2e2', color: '#991b1b', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button onClick={handlePredict} disabled={loading || !signal} style={{ padding: '0.75rem 2rem', background: loading ? '#9ca3af' : '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Upload size={20} />
          {loading ? 'Analyzing...' : 'Predict'}
        </button>
        <button onClick={handleDownloadReport} disabled={!signal} style={{ padding: '0.75rem 2rem', background: '#6366f1', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Download size={20} />
          Download PDF
        </button>
      </div>
    </div>
  );
};

export default PredictionPanel;
