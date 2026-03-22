import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Import your helper functions
# Ensure these files (utils.py, gpt_service.py) are in your root folder
from utils import analyze_email, load_model
from gpt_service import scan_with_gpt

# 1. Initialize App and Environment
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_secure_77")

# 2. Enable CORS
# This is critical so your Chrome Extension can send data to Render
CORS(app, supports_credentials=True)

# 3. Load ML Model at Startup
# This handles the 'Error 118' gracefully so the site doesn't crash
phish_model = load_model()

# --- ROUTES ---

@app.route('/')
def login():
    """
    Serves the login page. 
    Function name 'login' must match {{ url_for('login') }} in HTML.
    """
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """
    Serves the dashboard page. 
    Function name 'dashboard' must match {{ url_for('dashboard') }} in HTML.
    """
    return render_template('dashboard.html')

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """
    Endpoint for the Chrome Extension.
    Receives email content and returns score + AI explanation.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        content = data.get('content', '')
        subject = data.get('subject', 'No Subject')
        
        # ML Prediction (Fallback to 0.5 if model failed to load)
        ml_res = analyze_email(content, phish_model)
        
        # GPT/Gemini Detailed Analysis
        gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
        
        return jsonify({
            "subject": subject,
            "score": round(float(ml_res['phishing_score']) * 100, 2),
            "verdict": gpt_res.get('verdict', 'Neutral'),
            "explanation": gpt_res.get('explanation', 'AI analysis complete.')
        })
    except Exception as e:
        print(f"Error in /analyze-single: {e}")
        return jsonify({"error": "Analysis failed"}), 500

@app.route('/scan-inbox')
def scan_inbox():
    """
    Endpoint for the Dashboard charts.
    Provides data to charts.js.
    """
    # If model failed to load (Error 118), we show a system message
    if phish_model is None:
        return jsonify([{
            "subject": "System Alert", 
            "score": 0, 
            "status": "safe", 
            "explanation": "ML Model failed to load. Check requirements.txt for scikit-learn version."
        }])
    
    # Mock data for demonstration - Replace with real Gmail API logic if needed
    results = [
        {"subject": "Urgent: Password Reset", "score": 88, "status": "phishing", "explanation": "Urgent tone and suspicious link."},
        {"subject": "Weekly Newsletter", "score": 5, "status": "safe", "explanation": "Verified sender."}
    ]
    return jsonify(results)

# --- START SERVER ---

if __name__ == "__main__":
    # Render provides the port via environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
