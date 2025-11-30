# backend/app/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class VibrationData(BaseModel):
    """Input schema for vibration data"""
    signal: List[float] = Field(..., description="Raw vibration signal data points")
    sampling_rate: int = Field(12000, description="Sampling frequency in Hz")
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal": [0.5, 0.8, 0.3, -0.2, -0.6, 0.1],
                "sampling_rate": 12000
            }
        }

class ExtractedFeatures(BaseModel):
    """Extracted features from vibration signal"""
    # Time-domain features
    rms: float
    peak: float
    crest_factor: float
    kurtosis: float
    skewness: float
    std_dev: float
    peak_to_peak: float
    
    # Frequency-domain features
    dominant_frequency: float
    peak_fft_magnitude: float
    top_freq_1: float
    top_freq_2: float
    top_freq_3: float
    spectral_entropy: float
    frequency_centroid: float

class PredictionResponse(BaseModel):
    """Output schema for prediction"""
    prediction: str = Field(..., description="Predicted fault type")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    probabilities: Dict[str, float] = Field(..., description="Class probabilities")
    features: ExtractedFeatures = Field(..., description="Extracted features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "outer_race",
                "confidence": 0.98,
                "probabilities": {
                    "normal": 0.01,
                    "inner_race": 0.01,
                    "outer_race": 0.98,
                    "ball": 0.00
                },
                "features": {
                    "rms": 1.05,
                    "peak": 2.3,
                    "dominant_frequency": 250.0
                }
            }
        }

class StreamDataPoint(BaseModel):
    """Single data point for streaming"""
    timestamp: float
    amplitude: float
    
class HealthStatus(BaseModel):
    """System health status"""
    status: str
    model_loaded: bool
    scaler_loaded: bool
    version: str