# backend/app/preprocessing.py
import numpy as np
from scipy import stats
from scipy.fft import fft, fftfreq
from typing import Dict, Tuple
from app.models import ExtractedFeatures

class SignalProcessor:
    """Extract features from vibration signals"""
    
    @staticmethod
    def extract_time_features(signal: np.ndarray) -> Dict[str, float]:
        """Extract time-domain features"""
        
        # Basic statistics
        rms = np.sqrt(np.mean(signal**2))
        peak = np.max(np.abs(signal))
        std_dev = np.std(signal)
        peak_to_peak = np.ptp(signal)
        
        # Shape features
        crest_factor = peak / rms if rms > 0 else 0
        kurtosis = stats.kurtosis(signal)
        skewness = stats.skew(signal)
        
        return {
            'rms': float(rms),
            'peak': float(peak),
            'crest_factor': float(crest_factor),
            'kurtosis': float(kurtosis),
            'skewness': float(skewness),
            'std_dev': float(std_dev),
            'peak_to_peak': float(peak_to_peak)
        }
    
    @staticmethod
    def extract_frequency_features(signal: np.ndarray, sampling_rate: int) -> Dict[str, float]:
        """Extract frequency-domain features using FFT"""
        
        # Compute FFT
        n = len(signal)
        fft_vals = fft(signal)
        fft_freq = fftfreq(n, 1/sampling_rate)
        
        # Consider only positive frequencies
        positive_freq_idx = fft_freq > 0
        fft_freq = fft_freq[positive_freq_idx]
        fft_magnitude = np.abs(fft_vals[positive_freq_idx])
        
        # Dominant frequency
        dominant_idx = np.argmax(fft_magnitude)
        dominant_frequency = fft_freq[dominant_idx]
        peak_fft_magnitude = fft_magnitude[dominant_idx]
        
        # Top 3 frequencies
        top_indices = np.argsort(fft_magnitude)[-3:][::-1]
        top_freq_1 = fft_freq[top_indices[0]] if len(top_indices) > 0 else 0
        top_freq_2 = fft_freq[top_indices[1]] if len(top_indices) > 1 else 0
        top_freq_3 = fft_freq[top_indices[2]] if len(top_indices) > 2 else 0
        
        # Spectral entropy
        psd = fft_magnitude**2
        psd_norm = psd / np.sum(psd)
        spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm + 1e-12))
        
        # Frequency centroid
        frequency_centroid = np.sum(fft_freq * fft_magnitude) / np.sum(fft_magnitude)
        
        return {
            'dominant_frequency': float(dominant_frequency),
            'peak_fft_magnitude': float(peak_fft_magnitude),
            'top_freq_1': float(top_freq_1),
            'top_freq_2': float(top_freq_2),
            'top_freq_3': float(top_freq_3),
            'spectral_entropy': float(spectral_entropy),
            'frequency_centroid': float(frequency_centroid)
        }
    
    @classmethod
    def extract_all_features(cls, signal: np.ndarray, sampling_rate: int) -> ExtractedFeatures:
        """Extract all features and return as Pydantic model"""
        
        # Extract features
        time_features = cls.extract_time_features(signal)
        freq_features = cls.extract_frequency_features(signal, sampling_rate)
        
        # Combine all features
        all_features = {**time_features, **freq_features}
        
        return ExtractedFeatures(**all_features)
    
    @staticmethod
    def generate_synthetic_signal(fault_type: str, duration: float = 1.0, 
                                  sampling_rate: int = 12000) -> np.ndarray:
        """Generate synthetic vibration signal for given fault type"""
        
        t = np.linspace(0, duration, int(sampling_rate * duration))
        
        # Base signal parameters
        fault_frequencies = {
            'normal': 30,
            'inner_race': 297,
            'outer_race': 250,
            'ball': 400
        }
        
        base_freq = fault_frequencies.get(fault_type, 30)
        
        # Generate signal
        signal = (
            np.sin(2 * np.pi * base_freq * t) +
            0.3 * np.sin(2 * np.pi * base_freq * 2 * t) +
            0.1 * np.random.randn(len(t))  # Add noise
        )
        
        return signal
