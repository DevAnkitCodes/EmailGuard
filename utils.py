import joblib
import os
import numpy as np

def load_model():
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'ml', 'phishing_model.pkl')
    try:
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None
    except Exception as e:
        print(f"Model Load Error: {e}")
        return None

def analyze_email(text, model):
    if model is None:
        return {'phishing_score': 0.5} # Fallback if model fails
    
    # Replace this with your actual feature extraction logic
    prediction = model.predict_proba([text])[0][1] 
    return {'phishing_score': prediction}
