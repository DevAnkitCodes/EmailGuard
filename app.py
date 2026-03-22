import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure these files (utils.py, gpt_service.py) are in your root folder
from utils import analyze_email, load_model
from gpt_service import scan_with_gpt

# 1. Initialize App and Environment
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_secure_77")

# 2. Enable CORS
# This allows your Chrome Extension to send data to this Render server
CORS(app, supports_credentials=True)

# 3. Load ML Model at Startup
# This handles 'Error 118' gracefully so the site doesn't crash on boot
phish_model = load_model()

# --- ROUTES ---

@app.route('/')
def login():
    """
    Serves the login page. 
    Function name 'login' matches {{ url_for('login') }} in your HTML.
    """
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """
    Serves the main dashboard. 
    Function name 'dashboard' matches {{ url_for('dashboard') }} in your HTML.
    """
    return render_template('dashboard.html')

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """
    Endpoint for the Chrome Extension button.
    Receives email content and returns a score + AI explanation.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        content = data.get('content', '')
        subject = data.get('subject', 'No Subject')
        
        # 1. ML Prediction (Uses the loaded model)
        ml_res = analyze_email(content, phish_model)
        
        # 2. GPT/Gemini Detailed Analysis
        gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
        
        return jsonify({
            "subject": subject,
            "score": round(float(ml_res['phishing_score']) * 100, 2),
            "verdict": gpt_res.get('verdict', 'Neutral'),
            "explanation": gpt_res.get('explanation', 'AI analysis complete.')
        })
    except Exception as e:
        print(f"Error in /analyze-single: {e}")
        return jsonify({"error": "Internal server error during analysis"}), 500

@app.route('/scan-inbox')
def scan_inbox():
    """
    Endpoint for the Dashboard charts.
    Provides the data that charts.js needs to draw the graphs.
    """
    # If the model failed to load (Error 118), we show a warning in the dashboard
    if phish_model is None:
        return jsonify([{
            "subject": "System Warning", 
            "score": 0, 
            "status": "safe", 
            "explanation": "ML Model failed to load (Error 118). Check Render requirements.txt."
        }])
    
    # Mock data for demonstration - Replace with real Gmail API logic if needed
    results = [
        {"subject": "Urgent: Verify Your Account", "score": 89, "status": "phishing", "explanation": "Urgent tone and suspicious link detected."},
        {"subject": "Project Deadline Update", "score": 12, "status": "safe", "explanation": "Standard business communication."},
        {"subject": "You Won a Gift Card!", "score": 95, "status": "phishing", "explanation": "Common phishing lure identified."}
    ]
    return jsonify(results)

# --- START SERVER ---

if __name__ == "__main__":
    # Render provides the port via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
