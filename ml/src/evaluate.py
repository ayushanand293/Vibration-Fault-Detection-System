from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import numpy as np

def evaluate_model(model_path, X_test, y_test):
    model = joblib.load(model_path)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred)
    
    return {
        "accuracy": accuracy,
        "confusion_matrix": conf_matrix.tolist(),
        "classification_report": class_report
    }