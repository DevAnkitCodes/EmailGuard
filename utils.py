import joblib
import os

def load_model():
    """Safely loads the model and handles version mismatch errors."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_path, 'ml', 'final_phishing_model_v1.pkl')
    
    try:
        if os.path.exists(model_path):
            # Attempting load - this is where KeyError 118 usually triggers
            model = joblib.load(model_path)
            print("✅ Model loaded successfully!")
            return model
        else:
            print(f"❌ Model file not found at: {model_path}")
            return None
    except KeyError as e:
        if str(e) == "'118'":
            print("⚠️ Error 118 detected: Model/Server version mismatch.")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected model error: {e}")
        return None

def analyze_email(text, model):
    """Predicts phishing probability. Returns 0.5 if model is unavailable."""
    if model is None:
        return {'phishing_score': 0.5}
    
    try:
        # Standard prediction probability
        prediction = model.predict_proba([text])[0][1]
        return {'phishing_score': prediction}
    except Exception as e:
        print(f"Prediction error: {e}")
        return {'phishing_score': 0.5}
