import urllib.request
import scipy.io as sio
import os
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Create data directory
os.makedirs('data/cwru_raw', exist_ok=True)

print("="*60)
print("DOWNLOADING CWRU BEARING DATASET")
print("="*60)

# CWRU dataset URLs (1HP motor, 1797 RPM, normal and fault conditions)
urls = {
    'normal': 'https://engineering.case.edu/sites/default/files/2023-12/97.mat',
    'inner_race': 'https://engineering.case.edu/sites/default/files/2023-12/105.mat',
    'outer_race': 'https://engineering.case.edu/sites/default/files/2023-12/118.mat',
    'ball': 'https://engineering.case.edu/sites/default/files/2023-12/130.mat'
}

print("\nAttempting to download CWRU dataset files...")
print("Note: If downloads fail, please download manually from:")
print("https://engineering.case.edu/bearingdatacenter/")
print()

for fault_type, url in urls.items():
    file_path = f'data/cwru_raw/{fault_type}.mat'
    
    if not os.path.exists(file_path):
        print(f"Downloading {fault_type}...")
        try:
            urllib.request.urlretrieve(url, file_path)
            print(f"✓ Downloaded: {fault_type}")
        except Exception as e:
            print(f"⚠ Could not download {fault_type}: {type(e).__name__}")
            print(f"  URL: {url}")
    else:
        print(f"✓ Already exists: {fault_type}")

print("\n" + "="*60)
print("Download process complete!")
print("="*60)