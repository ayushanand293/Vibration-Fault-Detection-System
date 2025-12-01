import React from 'react';
import { Database } from 'lucide-react';

const FeatureTable = ({ features }) => {
  if (!features) return null;

  // Debug: Log features to see actual keys
  console.log('Features received:', features);

  const FeatureCard = ({ title, value, icon, color }) => (
    <div style={{
      background: 'white',
      borderRadius: '10px',
      padding: '1.25rem',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      border: `2px solid ${color}20`,
      transition: 'all 0.3s ease',
      cursor: 'default'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-3px)';
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.12)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '1.5rem' }}>{icon}</span>
        <span style={{ 
          fontSize: '0.875rem', 
          fontWeight: '600', 
          color: '#4a5568',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {title}
        </span>
      </div>
      <div style={{ 
        fontSize: '1.5rem', 
        fontWeight: '700', 
        color: color,
        fontFamily: 'monospace'
      }}>
        {typeof value === 'number' ? value.toFixed(4) : (value || 'N/A')}
      </div>
    </div>
  );

  // Dynamically get all features and group them
  const allFeatureKeys = Object.keys(features);
  
  // Time domain features (first 7)
  const timeDomainKeys = ['rms', 'peak', 'peak_to_peak', 'crest_factor', 'kurtosis', 'skewness', 'std'];
  const timeDomainFeatures = allFeatureKeys
    .filter(key => timeDomainKeys.includes(key))
    .map(key => ({
      key,
      label: key.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      value: features[key]
    }));

  // Frequency domain features (remaining)
  const frequencyDomainFeatures = allFeatureKeys
    .filter(key => !timeDomainKeys.includes(key))
    .map(key => ({
      key,
      label: key.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      value: features[key]
    }));

  const timeIcons = ['📈', '⬆️', '↕️', '🎯', '📊', '↗️', '📉'];
  const freqIcons = ['🎵', '📡', '📻', '🔊', '🎚️', '📶', '🌊'];

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '2rem',
      marginBottom: '2rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ 
          fontSize: '1.75rem', 
          fontWeight: 'bold', 
          color: '#2d3748',
          marginTop: 0,
          marginBottom: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <Database size={28} color="#667eea" />
          <span style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            Extracted Features
          </span>
        </h2>
        <p style={{ color: '#718096', fontSize: '0.95rem', margin: 0 }}>
          Advanced signal processing features used for fault classification
        </p>
      </div>

      {/* Time Domain Features */}
      {timeDomainFeatures.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '1.5rem',
            paddingBottom: '0.75rem',
            borderBottom: '2px solid #e2e8f0'
          }}>
            <span style={{ fontSize: '1.5rem' }}>⏱️</span>
            <h3 style={{ 
              fontSize: '1.25rem', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: 0
            }}>
              Time Domain Features
            </h3>
            <span style={{
              background: '#667eea20',
              color: '#667eea',
              padding: '0.25rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>
              {timeDomainFeatures.length} features
            </span>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem'
          }}>
            {timeDomainFeatures.map((feature, idx) => (
              <FeatureCard
                key={feature.key}
                title={feature.label}
                value={feature.value}
                icon={timeIcons[idx % timeIcons.length]}
                color="#667eea"
              />
            ))}
          </div>
        </div>
      )}

      {/* Frequency Domain Features */}
      {frequencyDomainFeatures.length > 0 && (
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '1.5rem',
            paddingBottom: '0.75rem',
            borderBottom: '2px solid #e2e8f0'
          }}>
            <span style={{ fontSize: '1.5rem' }}>🌊</span>
            <h3 style={{ 
              fontSize: '1.25rem', 
              fontWeight: '600', 
              color: '#2d3748',
              margin: 0
            }}>
              Frequency Domain Features
            </h3>
            <span style={{
              background: '#764ba220',
              color: '#764ba2',
              padding: '0.25rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>
              {frequencyDomainFeatures.length} features
            </span>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1rem'
          }}>
            {frequencyDomainFeatures.map((feature, idx) => (
              <FeatureCard
                key={feature.key}
                title={feature.label}
                value={feature.value}
                icon={freqIcons[idx % freqIcons.length]}
                color="#764ba2"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FeatureTable;