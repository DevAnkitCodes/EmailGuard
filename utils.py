# utils.py
import joblib
import os

# Get the path to the model file inside the ml/ folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'phishing_model.pkl')

# Load model once when the app starts
try:
    model = joblib.load(MODEL_PATH)
    print("SUCCESS: ML Model loaded.")
except Exception as e:
    print(f"ERROR: Could not load model: {e}")
    model = None

def analyze_email(text):
    if model:
        # This assumes your model expects a list/array of text
        prediction = model.predict_proba([text])[0]
        score = prediction[1] # Probability of being 'Phishing'
    else:
        score = 0.5 # Fallback if model fails
        
    return {"phishing_score": score}