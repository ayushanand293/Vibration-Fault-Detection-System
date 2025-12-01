import numpy as np
import pandas as pd
from scipy.io import loadmat
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
from scipy import stats
from scipy.signal import welch

def extract_features(signal):
    """Extract time and frequency domain features"""
    features = {}
    
    # Time domain features
    features['mean'] = np.mean(signal)
    features['std'] = np.std(signal)
    features['rms'] = np.sqrt(np.mean(signal**2))
    features['peak'] = np.max(np.abs(signal))
    features['peak_to_peak'] = np.ptp(signal)
    features['crest_factor'] = features['peak'] / features['rms'] if features['rms'] != 0 else 0
    features['skewness'] = stats.skew(signal)
    features['kurtosis'] = stats.kurtosis(signal)
    features['clearance_factor'] = features['peak'] / (np.mean(np.sqrt(np.abs(signal)))**2) if np.mean(np.sqrt(np.abs(signal))) != 0 else 0
    features['shape_factor'] = features['rms'] / np.mean(np.abs(signal)) if np.mean(np.abs(signal)) != 0 else 0
    features['impulse_factor'] = features['peak'] / np.mean(np.abs(signal)) if np.mean(np.abs(signal)) != 0 else 0
    
    # Frequency domain features
    freqs, psd = welch(signal, fs=12000, nperseg=1024)
    features['freq_mean'] = np.sum(freqs * psd) / np.sum(psd)
    features['freq_std'] = np.sqrt(np.sum(((freqs - features['freq_mean'])**2) * psd) / np.sum(psd))
    features['freq_peak'] = freqs[np.argmax(psd)]
    
    return features

def load_cwru_data(file_path):
    """Load CWRU .mat file and extract drive end bearing data"""
    mat_data = loadmat(file_path)
    
    # CWRU data structure - find the drive end bearing data key
    # Keys typically end with '_DE_time'
    de_keys = [key for key in mat_data.keys() if 'DE_time' in key]
    
    if de_keys:
        signal = mat_data[de_keys[0]].flatten()
        return signal
    else:
        raise ValueError(f"No drive end data found in {file_path}")

def segment_signal(signal, segment_length=2400, overlap=0.5):
    """Split signal into overlapping segments"""
    step = int(segment_length * (1 - overlap))
    segments = []
    
    for i in range(0, len(signal) - segment_length + 1, step):
        segments.append(signal[i:i + segment_length])
    
    return segments

def prepare_dataset():
    """Load and prepare CWRU dataset"""
    data_dir = 'data/cwru_dataset'
    
    X = []
    y = []
    
    file_mapping = {
        'normal_0.mat': 'normal',
        'ball_007_0.mat': 'ball',
        'inner_007_0.mat': 'inner_race',
        'outer_007_0.mat': 'outer_race'
    }
    
    print("Loading CWRU dataset...")
    
    for filename, label in file_mapping.items():
        file_path = os.path.join(data_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"⚠️  {filename} not found, skipping...")
            continue
        
        print(f"Processing {filename} ({label})...")
        
        # Load signal
        signal = load_cwru_data(file_path)
        
        # Segment signal
        segments = segment_signal(signal, segment_length=2400)
        
        print(f"  Created {len(segments)} segments")
        
        # Extract features from each segment
        for segment in segments:
            features = extract_features(segment)
            X.append(list(features.values()))
            y.append(label)
    
    print(f"\n✅ Dataset prepared: {len(X)} samples, {len(set(y))} classes")
    return np.array(X), np.array(y), list(features.keys())

def train_model():
    """Train Random Forest on real CWRU data"""
    print("=" * 60)
    print("TRAINING WITH REAL CWRU BEARING DATASET")
    print("=" * 60)
    
    # Prepare dataset
    X, y, feature_names = prepare_dataset()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Features: {len(feature_names)}")
    
    # Train Random Forest
    print("\nTraining Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    
    # Training accuracy
    train_score = rf_model.score(X_train, y_train)
    print(f"\nTraining Accuracy: {train_score:.4f}")
    
    # Test accuracy
    test_score = rf_model.score(X_test, y_test)
    print(f"Test Accuracy: {test_score:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
    print(f"Cross-validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Predictions
    y_pred = rf_model.predict(X_test)
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Important Features:")
    print(feature_importance.head(10))
    
    # Save model
    model_path = 'backend/models/rf_model_real.pkl'
    joblib.dump(rf_model, model_path)
    print(f"\n✅ Model saved to {model_path}")
    
    return rf_model, feature_names

if __name__ == "__main__":
    train_model()
