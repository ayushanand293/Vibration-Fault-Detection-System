import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Activity } from 'lucide-react';

const FFTChart = ({ signal }) => {
  // Move computeFFT BEFORE useMemo
  const computeFFT = (signal) => {
    const N = Math.min(signal.length, 1024); // Increased from 512 for more detail
    const result = [];
    
    for (let k = 0; k < N; k++) {
      let real = 0;
      let imag = 0;
      
      for (let n = 0; n < N; n++) {
        const angle = (2 * Math.PI * k * n) / N;
        real += signal[n] * Math.cos(angle);
        imag -= signal[n] * Math.sin(angle);
      }
      
      const magnitude = Math.sqrt(real * real + imag * imag) / N;
      result.push(magnitude);
    }
    
    return result;
  };

  const fftData = useMemo(() => {
    if (!signal || signal.length < 100) return [];
    
    const fft = computeFFT(signal);
    const halfLength = Math.floor(fft.length / 2);
    const samplingRate = 12000;
    
    return fft.slice(0, halfLength).map((magnitude, index) => ({
      frequency: (index * samplingRate) / fft.length,
      magnitude: magnitude
    })).filter(d => d.frequency <= 3000 && d.frequency > 0); // Increased frequency range
  }, [signal]);

  // Find peak frequencies
  const peakFrequencies = useMemo(() => {
    if (fftData.length === 0) return [];
    
    const sorted = [...fftData].sort((a, b) => b.magnitude - a.magnitude);
    return sorted.slice(0, 3); // Top 3 peaks
  }, [fftData]);

  if (!signal || signal.length < 100) {
    return null;
  }

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
            {`Frequency: ${payload[0].payload.frequency.toFixed(2)} Hz`}
          </p>
          <p style={{ margin: 0, color: '#4a5568' }}>
            {`Magnitude: ${payload[0].value.toExponential(3)}`}
          </p>
        </div>
      );
    }
    return null;
  };

  const CustomLabel = ({ viewBox, value, fill }) => {
    const { x, y } = viewBox;
    return (
      <text
        x={x}
        y={y - 10}
        fill={fill}
        fontSize={11}
        fontWeight={600}
        textAnchor="middle"
      >
        {value}
      </text>
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
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ 
          marginTop: 0, 
          marginBottom: '0.5rem',
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem' 
        }}>
          <Activity size={24} color="#667eea" />
          <span style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Frequency Spectrum (FFT)
          </span>
        </h2>
        <p style={{ color: '#718096', fontSize: '0.875rem', margin: 0 }}>
          Fast Fourier Transform analysis showing frequency components
        </p>
      </div>

      {/* Peak Frequencies Info */}
      {peakFrequencies.length > 0 && (
        <div style={{
          background: 'linear-gradient(135deg, #667eea10 0%, #764ba210 100%)',
          border: '2px solid #667eea20',
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <h4 style={{ 
            margin: '0 0 0.75rem 0', 
            fontSize: '0.875rem', 
            fontWeight: '600',
            color: '#4a5568',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            🎯 Dominant Frequencies:
          </h4>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(3, 1fr)', 
            gap: '0.75rem' 
          }}>
            {peakFrequencies.map((peak, idx) => (
              <div key={idx} style={{
                background: 'white',
                padding: '0.75rem',
                borderRadius: '8px',
                border: `2px solid ${['#667eea', '#764ba2', '#8b5cf6'][idx]}40`,
                textAlign: 'center'
              }}>
                <div style={{ 
                  fontSize: '1.25rem', 
                  fontWeight: '700', 
                  color: ['#667eea', '#764ba2', '#8b5cf6'][idx],
                  fontFamily: 'monospace'
                }}>
                  {peak.frequency.toFixed(2)} Hz
                </div>
                <div style={{ 
                  fontSize: '0.75rem', 
                  color: '#718096',
                  marginTop: '0.25rem'
                }}>
                  Mag: {peak.magnitude.toExponential(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div style={{ paddingTop: '1rem' }}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={fftData} margin={{ top: 40, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="frequency" 
              label={{ 
                value: 'Frequency (Hz)', 
                position: 'insideBottom', 
                offset: -10,
                style: { fontSize: '14px', fontWeight: '600', fill: '#4a5568' }
              }}
              tick={{ fontSize: 12, fill: '#718096' }}
              tickCount={10}
            />
            <YAxis 
              label={{ 
                value: 'Magnitude', 
                angle: -90, 
                position: 'insideLeft',
                style: { fontSize: '14px', fontWeight: '600', fill: '#4a5568' }
              }}
              tick={{ fontSize: 12, fill: '#718096' }}
              tickFormatter={(value) => value.toExponential(1)}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Reference lines for peak frequencies WITH labels */}
            {peakFrequencies.map((peak, idx) => (
              <ReferenceLine 
                key={idx}
                x={peak.frequency} 
                stroke={['#667eea', '#764ba2', '#8b5cf6'][idx]}
                strokeDasharray="5 5"
                strokeWidth={2}
                label={{
                  position: 'top',
                  value: `${peak.frequency.toFixed(1)}Hz`,
                  fill: ['#667eea', '#764ba2', '#8b5cf6'][idx],
                  fontSize: 11,
                  fontWeight: 600
                }}
              />
            ))}
            
            <Line 
              type="monotone" 
              dataKey="magnitude" 
              stroke="#667eea" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#667eea', stroke: 'white', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Additional Info */}
      <div style={{
        marginTop: '1rem',
        padding: '0.75rem',
        background: '#f7fafc',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.875rem',
        color: '#718096'
      }}>
        <span>📊 Sample Rate: <strong style={{ color: '#4a5568' }}>12 kHz</strong></span>
        <span>📈 FFT Size: <strong style={{ color: '#4a5568' }}>1024 points</strong></span>
        <span>🔍 Frequency Range: <strong style={{ color: '#4a5568' }}>0 - 3000 Hz</strong></span>
      </div>
    </div>
  );
};

export default FFTChart;