import os
import sys
import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import kurtosis
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

os.makedirs('data', exist_ok=True)
os.makedirs('../reports', exist_ok=True)

print("="*60)
print("CWRU PROCESSING STARTED")
print("="*60)

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

def preprocess(raw, fs):
    detrended = signal.detrend(raw, type='linear')
    ma = np.convolve(detrended, np.ones(5)/5, mode='same')
    b, a = signal.butter(4, 5000/(fs/2), btype='low')
    filtered = signal.filtfilt(b, a, ma)
    window = signal.windows.hann(len(filtered))
    windowed = filtered * window
    normalized = (windowed - np.mean(windowed)) / (np.std(windowed) + 1e-10)
    return normalized, {'raw': raw, 'detrended': detrended, 'ma_filtered': ma, 
                        'lp_filtered': filtered, 'windowed': windowed, 'normalized': normalized}

def compute_fft(sig, fs):
    n = len(sig)
    freqs = np.fft.fftfreq(n, d=1/fs)[:n//2]
    fft_vals = np.abs(np.fft.fft(sig)[:n//2])
    fft_vals = fft_vals / (np.max(fft_vals) + 1e-10)
    freqs_psd, psd = signal.welch(sig, fs=fs, nperseg=1024)
    return freqs, fft_vals, freqs_psd, psd

def extract_features(sig, freqs, fft_vals, freqs_psd, psd):
    f = {}
    f['rms'] = np.sqrt(np.mean(sig**2))
    f['peak'] = np.max(np.abs(sig))
    f['crest_factor'] = f['peak'] / (f['rms'] + 1e-10)
    f['kurtosis'] = kurtosis(sig)
    f['skewness'] = pd.Series(sig).skew()
    f['std_dev'] = np.std(sig)
    f['dominant_frequency'] = freqs[np.argmax(fft_vals)]
    f['peak_fft_magnitude'] = np.max(fft_vals)
    top3 = np.argsort(fft_vals)[-3:][::-1]
    f['top_freq_1'] = freqs[top3[0]]
    f['top_freq_2'] = freqs[top3[1]]
    f['top_freq_3'] = freqs[top3[2]]
    norm_psd = psd / (np.sum(psd) + 1e-10)
    f['spectral_entropy'] = -np.sum(norm_psd * np.log2(norm_psd + 1e-10))
    f['frequency_centroid'] = np.sum(freqs_psd * psd) / (np.sum(psd) + 1e-10)
    return f

fault_types = ['normal', 'inner_race', 'outer_race', 'ball']
all_features = []
stages_dict = {}

for ft in fault_types:
    print(f"Processing {ft}...")
    t, raw, fs = generate_signal(ft)
    proc, stages = preprocess(raw, fs)
    stages_dict[ft] = stages
    freqs, fft_vals, freqs_psd, psd = compute_fft(proc, fs)
    features = extract_features(proc, freqs, fft_vals, freqs_psd, psd)
    features['fault_type'] = ft
    all_features.append(features)

df = pd.DataFrame(all_features)
df.to_csv('data/cwru_features.csv', index=False)
print("✓ Saved: data/cwru_features.csv")

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
fig.suptitle('Preprocessing Pipeline', fontsize=16, fontweight='bold')
stages = stages_dict['normal']
names = ['Raw', 'Detrended', 'MA Filtered', 'LP Filtered', 'Windowed', 'Normalized']
keys = ['raw', 'detrended', 'ma_filtered', 'lp_filtered', 'windowed', 'normalized']
for idx, (name, key) in enumerate(zip(names, keys)):
    ax = axes[idx // 3, idx % 3]
    ax.plot(stages[key][:5000], linewidth=0.8)
    ax.set_title(name, fontweight='bold')
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../reports/01_preprocessing_pipeline.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/01_preprocessing_pipeline.png")
plt.close()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('FFT Analysis', fontsize=16, fontweight='bold')
for idx, ft in enumerate(fault_types):
    ax = axes[idx // 2, idx % 2]
    proc = stages_dict[ft]['normalized']
    freqs, fft_vals, _, _ = compute_fft(proc, 12000)
    ax.semilogy(freqs[:2000], fft_vals[:2000], linewidth=0.8)
    ax.set_title(ft.upper(), fontweight='bold')
    ax.set_xlabel('Frequency (Hz)')
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../reports/02_fft_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/02_fft_comparison.png")
plt.close()

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Feature Distributions', fontsize=16, fontweight='bold')
features_plot = ['rms', 'kurtosis', 'crest_factor', 'dominant_frequency']
for idx, feat in enumerate(features_plot):
    ax = axes[idx // 2, idx % 2]
    for ft in fault_types:
        val = df[df['fault_type'] == ft][feat].values[0]
        ax.bar(ft, val, alpha=0.7)
    ax.set_title(feat.upper(), fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
plt.tight_layout()
plt.savefig('../reports/03_feature_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: reports/03_feature_comparison.png")
plt.close()

print("\n" + "="*60)
print("✅ PART A COMPLETE")
print("="*60)
print(df.to_string())
