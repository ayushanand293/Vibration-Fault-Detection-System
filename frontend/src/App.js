import React, { useState } from 'react';
import Navbar from './components/Navbar';
import StreamingChart from './components/StreamingChart';
import PredictionPanel from './components/PredictionPanel';
import ResultsDisplay from './components/ResultsDisplay';
import FeatureTable from './components/FeatureTable';
import FFTChart from './components/FFTChart';
import HistoryTable from './components/HistoryTable';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [currentSignal, setCurrentSignal] = useState(null);
  const [history, setHistory] = useState([]);

  const handlePrediction = (result, saveToHistory = true) => {
    setPrediction(result);

    // Update current signal for FFT chart if provided
    if (result.signal && result.signal.length > 0) {
      setCurrentSignal(result.signal);
    }

    if (saveToHistory) {
      const historyEntry = {
        timestamp: new Date().toISOString(),
        prediction: result.prediction,
        confidence: result.confidence,
        sampleCount: result.signal ? result.signal.length : (currentSignal ? currentSignal.length : 0),
        signal: result.signal || currentSignal || []
      };

      setHistory(prev => [historyEntry, ...prev].slice(0, 10));
    }
  };

  const handleSignalLoaded = (signalArray) => {
    setCurrentSignal(signalArray);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Navbar />

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
        <StreamingChart onPrediction={handlePrediction} />

        {/* Updated grid layout with uniform heights */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          marginBottom: '2rem'
        }}>
          <PredictionPanel
            onPrediction={handlePrediction}
            onSignalLoaded={handleSignalLoaded}
          />

          {prediction ? (
            <ResultsDisplay prediction={prediction} />
          ) : (
            // Placeholder when no prediction yet
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '2rem',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px dashed #e2e8f0',
              minHeight: '400px' // Fixed height to match PredictionPanel
            }}>
              <div style={{ textAlign: 'center', color: '#a0aec0' }}>
                <svg
                  style={{ width: '64px', height: '64px', margin: '0 auto 1rem' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                <h3 style={{
                  fontSize: '1.125rem',
                  fontWeight: '600',
                  marginBottom: '0.5rem',
                  color: '#718096'
                }}>
                  No Diagnosis Yet
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#a0aec0' }}>
                  Upload a signal file and click "Run Diagnosis" to see results
                </p>
              </div>
            </div>
          )}
        </div>

        {currentSignal && <FFTChart signal={currentSignal} />}

        {prediction && <FeatureTable features={prediction.features} />}

        <HistoryTable history={history} />
      </div>
    </div>
  );
}

export default App;