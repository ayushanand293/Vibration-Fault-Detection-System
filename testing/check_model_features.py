import joblib
import numpy as np

# Load model
model = joblib.load('backend/models/rf_model_real.pkl')

print("Model classes:", model.classes_)
print("Number of features expected:", model.n_features_in_)
print("\nModel info:")
print(f"  - Trees: {model.n_estimators}")
print(f"  - Max depth: {model.max_depth}")

# Test with dummy data
dummy_features = np.zeros((1, 14))
print("\nTest prediction with zeros:", model.predict(dummy_features))
print("Test probabilities:", model.predict_proba(dummy_features))
