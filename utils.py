import joblib
import os
import numpy as np

def load_model():
    """
    Safely loads the phishing detection model from the 'ml' folder.
    Handles 'Error 118' (version mismatch) to prevent server crashes.
    """
    # Build the path to the model file
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'ml', 'final_phishing_model_v1.pkl')
    
    try:
        if os.path.exists(model_path):
            # Attempt to load the model
            model = joblib.load(model_path)
            print("✅ ML Model loaded successfully.")
            return model
        else:
            print(f"❌ CRITICAL: Model file not found at {model_path}")
            return None
            
    except KeyError as e:
        if str(e) == '118':
            print("⚠️ ERROR 118: scikit-learn version mismatch between local and Render.")
            print("Check your requirements.txt and ensure scikit-learn matches your local version.")
        else:
            print(f"⚠️ Model Load Error: {e}")
        return None
        
    except Exception as e:
        print(f"⚠️ Unexpected Error loading model: {e}")
        return None

def analyze_email(text, model):
    """
    Processes email text and returns a phishing probability score.
    Returns a safe default score (0.5) if the model is not loaded.
    """
    # 1. Fallback: If model failed to load, return a neutral 'unknown' score
    if model is None:
        return {'phishing_score': 0.5}
    
    try:
        # 2. Basic Preprocessing: Wrap text in a list for the model's vectorizer
        # Note: This assumes your .pkl file contains a Pipeline (Vectorizer + Model)
        # If your model requires manual vectorization, add that logic here.
        prediction_proba = model.predict_proba([text])
        
        # Get the probability for the 'Phishing' class (usually index 1)
        score = prediction_proba[0][1]
        
        return {'phishing_score': float(score)}
        
    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        # Return neutral score on failure to keep the UI running
        return {'phishing_score': 0.5}

def get_verdict(score):
    """
    Simple helper to turn a numerical score into a label.
    """
    if score > 0.7:
        return "High Risk"
    elif score > 0.4:
        return "Suspicious"
    else:
        return "Safe"
