import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity } from 'lucide-react';

const FFTChart = ({ signal }) => {
  // Move computeFFT BEFORE useMemo
  const computeFFT = (signal) => {
    const N = Math.min(signal.length, 512);
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
    })).filter(d => d.frequency <= 2000 && d.frequency > 0);
  }, [signal]);

  if (!signal || signal.length < 100) {
    return null;
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <h2 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Activity size={24} color="#667eea" />
        Frequency Spectrum (FFT)
      </h2>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={fftData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="frequency" 
            label={{ value: 'Frequency (Hz)', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            label={{ value: 'Magnitude', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value) => value.toExponential(3)}
            labelFormatter={(value) => `${value.toFixed(1)} Hz`}
          />
          <Line 
            type="monotone" 
            dataKey="magnitude" 
            stroke="#667eea" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FFTChart;
