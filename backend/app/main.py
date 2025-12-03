
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import numpy as np
import joblib
from scipy import stats
from scipy.signal import welch
from scipy.io import loadmat
import io
import time
import asyncio
import os
from datetime import datetime

# Import the report generator
from app.report_generator import ReportGenerator

app = FastAPI(title="Vibration Fault Detection API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
model = joblib.load('models/rf_model_real.pkl')

# Initialize report generator
report_gen = ReportGenerator()

class SignalData(BaseModel):
    signal: List[float]
    sampling_rate: int = 12000

def extract_features(signal):
    """Extract features in EXACT same order as training"""
    signal = np.array(signal)
    
    if len(signal) < 100:
        raise ValueError("Signal too short")
    
    # Time domain features
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
    
    # Frequency domain features
    freqs, psd = welch(signal, fs=12000, nperseg=min(1024, len(signal)))
    freq_mean = np.sum(freqs * psd) / np.sum(psd) if np.sum(psd) > 0 else 0
    freq_std = np.sqrt(np.sum(((freqs - freq_mean)**2) * psd) / np.sum(psd)) if np.sum(psd) > 0 else 0
    freq_peak = freqs[np.argmax(psd)]
    
    features_dict = {
        'mean': float(mean),
        'std': float(std),
        'rms': float(rms),
        'peak': float(peak),
        'peak_to_peak': float(peak_to_peak),
        'crest_factor': float(crest_factor),
        'skewness': float(skewness),
        'kurtosis': float(kurtosis),
        'clearance_factor': float(clearance_factor),
        'shape_factor': float(shape_factor),
        'impulse_factor': float(impulse_factor),
        'freq_mean': float(freq_mean),
        'freq_std': float(freq_std),
        'freq_peak': float(freq_peak)
    }
    
    return features_dict

def load_real_signal_segment(fault_type: str):
    """Load a real segment from CWRU dataset"""
    data_dir = '../data/cwru_dataset'
    
    file_mapping = {
        'normal': 'normal_0.mat',
        'fault/ball': 'ball_007_0.mat',
        'fault/inner_race': 'inner_007_0.mat',
        'fault/outer_race': 'outer_007_0.mat'
    }
    
    if fault_type not in file_mapping:
        return None
    
    file_path = os.path.join(data_dir, file_mapping[fault_type])
    
    if not os.path.exists(file_path):
        return None
    
    try:
        mat_data = loadmat(file_path)
        de_keys = [key for key in mat_data.keys() if 'DE_time' in key]
        
        if de_keys:
            full_signal = mat_data[de_keys[0]].flatten()
            start_idx = 10000
            segment = full_signal[start_idx:start_idx+2400]
            return segment.tolist()
    
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None
    
    return None

@app.get("/")
def root():
    return {
        "message": "Vibration Fault Detection API - Real CWRU Model", 
        "status": "active",
        "model_classes": model.classes_.tolist()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "model": "Random Forest (Real CWRU Data)", 
        "version": "2.1",
        "features_expected": model.n_features_in_
    }

@app.post("/predict")
def predict_fault(data: SignalData):
    try:
        if len(data.signal) < 100:
            raise HTTPException(status_code=400, detail="Signal too short (minimum 100 samples)")
        
        # Extract features
        features_dict = extract_features(data.signal)
        feature_array = np.array(list(features_dict.values())).reshape(1, -1)
        
        # Predict
        prediction = model.predict(feature_array)[0]
        probabilities = model.predict_proba(feature_array)[0]
        
        # Map to class names
        class_names = model.classes_
        prob_dict = {name: float(prob) for name, prob in zip(class_names, probabilities)}
        
        return {
            "prediction": prediction,
            "confidence": float(max(probabilities)),
            "probabilities": prob_dict,
            "features": features_dict,
            "signal": data.signal  # Add the signal to the response
        }
    
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/example/{fault_type:path}")
def get_example_signal(fault_type: str):
    """Load REAL example from CWRU dataset"""
    signal = load_real_signal_segment(fault_type)
    
    if signal is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Could not load real data for {fault_type}. Check CWRU dataset files."
        )
    
    return {"signal": signal, "type": fault_type}

