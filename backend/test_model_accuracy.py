import json
import numpy as np
import joblib
from scipy import stats
from scipy.signal import welch

# Load model
model = joblib.load('models/rf_model_real.pkl')

def extract_features(signal):
    """Extract features (same as in main.py)"""
    signal = np.array(signal)
    
    mean = np.mean(signal)
    std = np.std(signal)
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    peak_to_peak = np.ptp(signal)
    crest_factor = peak / rms if rms > 0 else 0
    skewness = stats.skew(signal)
    kurtosis = stats.kurtosis(signal)
    
    sqrt_abs_signal = np.sqrt(np.abs(signal))
    sqrt_abs_mean = np.mean(sqrt_abs_signal)
    clearance_factor = peak / (sqrt_abs_mean**2) if sqrt_abs_mean > 0 else 0
    
    abs_mean = np.mean(np.abs(signal))
    shape_factor = rms / abs_mean if abs_mean > 0 else 0
    impulse_factor = peak / abs_mean if abs_mean > 0 else 0
    
    freqs, psd = welch(signal, fs=12000, nperseg=min(1024, len(signal)))
    freq_mean = np.sum(freqs * psd) / np.sum(psd) if np.sum(psd) > 0 else 0
    freq_std = np.sqrt(np.sum(((freqs - freq_mean)**2) * psd) / np.sum(psd)) if np.sum(psd) > 0 else 0
    freq_peak = freqs[np.argmax(psd)]
    
    return np.array([mean, std, rms, peak, peak_to_peak, crest_factor, 
                     skewness, kurtosis, clearance_factor, shape_factor, 
                     impulse_factor, freq_mean, freq_std, freq_peak])

def test_dataset(json_file):
    """Test model on synthetic dataset"""
    
    print(f"\n{'='*70}")
    print(f"Testing: {json_file}")
    print(f"{'='*70}\n")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    results = {}
    total_correct = 0
    total_samples = 0
    
    for fault_type, signals in data['data'].items():
        correct = 0
        predictions = []
        confidences = []
        
        for signal in signals:
            features = extract_features(signal).reshape(1, -1)
            prediction = model.predict(features)[0]
            confidence = model.predict_proba(features)[0].max()
            
            predictions.append(prediction)
            confidences.append(confidence)
            
            if prediction == fault_type:
                correct += 1
        
        accuracy = (correct / len(signals)) * 100
        avg_confidence = np.mean(confidences)
        
        results[fault_type] = {
            'accuracy': accuracy,
            'correct': correct,
            'total': len(signals),
            'avg_confidence': avg_confidence
        }
        
        total_correct += correct
        total_samples += len(signals)
        
        print(f"📊 {fault_type.upper()}")
        print(f"   Accuracy: {accuracy:.2f}% ({correct}/{len(signals)})")
        print(f"   Avg Confidence: {avg_confidence:.3f}")
        print()
    
    overall_accuracy = (total_correct / total_samples) * 100
    
    print(f"{'='*70}")
    print(f"🎯 OVERALL ACCURACY: {overall_accuracy:.2f}% ({total_correct}/{total_samples})")
    print(f"{'='*70}\n")
    
    return results, overall_accuracy

# Test both datasets
high_noise_results, high_acc = test_dataset('synthetic_test_data/test_data_high_noise.json')
extreme_noise_results, extreme_acc = test_dataset('synthetic_test_data/test_data_extreme_noise.json')

print(f"\n{'='*70}")
print("📈 SUMMARY")
print(f"{'='*70}")
print(f"High Noise:    {high_acc:.2f}%")
print(f"Extreme Noise: {extreme_acc:.2f}%")
print(f"{'='*70}\n")
