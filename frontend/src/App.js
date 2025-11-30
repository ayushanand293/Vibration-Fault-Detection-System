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

  const handlePrediction = (result) => {
    setPrediction(result);
    
    const historyEntry = {
      timestamp: new Date().toISOString(),
      prediction: result.prediction,
      confidence: result.confidence,
      sampleCount: currentSignal ? currentSignal.length : 0
    };
    
    setHistory(prev => [historyEntry, ...prev].slice(0, 10));
  };

  const handleSignalLoaded = (signalArray) => {
    setCurrentSignal(signalArray);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Navbar />
      
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
        <StreamingChart />
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
          <div>
            <PredictionPanel 
              onPrediction={handlePrediction}
              onSignalLoaded={handleSignalLoaded}
            />
          </div>
          <div>
            {prediction && <ResultsDisplay prediction={prediction} />}
          </div>
        </div>
        
        {currentSignal && <FFTChart signal={currentSignal} />}
        
        {prediction && <FeatureTable features={prediction.features} />}
        
        <HistoryTable history={history} />
      </div>
    </div>
  );
}

export default App;
