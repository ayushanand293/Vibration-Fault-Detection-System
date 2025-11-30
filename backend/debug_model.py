# Debug script to check model's expected features
import pickle

# Load the model
with open('ml_models/random_forest_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Get feature names the model expects
if hasattr(model, 'feature_names_in_'):
    print("✅ Model expects these features (in this order):")
    print("="*70)
    for i, feature in enumerate(model.feature_names_in_):
        print(f"{i+1:2d}. {feature}")
    print("="*70)
else:
    print("⚠️  Model doesn't have feature_names_in_ attribute")
    
# Get number of features
print(f"\nTotal features expected: {model.n_features_in_}")
