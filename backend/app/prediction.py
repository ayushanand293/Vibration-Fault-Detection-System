# backend/app/prediction.py
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
from app.models import ExtractedFeatures

class FaultPredictor:
    """Load model and make predictions"""
    
    def __init__(self, model_path: str = "ml_models/random_forest_model.pkl",
                 scaler_path: str = "ml_models/scaler.pkl"):
        """Initialize predictor with model and scaler"""
        
        self.model = None
        self.scaler = None
        self.class_names = ['ball', 'inner_race', 'normal', 'outer_race']
        
        # CORRECT Feature order from debug output
        self.feature_order = [
            'rms',
            'peak',
            'peak_to_peak',        # ← MOVED UP
            'crest_factor',        # ← MOVED DOWN
            'kurtosis',
            'skewness',
            'std_dev',
            'dominant_frequency',
            'peak_fft_magnitude',
            'top_freq_1',
            'top_freq_2',
            'top_freq_3',
            'spectral_entropy',
            'frequency_centroid'
        ]
        
        # Load model
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Model loaded from {model_path}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
        
        # Load scaler
        try:
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"✅ Scaler loaded from {scaler_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load scaler: {e}")
    
    def features_to_dataframe(self, features: ExtractedFeatures) -> pd.DataFrame:
        """Convert ExtractedFeatures to DataFrame with CORRECT ORDER"""
        
        # Create dictionary with all features
        feature_dict = {
            'rms': features.rms,
            'peak': features.peak,
            'peak_to_peak': features.peak_to_peak,
            'crest_factor': features.crest_factor,
            'kurtosis': features.kurtosis,
            'skewness': features.skewness,
            'std_dev': features.std_dev,
            'dominant_frequency': features.dominant_frequency,
            'peak_fft_magnitude': features.peak_fft_magnitude,
            'top_freq_1': features.top_freq_1,
            'top_freq_2': features.top_freq_2,
            'top_freq_3': features.top_freq_3,
            'spectral_entropy': features.spectral_entropy,
            'frequency_centroid': features.frequency_centroid
        }
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([feature_dict])
        
        # Reorder columns to match training
        df = df[self.feature_order]
        
        return df
    
    def predict(self, features: ExtractedFeatures) -> Tuple[str, float, Dict[str, float]]:
        """Make prediction from features"""
        
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Convert features to DataFrame with correct order
        X = self.features_to_dataframe(features)
        
        # Scale features if scaler available
        if self.scaler is not None:
            try:
                X_scaled = self.scaler.transform(X)
                X = pd.DataFrame(X_scaled, columns=X.columns)
            except Exception as e:
                print(f"⚠️  Scaling skipped: {e}")
        
        # Get prediction
        prediction_idx = self.model.predict(X)[0]
        prediction = self.class_names[prediction_idx]
        
        # Get probabilities
        probabilities = self.model.predict_proba(X)[0]
        confidence = float(np.max(probabilities))
        
        # Create probability dictionary
        prob_dict = {
            class_name: float(prob) 
            for class_name, prob in zip(self.class_names, probabilities)
        }
        
        return prediction, confidence, prob_dict
    
    def is_healthy(self) -> bool:
        """Check if predictor is ready"""
        return self.model is not None