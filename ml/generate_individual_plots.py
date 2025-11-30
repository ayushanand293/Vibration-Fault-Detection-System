import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_palette("husl")

def generate_signal(fault_type, duration=2, fs=12000):
    t = np.linspace(0, duration, fs * duration, endpoint=False)
    if fault_type == 'normal':
        s = 0.3 * np.sin(2 * np.pi * 30 * t) + np.random.normal(0, 0.02, len(t))
    elif fault_type == 'inner_race':
        s = 0.5 * np.sin(2 * np.pi * 297 * t) + np.random.normal(0, 0.05, len(t))
    elif fault_type == 'outer_race':
        s = 0.6 * np.sin(2 * np.pi * 250 * t) + np.random.normal(0, 0.03, len(t))
    else:
        s = 0.4 * np.sin(2 * np.pi * 400 * t) + np.random.normal(0, 0.04, len(t))
    return t, s, fs

print("="*60)
print("GENERATING INDIVIDUAL ANALYSIS PLOTS")
print("="*60)

fault_types = ['normal', 'inner_race', 'outer_race', 'ball']

for fault_type in fault_types:
    print(f"\nProcessing {fault_type}...")
    t, raw_signal, fs = generate_signal(fault_type)
    
    # FFT
    n = len(raw_signal)
    freqs = np.fft.fftfreq(n, d=1/fs)[:n//2]
    fft_vals = np.abs(np.fft.fft(raw_signal)[:n//2])
    
    # PSD
    freqs_psd, psd = signal.welch(raw_signal, fs=fs, nperseg=1024)
    
    # 3-panel plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle(f'{fault_type.upper()} - Complete Signal Analysis', fontsize=16, fontweight='bold')
    
    # Raw Signal
    axes[0].plot(t[:5000], raw_signal[:5000], linewidth=0.8, color='steelblue')
    axes[0].set_title('Raw Vibration Signal', fontweight='bold', fontsize=12)
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude')
    axes[0].grid(True, alpha=0.3)
    
    # FFT
    axes[1].plot(freqs[:2000], fft_vals[:2000], linewidth=0.8, color='coral')
    axes[1].set_title('FFT (Frequency Spectrum)', fontweight='bold', fontsize=12)
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('Magnitude')
    axes[1].grid(True, alpha=0.3)
    axes[1].axvline(freqs[np.argmax(fft_vals[:2000])], color='red', linestyle='--', 
                    label=f'Peak: {freqs[np.argmax(fft_vals[:2000])]:.1f} Hz', alpha=0.7)
    axes[1].legend()
    
    # PSD
    axes[2].semilogy(freqs_psd, psd, linewidth=0.8, color='green')
    axes[2].set_title('PSD (Power Spectral Density)', fontweight='bold', fontsize=12)
    axes[2].set_xlabel('Frequency (Hz)')
    axes[2].set_ylabel('Power/Frequency (dB/Hz)')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'../reports/04_{fault_type}_analysis.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: reports/04_{fault_type}_analysis.png")
    plt.close()

# Feature summary
df = pd.read_csv('data/cwru_features.csv')
summary = df.describe().T
summary.to_csv('data/feature_summary.csv')
print("\n✓ Saved: data/feature_summary.csv")

print("\n" + "="*60)
print("✅ ALL INDIVIDUAL PLOTS GENERATED")
print("="*60)
print("\n📊 Complete Part A Deliverables:")
print("  ✓ data/cwru_features.csv")
print("  ✓ data/feature_summary.csv")
print("  ✓ reports/01_preprocessing_pipeline.png")
print("  ✓ reports/02_fft_comparison.png")
print("  ✓ reports/03_feature_comparison.png")
print("  ✓ reports/04_normal_analysis.png")
print("  ✓ reports/04_inner_race_analysis.png")
print("  ✓ reports/04_outer_race_analysis.png")
print("  ✓ reports/04_ball_analysis.png")
print("="*60)
