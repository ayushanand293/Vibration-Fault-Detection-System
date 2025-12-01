import numpy as np
import joblib
from scipy.io import loadmat
from scipy import stats
from scipy.signal import welch

def extract_features(signal):
    """Extract features"""
    signal = np.array(signal)
    
    mean = np.mean(signal)
    std = np.std(signal)
    rms = np.sqrt(np.mean(signal**2))
    peak = np.max(np.abs(signal))
    peak_to_peak = np.ptp(signal)
    crest_factor = peak / rms if rms > 0 else 0
    skewness = stats.skew(signal)
    kurtosis = stats.kurtosis(signal)
    
    sqrt_abs_mean = np.mean(np.sqrt(np.abs(signal)))
    clearance_factor = peak / (sqrt_abs_mean**2) if sqrt_abs_mean > 0 else 0
    
    abs_mean = np.mean(np.abs(signal))
    shape_factor = rms / abs_mean if abs_mean > 0 else 0
    impulse_factor = peak / abs_mean if abs_mean > 0 else 0
    
    freqs, psd = welch(signal, fs=12000, nperseg=1024)
    freq_mean = np.sum(freqs * psd) / np.sum(psd)
    freq_std = np.sqrt(np.sum(((freqs - freq_mean)**2) * psd) / np.sum(psd))
    freq_peak = freqs[np.argmax(psd)]
    
    return np.array([mean, std, rms, peak, peak_to_peak, crest_factor, 
                     skewness, kurtosis, clearance_factor, shape_factor, 
                     impulse_factor, freq_mean, freq_std, freq_peak])

# Load model
model = joblib.load('backend/models/rf_model_real.pkl')

print("="*60)
print("TESTING MODEL ON DIFFERENT SEGMENTS")
print("="*60)

# Test on segments from DIFFERENT parts of the data files
test_cases = [
    ('data/cwru_dataset/normal_0.mat', 'normal', 50000),  # Different position
    ('data/cwru_dataset/ball_007_0.mat', 'ball', 50000),
    ('data/cwru_dataset/inner_007_0.mat', 'inner_race', 50000),
    ('data/cwru_dataset/outer_007_0.mat', 'outer_race', 50000),
]

for file_path, true_label, start_idx in test_cases:
    mat_data = loadmat(file_path)
    de_keys = [key for key in mat_data.keys() if 'DE_time' in key]
    
    if de_keys:
        full_signal = mat_data[de_keys[0]].flatten()
        
        # Extract segment from different position
        segment = full_signal[start_idx:start_idx+2400]
        
        # Extract features and predict
        features = extract_features(segment)
        features = features.reshape(1, -1)
        
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        prob_dict = dict(zip(model.classes_, probabilities))
        
        print(f"\n{true_label.upper()}:")
        print(f"  Predicted: {prediction}")
        print(f"  Confidence: {max(probabilities)*100:.2f}%")
        print(f"  All probabilities:")
        for cls, prob in prob_dict.items():
            marker = "✓" if cls == true_label else " "
            print(f"    {marker} {cls:12s}: {prob*100:5.2f}%")
        
        correct = "✅ CORRECT" if prediction == true_label else "❌ WRONG"
        print(f"  {correct}")

print("\n" + "="*60)
print("TESTING ON RANDOM SEGMENTS (Multiple Positions)")
print("="*60)

# Test multiple random segments from each file
file_path = 'data/cwru_dataset/ball_007_0.mat'
mat_data = loadmat(file_path)
de_keys = [key for key in mat_data.keys() if 'DE_time' in key]
full_signal = mat_data[de_keys[0]].flatten()

print(f"\nBall Fault - Testing 5 different segments:")
for i, start_idx in enumerate([5000, 15000, 25000, 35000, 45000]):
    segment = full_signal[start_idx:start_idx+2400]
    features = extract_features(segment).reshape(1, -1)
    prediction = model.predict(features)[0]
    confidence = max(model.predict_proba(features)[0])
    
    print(f"  Segment {i+1} (pos {start_idx}): {prediction} ({confidence*100:.1f}%)")
