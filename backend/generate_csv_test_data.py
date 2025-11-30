"""
CSV Generator - 1 file per noise level per fault type
Generates: low, medium, high noise for each fault (12 files total)
"""

import numpy as np
import csv
import os
from datetime import datetime

class SimpleCSVGenerator:
    """Generate CSV files with vibration data for testing"""
    
    def __init__(self, sampling_rate=12000, duration=0.2):
        self.fs = sampling_rate
        self.duration = duration
        self.n_samples = int(sampling_rate * duration)
        self.time = np.linspace(0, duration, self.n_samples)
        
        # Bearing frequencies
        self.f_rot = 30  # 1800 RPM
        self.f_bpfo = 107.4  # Outer race
        self.f_bpfi = 162.2  # Inner race
        self.f_bsf = 141.2   # Ball spin
    
    def add_noise(self, signal, snr_db):
        """Add noise to signal based on SNR"""
        signal_power = np.mean(signal ** 2)
        if signal_power == 0:
            signal_power = 1e-10
        
        noise_power_db = 10 * np.log10(signal_power) - snr_db
        noise_power = 10 ** (noise_power_db / 10)
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        
        return signal + noise
    
    def generate_normal(self, noise_level='low'):
        """Generate normal bearing signal"""
        signal = (0.1 * np.sin(2 * np.pi * self.f_rot * self.time) +
                 0.05 * np.sin(2 * np.pi * 2 * self.f_rot * self.time) +
                 0.05 * np.random.randn(self.n_samples))
        
        # Noise levels: low=30dB, medium=15dB, high=5dB
        snr_map = {'low': 30, 'medium': 15, 'high': 5}
        return self.add_noise(signal, snr_db=snr_map[noise_level])
    
    def generate_ball_fault(self, noise_level='low'):
        """Generate ball bearing fault signal"""
        impulse_train = np.zeros(self.n_samples)
        impulse_period = int(self.fs / self.f_bpfo)
        
        for i in range(0, self.n_samples, impulse_period):
            if i < self.n_samples:
                decay_len = min(200, self.n_samples - i)
                decay = np.exp(-np.arange(decay_len) / 50)
                impulse_train[i:i+decay_len] += decay * np.random.uniform(0.8, 1.2)
        
        carrier = 1 + 0.3 * np.sin(2 * np.pi * self.f_rot * self.time)
        signal = impulse_train * carrier
        background = 0.05 * np.sin(2 * np.pi * self.f_rot * self.time)
        
        snr_map = {'low': 25, 'medium': 12, 'high': 3}
        return self.add_noise(signal + background, snr_db=snr_map[noise_level])
    
    def generate_inner_race_fault(self, noise_level='low'):
        """Generate inner race fault signal"""
        impulse_train = np.zeros(self.n_samples)
        impulse_period = int(self.fs / self.f_bpfi)
        
        for i in range(0, self.n_samples, impulse_period):
            if i < self.n_samples:
                decay_len = min(150, self.n_samples - i)
                decay = np.exp(-np.arange(decay_len) / 30)
                impulse_train[i:i+decay_len] += decay * np.random.uniform(1.0, 1.5)
        
        modulation = 1 + 0.5 * np.sin(2 * np.pi * self.f_rot * self.time)
        signal = impulse_train * modulation
        background = 0.08 * np.sin(2 * np.pi * self.f_rot * self.time)
        
        snr_map = {'low': 25, 'medium': 10, 'high': 2}
        return self.add_noise(signal + background, snr_db=snr_map[noise_level])
    
    def generate_outer_race_fault(self, noise_level='low'):
        """Generate outer race fault signal"""
        impulse_train = np.zeros(self.n_samples)
        impulse_period = int(self.fs / self.f_bpfo)
        
        for i in range(0, self.n_samples, impulse_period):
            if i < self.n_samples:
                decay_len = min(180, self.n_samples - i)
                decay = np.exp(-np.arange(decay_len) / 40)
                impulse_train[i:i+decay_len] += decay * np.random.uniform(0.9, 1.1)
        
        modulation = 1 + 0.2 * np.sin(2 * np.pi * self.f_rot * self.time)
        signal = impulse_train * modulation
        background = 0.06 * np.sin(2 * np.pi * self.f_rot * self.time)
        
        snr_map = {'low': 28, 'medium': 13, 'high': 4}
        return self.add_noise(signal + background, snr_db=snr_map[noise_level])
    
    def save_to_csv(self, signal, filename):
        """Save signal to CSV file (single row with comma separation)"""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(signal.tolist())
        
        print(f"✅ Generated: {filename}")


