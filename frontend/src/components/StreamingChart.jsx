import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Pause, Activity, RotateCcw, Download } from 'lucide-react';

const StreamingChart = () => {
  const [data, setData] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamSpeed, setStreamSpeed] = useState(100); // ms
  const [amplitude, setAmplitude] = useState(0);
  const [rms, setRms] = useState(0);
  const [peakToPeak, setPeakToPeak] = useState(0);
  const intervalRef = useRef(null);
  const timeRef = useRef(0);

  useEffect(() => {
    if (isStreaming) {
      intervalRef.current = setInterval(() => {
        const time = timeRef.current;
        const newAmplitude = Math.sin(time / 10) * 0.5 + 
                            Math.sin(time / 5) * 0.3 + 
                            (Math.random() - 0.5) * 0.2;
        
        const newPoint = {
          time: parseFloat(time.toFixed(2)),
          amplitude: parseFloat(newAmplitude.toFixed(4))
        };
        
        setData(prev => {
          const updated = [...prev, newPoint];
          const latest = updated.slice(-100); // Keep last 100 points
          
          // Calculate statistics
          const amplitudes = latest.map(p => p.amplitude);
          const currentAmp = Math.abs(newAmplitude);
          const currentRms = Math.sqrt(amplitudes.reduce((sum, a) => sum + a * a, 0) / amplitudes.length);
          const currentPtp = Math.max(...amplitudes) - Math.min(...amplitudes);
          
          setAmplitude(currentAmp);
          setRms(currentRms);
          setPeakToPeak(currentPtp);
          
          return latest;
        });
        
        timeRef.current += 0.1;
      }, streamSpeed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isStreaming, streamSpeed]);

  const handleReset = () => {
    setData([]);
    timeRef.current = 0;
    setAmplitude(0);
    setRms(0);
    setPeakToPeak(0);
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
      `# Stream Speed: ${streamSpeed}ms`,
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
        {value.toFixed(4)}
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
          </div>
        </div>
        <p style={{ color: '#718096', fontSize: '0.875rem', margin: 0 }}>
          Live sensor data stream • {data.length} samples collected
        </p>
      </div>

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

      {/* Speed Control */}
      <div style={{
        background: '#f7fafc',
        padding: '1rem',
        borderRadius: '8px',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem'
      }}>
        <label style={{ 
          fontSize: '0.875rem', 
          fontWeight: '600', 
          color: '#4a5568',
          minWidth: '120px'
        }}>
          Stream Speed:
        </label>
        <input
          type="range"
          min="50"
          max="500"
          step="50"
          value={streamSpeed}
          onChange={(e) => setStreamSpeed(Number(e.target.value))}
          disabled={isStreaming}
          style={{
            flex: 1,
            cursor: isStreaming ? 'not-allowed' : 'pointer'
          }}
        />
        <span style={{ 
          fontSize: '0.875rem', 
          fontWeight: '600', 
          color: '#667eea',
          minWidth: '60px',
          fontFamily: 'monospace'
        }}>
          {streamSpeed}ms
        </span>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
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
            animationDuration={300}
            isAnimationActive={true}
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
          {isStreaming ? 'Streaming Active' : 'Stream Paused'}
        </span>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </div>
  );
};

export default StreamingChart;