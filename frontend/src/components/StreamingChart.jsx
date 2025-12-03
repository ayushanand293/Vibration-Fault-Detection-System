
import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Pause, Activity, RotateCcw, Download, FileText } from 'lucide-react';
import { downloadDiagnosticReport } from '../services/api';

const StreamingChart = ({ onPrediction }) => {
  const [data, setData] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamMode, setStreamMode] = useState('real'); // 'real' or 'random'
  const [streamSpeed, setStreamSpeed] = useState(50); // ms
  const [amplitude, setAmplitude] = useState(0);
  const [rms, setRms] = useState(0);
  const [peakToPeak, setPeakToPeak] = useState(0);

  // Prediction State
  const [prediction, setPrediction] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [currentScenario, setCurrentScenario] = useState(null);

  const eventSourceRef = useRef(null);
  const lastHistoryUpdateRef = useRef(0);
  const dataRef = useRef([]);

  useEffect(() => {
    if (isStreaming) {
      // Connect to backend stream with selected mode
      eventSourceRef.current = new EventSource(`http://localhost:8000/stream-signal?mode=${streamMode}`);

      eventSourceRef.current.onmessage = (event) => {
        const point = JSON.parse(event.data);

        setData(prev => {
          const updated = [...prev, {
            time: parseFloat(point.timestamp.toFixed(2)),
            amplitude: point.amplitude
          }];
          // Keep more points for report generation, but slice for display if needed
          // For now, let's keep last 2000 for a good report, but maybe only chart last 100?
          // Actually, let's just keep growing it but limit to say 5000 to avoid memory issues
          if (updated.length > 5000) updated.shift();

          // Update ref for access in other listeners
          dataRef.current = updated;

          const latest = updated;

          // Calculate statistics on recent window
          const recentWindow = latest.slice(-100);
          const amplitudes = recentWindow.map(p => p.amplitude);
          const currentAmp = Math.abs(point.amplitude);
          const currentRms = Math.sqrt(amplitudes.reduce((sum, a) => sum + a * a, 0) / amplitudes.length);
          const currentPtp = Math.max(...amplitudes) - Math.min(...amplitudes);

          setAmplitude(currentAmp);
          setRms(currentRms);
          setPeakToPeak(currentPtp);

          return latest;
        });
      };

      // Listen for prediction events
      eventSourceRef.current.addEventListener('prediction', (event) => {
        const predData = JSON.parse(event.data);
        setPrediction(predData.prediction);
        setConfidence(predData.confidence);
        setCurrentScenario(predData.scenario);

        // Get recent signal data for FFT and History
        // Use last 1024 points for a good FFT resolution, or whatever is available
        const recentSignal = dataRef.current.slice(-1024).map(d => d.amplitude);
        predData.signal = recentSignal;

        // Update main app state if callback provided
        if (onPrediction) {
          const now = Date.now();
          // Save to history only if 1 minute (60000ms) has passed since last save
          const shouldSaveToHistory = now - lastHistoryUpdateRef.current > 60000;

          if (shouldSaveToHistory) {
            lastHistoryUpdateRef.current = now;
          }

          onPrediction(predData, shouldSaveToHistory);
        }
      });

      eventSourceRef.current.onerror = (err) => {
        console.error("EventSource failed:", err);
        eventSourceRef.current.close();
        setIsStreaming(false);
      };

    } else {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [isStreaming, streamMode]); // Re-run when mode changes

  const handleReset = () => {
    setData([]);
    setAmplitude(0);
    setRms(0);
    setPeakToPeak(0);
    setPrediction(null);
    setConfidence(0);
    setCurrentScenario(null);
  };

  const handleExport = () => {
    // Create CSV header with metadata
    const timestamp = new Date().toISOString();
    const csvHeader = [
      '# Vibration Fault Detection System - Streaming Data Export',
      `# Export Date: ${new Date().toLocaleString()}`,
      `# Total Samples: ${data.length}`,
      `# Current Amplitude: ${amplitude.toFixed(4)}`,
      `# Current RMS: ${rms.toFixed(4)}`,
      `# Peak-to-Peak: ${peakToPeak.toFixed(4)}`,
      '#',
      '# Data Format: Time (seconds), Amplitude',
      'Time,Amplitude'
    ].join('\n');

    const csvData = data.map(d => `${d.time},${d.amplitude}`).join('\n');
    const fullCsv = `${csvHeader}\n${csvData}`;

    const blob = new Blob([fullCsv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vibration_stream_${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleGenerateReport = async () => {
    if (data.length < 100) {
      alert("Need at least 100 data points to generate a report.");
      return;
    }

    // Extract signal array from data objects
    const signalArray = data.map(d => d.amplitude);

    try {
      await downloadDiagnosticReport(signalArray);
    } catch (error) {
      console.error("Failed to generate report:", error);
      alert("Failed to generate report. See console for details.");
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          border: '2px solid #667eea',
          borderRadius: '8px',
          padding: '0.75rem',
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: '0 0 0.25rem 0', fontWeight: '600', color: '#667eea' }}>
            Time: {payload[0].payload.time.toFixed(2)}s
          </p>
          <p style={{ margin: 0, color: '#4a5568' }}>
            Amplitude: {payload[0].value.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  const StatCard = ({ label, value, icon, color }) => (
    <div style={{
      background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
      border: `2px solid ${color}30`,
      borderRadius: '10px',
      padding: '1rem',
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '1.25rem' }}>{icon}</span>
        <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#718096', textTransform: 'uppercase' }}>
          {label}
        </span>
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: color, fontFamily: 'monospace' }}>
        {typeof value === 'number' ? value.toFixed(4) : value}
      </div>
    </div>
  );

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h2 style={{
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}>
            <Activity size={28} color="#667eea" />
            <span style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Real-time Vibration Monitor
            </span>
          </h2>
          <div style={{
            display: 'flex',
            gap: '0.5rem',
            alignItems: 'center'
          }}>
            {/* Mode Toggle */}
            <div style={{
              display: 'flex',
              background: '#f3f4f6',
              padding: '4px',
              borderRadius: '8px',
              marginRight: '1rem'
            }}>
              <button
                onClick={() => !isStreaming && setStreamMode('real')}
                disabled={isStreaming}
                style={{
                  padding: '0.5rem 1rem',
                  background: streamMode === 'real' ? 'white' : 'transparent',
                  color: streamMode === 'real' ? '#667eea' : '#6b7280',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isStreaming ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  boxShadow: streamMode === 'real' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                Real Data
              </button>
              <button
                onClick={() => !isStreaming && setStreamMode('random')}
                disabled={isStreaming}
                style={{
                  padding: '0.5rem 1rem',
                  background: streamMode === 'random' ? 'white' : 'transparent',
                  color: streamMode === 'random' ? '#667eea' : '#6b7280',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isStreaming ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  boxShadow: streamMode === 'random' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                Random Data
              </button>
            </div>

            <button
              onClick={() => setIsStreaming(!isStreaming)}
              style={{
                padding: '0.625rem 1.25rem',
                background: isStreaming ? '#ef4444' : '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontWeight: '600',
                fontSize: '0.875rem',
                transition: 'all 0.3s ease',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
              }}
            >
              {isStreaming ? <><Pause size={16} /> Stop</> : <><Play size={16} /> Start</>}
            </button>
            <button
              onClick={handleReset}
              disabled={isStreaming}
              style={{
                padding: '0.625rem 1rem',
                background: isStreaming ? '#d1d5db' : '#6366f1',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: isStreaming ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontWeight: '600',
                fontSize: '0.875rem',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (!isStreaming) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 8px rgba(99, 102, 241, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isStreaming) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }
              }}
            >
              <RotateCcw size={16} /> Reset
            </button>
            <button
              onClick={handleExport}
              disabled={data.length === 0}
              style={{
                padding: '0.625rem 1rem',
                background: data.length === 0 ? '#d1d5db' : '#8b5cf6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: data.length === 0 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontWeight: '600',
                fontSize: '0.875rem',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (data.length > 0) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 8px rgba(139, 92, 246, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (data.length > 0) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }
              }}
            >
              <Download size={16} /> Export CSV
            </button>
            <button
              onClick={handleGenerateReport}
              disabled={data.length < 100}
              style={{
                padding: '0.625rem 1rem',
                background: data.length < 100 ? '#d1d5db' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: data.length < 100 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontWeight: '600',
                fontSize: '0.875rem',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                if (data.length >= 100) {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 4px 8px rgba(59, 130, 246, 0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (data.length >= 100) {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = 'none';
                }
              }}
            >
              <FileText size={16} /> Report
            </button>
          </div>
        </div>
        <p style={{ color: '#718096', fontSize: '0.875rem', margin: 0 }}>
          Live sensor data stream • {data.length} samples collected • Mode: {streamMode === 'real' ? 'Real CWRU Data' : 'Random Noise'}
        </p>
      </div>

      {/* Live Prediction Banner */}
      {prediction && (
        <div style={{
          marginBottom: '1.5rem',
          padding: '1rem',
          background: prediction === 'normal' ? '#d1fae5' : '#fee2e2',
          border: `2px solid ${prediction === 'normal' ? '#10b981' : '#ef4444'} `,
          borderRadius: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontWeight: 'bold', color: '#374151', marginRight: '0.5rem' }}>
              Live Diagnosis:
            </span>
            <span style={{
              fontWeight: '800',
              fontSize: '1.1rem',
              color: prediction === 'normal' ? '#047857' : '#b91c1c',
              textTransform: 'uppercase'
            }}>
              {prediction.replace('_', ' ')}
            </span>
          </div>
          <div style={{ fontSize: '0.9rem', color: '#4b5563' }}>
            Confidence: <strong>{(confidence * 100).toFixed(1)}%</strong>
            {currentScenario && (
              <span style={{ marginLeft: '1rem', fontSize: '0.8rem', opacity: 0.7 }}>
                (Simulating: {currentScenario})
              </span>
            )}
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      <div style={{
        display: 'flex',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <StatCard label="Amplitude" value={amplitude} icon="📊" color="#667eea" />
        <StatCard label="RMS" value={rms} icon="📈" color="#10b981" />
        <StatCard label="Peak-to-Peak" value={peakToPeak} icon="↕️" color="#f59e0b" />
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data.slice(-100)} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="time"
            label={{
              value: 'Time (s)',
              position: 'insideBottom',
              offset: -5,
              style: { fontSize: '14px', fontWeight: '600', fill: '#4a5568' }
            }}
            tick={{ fontSize: 12, fill: '#718096' }}
            domain={['auto', 'auto']}
          />
          <YAxis
            label={{
              value: 'Amplitude',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: '14px', fontWeight: '600', fill: '#4a5568' }
            }}
            tick={{ fontSize: 12, fill: '#718096' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="amplitude"
            stroke="#667eea"
            strokeWidth={2}
            dot={false}
            animationDuration={0}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Status Indicator */}
      <div style={{
        marginTop: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        justifyContent: 'center',
        padding: '0.5rem',
        background: isStreaming ? '#10b98120' : '#e5e7eb',
        borderRadius: '6px'
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: isStreaming ? '#10b981' : '#6b7280',
          animation: isStreaming ? 'pulse 2s infinite' : 'none'
        }} />
        <span style={{
          fontSize: '0.875rem',
          fontWeight: '600',
          color: isStreaming ? '#10b981' : '#6b7280'
        }}>
          {isStreaming ? 'Streaming Active - Connected to Backend' : 'Stream Paused'}
        </span>
      </div>

      <style>
        {`
@keyframes pulse {
  0 %, 100 % { opacity: 1; }
  50 % { opacity: 0.5; }
}
`}
      </style>
    </div>
  );
};

export default StreamingChart;