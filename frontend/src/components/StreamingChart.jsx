import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Pause } from 'lucide-react';

const StreamingChart = () => {
  const [data, setData] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isStreaming) {
      let time = 0;
      intervalRef.current = setInterval(() => {
        const newPoint = {
          time: time,
          amplitude: Math.sin(time / 10) * 0.5 + (Math.random() - 0.5) * 0.2
        };
        
        setData(prev => {
          const updated = [...prev, newPoint];
          return updated.slice(-50);
        });
        
        time += 0.1;
      }, 100);
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
  }, [isStreaming]);

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      marginBottom: '2rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0 }}>Real-time Vibration Signal</h2>
        <button
          onClick={() => setIsStreaming(!isStreaming)}
          style={{
            padding: '0.5rem 1rem',
            background: isStreaming ? '#ef4444' : '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          {isStreaming ? <><Pause size={16} /> Stop</> : <><Play size={16} /> Start</>}
        </button>
      </div>
      
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }} />
          <YAxis label={{ value: 'Amplitude', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Line type="monotone" dataKey="amplitude" stroke="#667eea" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StreamingChart;
