import React, { useState } from 'react';
import { Upload, Zap, Download, Paperclip } from 'lucide-react';
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
      
      // Load signal FIRST so FFT chart appears
      if (onSignalLoaded) {
        onSignalLoaded(signalArray);
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

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const values = text.split(/[,\n\r\s]+/).map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
        
        if (values.length < 100) {
          setError('CSV file must contain at least 100 samples');
          return;
        }
        
        setSignal(values.join(', '));
        
        setError('');
      } catch (err) {
        setError('Failed to read CSV file');
      }
    };
    reader.readAsText(file);
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
          placeholder="Load an example below or attach a CSV file..."
          rows={12}
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

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <button onClick={() => loadExample('normal')} disabled={loading} style={{ padding: '0.75rem 1rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500' }}>
          Load Normal
        </button>
        <button onClick={() => loadExample('fault/ball')} disabled={loading} style={{ padding: '0.75rem 1rem', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500' }}>
          Load Ball Fault
        </button>
        <button onClick={() => loadExample('fault/inner_race')} disabled={loading} style={{ padding: '0.75rem 1rem', background: '#f59e0b', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500' }}>
          Load Inner Race
        </button>
        <button onClick={() => loadExample('fault/outer_race')} disabled={loading} style={{ padding: '0.75rem 1rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.875rem', fontWeight: '500' }}>
          Load Outer Race
        </button>
      </div>

      {error && (
        <div style={{ background: '#fee2e2', color: '#991b1b', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <input
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
        id="csv-file-input"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
        <label htmlFor="csv-file-input" style={{ padding: '0.875rem', background: '#8b5cf6', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
          <Paperclip size={20} />
          Attach CSV
        </label>
        <button onClick={handlePredict} disabled={loading || !signal} style={{ padding: '0.875rem', background: loading ? '#9ca3af' : '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
          <Upload size={20} />
          {loading ? 'Analyzing...' : 'Predict'}
        </button>
        <button onClick={handleDownloadReport} disabled={!signal} style={{ padding: '0.875rem', background: '#6366f1', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '1rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
          <Download size={20} />
          Download PDF
        </button>
      </div>
    </div>
  );
};

export default PredictionPanel;