def main():
    print("=" * 70)
    print("  CSV TEST DATA GENERATOR")
    print("  1 file per noise level per fault type (12 files total)")
    print("=" * 70)
    print()
    
    # Create output directory
    output_dir = 'csv_test_files'
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize generator
    generator = SimpleCSVGenerator(sampling_rate=12000, duration=0.2)
    
    # Noise levels to generate
    noise_levels = ['low', 'medium', 'high']
    
    # Fault type generators
    fault_generators = {
        'normal': generator.generate_normal,
        'ball': generator.generate_ball_fault,
        'inner_race': generator.generate_inner_race_fault,
        'outer_race': generator.generate_outer_race_fault
    }
    
    print("📊 Generating CSV files...\n")
    
    file_count = 0
    
    # Generate files
    for fault_name, generator_func in fault_generators.items():
        print(f"🔧 {fault_name.upper()} fault:")
        
        for noise_level in noise_levels:
            signal = generator_func(noise_level)
            filename = os.path.join(output_dir, f'{fault_name}_{noise_level}.csv')
            generator.save_to_csv(signal, filename)
            file_count += 1
        
        print()
    
    print("=" * 70)
    print("✅ GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\n📁 Location: {output_dir}/")
    print(f"📊 Total files: {file_count}")
    print(f"\n📋 Generated files:")
    print(f"   - normal_low.csv, normal_medium.csv, normal_high.csv")
    print(f"   - ball_low.csv, ball_medium.csv, ball_high.csv")
    print(f"   - inner_race_low.csv, inner_race_medium.csv, inner_race_high.csv")
    print(f"   - outer_race_low.csv, outer_race_medium.csv, outer_race_high.csv")
    
    # Create summary file
    summary_file = os.path.join(output_dir, 'README.txt')
    with open(summary_file, 'w') as f:
        f.write("CSV TEST DATA FILES\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("STRUCTURE:\n")
        f.write("12 files total - 3 noise levels per fault type:\n\n")
        f.write("NORMAL:\n")
        f.write("  - normal_low.csv    (SNR: 30 dB - Clean signal)\n")
        f.write("  - normal_medium.csv (SNR: 15 dB - Moderate noise)\n")
        f.write("  - normal_high.csv   (SNR: 5 dB  - Heavy noise)\n\n")
        f.write("BALL FAULT:\n")
        f.write("  - ball_low.csv      (SNR: 25 dB)\n")
        f.write("  - ball_medium.csv   (SNR: 12 dB)\n")
        f.write("  - ball_high.csv     (SNR: 3 dB)\n\n")
        f.write("INNER RACE FAULT:\n")
        f.write("  - inner_race_low.csv    (SNR: 25 dB)\n")
        f.write("  - inner_race_medium.csv (SNR: 10 dB)\n")
        f.write("  - inner_race_high.csv   (SNR: 2 dB)\n\n")
        f.write("OUTER RACE FAULT:\n")
        f.write("  - outer_race_low.csv    (SNR: 28 dB)\n")
        f.write("  - outer_race_medium.csv (SNR: 13 dB)\n")
        f.write("  - outer_race_high.csv   (SNR: 4 dB)\n\n")
        f.write("SPECIFICATIONS:\n")
        f.write(f"- Sampling Rate: 12,000 Hz\n")
        f.write(f"- Duration: 0.2 seconds\n")
        f.write(f"- Data Points: 2,400 per file\n\n")
        f.write("FORMAT:\n")
        f.write("Single row with comma-separated values:\n")
        f.write("  0.123,0.234,0.345,0.456,...\n")
    
    print(f"\n📄 Summary saved: {summary_file}\n")
    print(f"💡 Test with: python3 test_csv_files.py all\n")


if __name__ == "__main__":
    main()