@app.post("/diagnostic-report")
async def generate_diagnostic_report(data: SignalData):
    """
    Generate comprehensive PDF diagnostic report
    Accepts signal data and returns PDF file
    """
    try:
        # Validate input
        if len(data.signal) < 100:
            raise HTTPException(
                status_code=400, 
                detail="Signal too short (minimum 100 samples required)"
            )
        
        # Convert to numpy array
        signal = np.array(data.signal)
        
        # Extract features
        features_dict = extract_features(signal)
        feature_array = np.array(list(features_dict.values())).reshape(1, -1)
        
        # Get prediction from model
        prediction = model.predict(feature_array)[0]
        probabilities = model.predict_proba(feature_array)[0]
        confidence = float(max(probabilities))
        
        # Create probabilities dictionary
        prob_dict = {
            name: float(prob) 
            for name, prob in zip(model.classes_, probabilities)
        }
        
        print(f"Generating report for prediction: {prediction} (confidence: {confidence:.2%})")
        
        # Generate PDF report
        pdf_bytes = report_gen.generate_pdf(
            signal=signal,
            sampling_rate=data.sampling_rate,
            features=features_dict,
            prediction=prediction,
            confidence=confidence,
            probabilities=prob_dict
        )
        
        # Create file buffer
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bearing_diagnostic_report_{timestamp}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/pdf"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Report generation error:\n{error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate report: {str(e)}"
        )

@app.get("/stream-signal")
async def stream_signal(mode: str = 'real'):
    """
    Stream simulated real-time vibration data with predictions
    mode: 'real' (CWRU data) or 'random' (generated noise)
    """
    async def generate():
        import json
        import random
        
        # Load real segments for simulation
        scenarios = ['normal', 'fault/ball', 'fault/inner_race', 'fault/outer_race']
        
        while True:
            if mode == 'real':
                # Pick a random scenario
                scenario = random.choice(scenarios)
                signal_segment = load_real_signal_segment(scenario)
                
                if signal_segment is None:
                    continue
                    
                # Stream this segment point by point
                buffer = []
                for val in signal_segment[:500]: # Stream 500 points per scenario switch
                    data_point = {
                        "timestamp": time.time(),
                        "amplitude": float(val)
                    }
                    yield f"data: {json.dumps(data_point)}\n\n"
                    
                    # Add to buffer for prediction
                    buffer.append(val)
                    if len(buffer) >= 100:
                        # Run prediction on buffer
                        try:
                            features = extract_features(buffer[-100:]) # Last 100 points
                            feature_array = np.array(list(features.values())).reshape(1, -1)
                            prediction = model.predict(feature_array)[0]
                            confidence = float(max(model.predict_proba(feature_array)[0]))
                            
                            # Map to class names
                            class_names = model.classes_
                            prob_dict = {name: float(prob) for name, prob in zip(class_names, model.predict_proba(feature_array)[0])}
                            
                            pred_event = {
                                "type": "prediction",
                                "prediction": prediction,
                                "confidence": confidence,
                                "probabilities": prob_dict,
                                "features": features,
                                "scenario": scenario # For debugging/verification
                            }
                            yield f"event: prediction\ndata: {json.dumps(pred_event)}\n\n"
                        except Exception as e:
                            print(f"Stream prediction error: {e}")
                    
                    await asyncio.sleep(0.05) # 20Hz streaming rate for visualization
            
            else: # Random mode
                # Generate random noise/sine waves
                buffer = []
                # Simulate a "scenario" for random mode too (e.g. just noise vs high amplitude noise)
                is_noisy = random.random() > 0.5
                scenario = "simulated_noise" if not is_noisy else "simulated_fault"
                
                for i in range(200): # Stream 200 points
                    t = time.time()
                    if is_noisy:
                        val = np.sin(t * 10) * 0.5 + np.random.normal(0, 0.2)
                    else:
                        val = np.random.normal(0, 0.05)
                        
                    data_point = {
                        "timestamp": t,
                        "amplitude": float(val)
                    }
                    yield f"data: {json.dumps(data_point)}\n\n"
                    
                    buffer.append(val)
                    if len(buffer) >= 100:
                        try:
                            features = extract_features(buffer[-100:])
                            feature_array = np.array(list(features.values())).reshape(1, -1)
                            prediction = model.predict(feature_array)[0]
                            confidence = float(max(model.predict_proba(feature_array)[0]))
                            
                            class_names = model.classes_
                            prob_dict = {name: float(prob) for name, prob in zip(class_names, model.predict_proba(feature_array)[0])}
                            
                            pred_event = {
                                "type": "prediction",
                                "prediction": prediction,
                                "confidence": confidence,
                                "probabilities": prob_dict,
                                "features": features,
                                "scenario": scenario
                            }
                            yield f"event: prediction\ndata: {json.dumps(pred_event)}\n\n"
                        except Exception as e:
                            pass
                            
                    await asyncio.sleep(0.05)

    return StreamingResponse(generate(), media_type="text/event-stream")

