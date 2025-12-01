import joblib
import numpy as np
from scipy import stats
from scipy.signal import welch

def extract_features(signal):
    """Extract features exactly as training"""
    signal = np.array(signal)
    features = {}
    
    features['mean'] = float(np.mean(signal))
    features['std'] = float(np.std(signal))
    features['rms'] = float(np.sqrt(np.mean(signal**2)))
    features['peak'] = float(np.max(np.abs(signal)))
    features['peak_to_peak'] = float(np.ptp(signal))
    features['crest_factor'] = float(features['peak'] / features['rms']) if features['rms'] != 0 else 0
    features['skewness'] = float(stats.skew(signal))
    features['kurtosis'] = float(stats.kurtosis(signal))
    
    sqrt_abs_mean = np.mean(np.sqrt(np.abs(signal)))
    features['clearance_factor'] = float(features['peak'] / (sqrt_abs_mean**2)) if sqrt_abs_mean != 0 else 0
    
    mean_abs = np.mean(np.abs(signal))
    features['shape_factor'] = float(features['rms'] / mean_abs) if mean_abs != 0 else 0
    features['impulse_factor'] = float(features['peak'] / mean_abs) if mean_abs != 0 else 0
    
    freqs, psd = welch(signal, fs=12000, nperseg=1024)
    psd_sum = np.sum(psd)
    
    if psd_sum != 0:
        features['freq_mean'] = float(np.sum(freqs * psd) / psd_sum)
        features['freq_std'] = float(np.sqrt(np.sum(((freqs - features['freq_mean'])**2) * psd) / psd_sum))
    else:
        features['freq_mean'] = 0.0
        features['freq_std'] = 0.0
    
    features['freq_peak'] = float(freqs[np.argmax(psd)])
    
    return features

print("=" * 80)
print("🧪 TESTING rf_model_real.pkl WITHOUT SCALER")
print("=" * 80)

model = joblib.load('backend/models/rf_model_real.pkl')
print(f"✅ Model loaded")
print(f"   Classes: {model.classes_}")
print(f"   Features: {model.n_features_in_}")

# Test with different signals
t = np.linspace(0, 0.2, 2400)

signals = {
    'Normal': 1.0 * np.sin(2 * np.pi * 30 * t) + 0.15 * np.random.randn(len(t)),
    'Ball': 1.0 * np.sin(2 * np.pi * 30 * t) + 2.5 * np.sin(2 * np.pi * 157 * t) + 0.25 * np.random.randn(len(t)),
    'Inner': 1.0 * np.sin(2 * np.pi * 30 * t) + 2.2 * np.sin(2 * np.pi * 162 * t) + 0.25 * np.random.randn(len(t)),
    'Outer': 1.0 * np.sin(2 * np.pi * 30 * t) + 2.0 * np.sin(2 * np.pi * 107 * t) + 0.25 * np.random.randn(len(t))
}

feature_names = ['mean', 'std', 'rms', 'peak', 'peak_to_peak', 'crest_factor',
                'skewness', 'kurtosis', 'clearance_factor', 'shape_factor',
                'impulse_factor', 'freq_mean', 'freq_std', 'freq_peak']

for name, signal in signals.items():
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    
    features = extract_features(signal)
    X = np.array([[features[fn] for fn in feature_names]])
    
    # NO SCALING - Direct prediction
    prediction = model.predict(X)[0]
    probs = model.predict_proba(X)[0]
    
    print(f"🎯 Prediction: {prediction}")
    for label, prob in zip(model.classes_, probs):
        bar = '█' * int(prob * 30)
        print(f"   {label:15s}: {prob*100:5.1f}% {bar}")

print("\n" + "=" * 80)
