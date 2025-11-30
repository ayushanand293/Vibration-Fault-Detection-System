import joblib
import os
from datetime import datetime

print("=" * 80)
print("🔍 DETAILED SCALER ANALYSIS")
print("=" * 80)

scaler_paths = [
    './backend/ml_models/scaler.pkl',
    './ml/models/scaler.pkl',
    './backend/models/scaler.pkl',  # Check if it exists here
    './models/scaler.pkl',
    './scaler.pkl'
]

for scaler_path in scaler_paths:
    if os.path.exists(scaler_path):
        print(f"\n{'='*80}")
        print(f"📦 SCALER: {scaler_path}")
        print(f"{'='*80}")
        
        try:
            scaler = joblib.load(scaler_path)
            
            stat = os.stat(scaler_path)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"✅ Loaded successfully")
            print(f"   Type: {type(scaler).__name__}")
            print(f"   File size: {stat.st_size / 1024:.2f} KB")
            print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if hasattr(scaler, 'n_features_in_'):
                print(f"   Features expected: {scaler.n_features_in_}")
            
            if hasattr(scaler, 'feature_names_in_'):
                print(f"\n   Feature names ({len(scaler.feature_names_in_)}):")
                for i, name in enumerate(scaler.feature_names_in_, 1):
                    print(f"      {i:2d}. {name}")
            else:
                print("   ⚠️  No feature names stored")
            
            if hasattr(scaler, 'mean_'):
                print(f"\n   Statistics:")
                print(f"      Mean (first 5): {scaler.mean_[:5]}")
                print(f"      Scale (first 5): {scaler.scale_[:5]}")
            
        except Exception as e:
            print(f"❌ Error loading: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ NOT FOUND: {scaler_path}")

print("\n" + "=" * 80)
print("🔍 COMPARING WITH rf_model_real.pkl")
print("=" * 80)

try:
    model = joblib.load('./backend/models/rf_model_real.pkl')
    stat = os.stat('./backend/models/rf_model_real.pkl')
    mod_time = datetime.fromtimestamp(stat.st_mtime)
    
    print(f"\n✅ Model: rf_model_real.pkl")
    print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Features expected: {model.n_features_in_}")
    print(f"   Classes: {model.classes_}")
    
    print("\n🎯 MATCHING CRITERIA:")
    print("   - Scaler should have 14 features (not 14 features with different names)")
    print("   - Scaler modified around same time as model")
    print("   - Scaler should be in backend/models/ directory")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")

print("\n" + "=" * 80)
