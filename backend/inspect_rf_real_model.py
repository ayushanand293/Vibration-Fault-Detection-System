import joblib
import numpy as np

print("=" * 70)
print("🔍 INSPECTING: models/rf_model_real.pkl")
print("=" * 70)

try:
    model = joblib.load('models/rf_model_real.pkl')
    
    print(f"\n✅ Model loaded successfully!")
    print(f"   Model type: {type(model).__name__}")
    
    if hasattr(model, 'classes_'):
        print(f"   Classes: {model.classes_}")
    
    if hasattr(model, 'n_features_in_'):
        print(f"   Number of features expected: {model.n_features_in_}")
    
    if hasattr(model, 'feature_names_in_'):
        print(f"\n📋 FEATURE NAMES EXPECTED BY MODEL:")
        print(f"   (in exact order)")
        for i, name in enumerate(model.feature_names_in_, 1):
            print(f"      {i:2d}. {name}")
    else:
        print(f"\n⚠️  Model doesn't have feature_names_in_ attribute")
        print(f"   This means it was trained without explicit feature names")
    
    # Check model details
    if hasattr(model, 'n_estimators'):
        print(f"\n🌲 Random Forest Details:")
        print(f"   Number of trees: {model.n_estimators}")
        print(f"   Max depth: {model.max_depth}")
    
except FileNotFoundError:
    print("❌ File not found: models/rf_model_real.pkl")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

# Also check scaler
print("\n🔍 INSPECTING: ml_models/scaler.pkl")
print("=" * 70)

try:
    scaler = joblib.load('ml_models/scaler.pkl')
    
    print(f"\n✅ Scaler loaded successfully!")
    print(f"   Scaler type: {type(scaler).__name__}")
    
    if hasattr(scaler, 'n_features_in_'):
        print(f"   Number of features expected: {scaler.n_features_in_}")
    
    if hasattr(scaler, 'feature_names_in_'):
        print(f"\n📋 FEATURE NAMES EXPECTED BY SCALER:")
        print(f"   (in exact order)")
        for i, name in enumerate(scaler.feature_names_in_, 1):
            print(f"      {i:2d}. {name}")
    
    if hasattr(scaler, 'mean_'):
        print(f"\n📊 Scaler Statistics:")
        print(f"   Mean values: {scaler.mean_[:5]}... (showing first 5)")
        print(f"   Scale values: {scaler.scale_[:5]}... (showing first 5)")
    
except FileNotFoundError:
    print("❌ File not found: ml_models/scaler.pkl")
except Exception as e:
    print(f"❌ Error loading scaler: {e}")

print("\n" + "=" * 70)
