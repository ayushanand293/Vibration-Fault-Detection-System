import joblib
import os
import numpy as np

print("=" * 80)
print("🔍 CHECKING ALL MODELS IN PROJECT")
print("=" * 80)

model_files = [
    './backend/models/rf_model_real.pkl',
    './backend/ml_models/random_forest_model.pkl',
    './ml/models/random_forest_model.pkl'
]

for model_path in model_files:
    if os.path.exists(model_path):
        print(f"\n{'='*80}")
        print(f"📦 MODEL: {model_path}")
        print(f"{'='*80}")
        
        try:
            model = joblib.load(model_path)
            print(f"✅ Loaded successfully")
            print(f"   Type: {type(model).__name__}")
            
            if hasattr(model, 'classes_'):
                print(f"   Classes: {model.classes_}")
                print(f"   Number of classes: {len(model.classes_)}")
            
            if hasattr(model, 'n_features_in_'):
                print(f"   Features expected: {model.n_features_in_}")
            
            if hasattr(model, 'n_estimators'):
                print(f"   Number of trees: {model.n_estimators}")
                print(f"   Max depth: {model.max_depth}")
            
            # Try to get feature importances
            if hasattr(model, 'feature_importances_'):
                print(f"   Feature importances available: Yes")
                top_3_idx = np.argsort(model.feature_importances_)[-3:][::-1]
                print(f"   Top 3 important feature indices: {top_3_idx}")
            
            # Check file creation date
            stat = os.stat(model_path)
            from datetime import datetime
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   File size: {stat.st_size / 1024:.2f} KB")
            
        except Exception as e:
            print(f"❌ Error loading: {e}")
    else:
        print(f"\n❌ NOT FOUND: {model_path}")

# Also check scalers
print(f"\n{'='*80}")
print("🔧 CHECKING SCALERS")
print(f"{'='*80}")

scaler_files = [
    './backend/ml_models/scaler.pkl',
    './ml/models/scaler.pkl'
]

for scaler_path in scaler_files:
    if os.path.exists(scaler_path):
        print(f"\n📦 SCALER: {scaler_path}")
        try:
            scaler = joblib.load(scaler_path)
            print(f"✅ Loaded successfully")
            
            if hasattr(scaler, 'n_features_in_'):
                print(f"   Features expected: {scaler.n_features_in_}")
            
            if hasattr(scaler, 'feature_names_in_'):
                print(f"   Feature names: {list(scaler.feature_names_in_)}")
            
            stat = os.stat(scaler_path)
            from datetime import datetime
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n" + "=" * 80)
