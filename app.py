import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Import your helper modules
from utils import analyze_email, load_model
from gpt_service import scan_with_gpt

# 1. Setup Environment and App
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_77")

# 2. Enable CORS so the Chrome Extension can talk to this server
CORS(app, supports_credentials=True)

# 3. Load the ML Model at Startup
# phish_model will be None if the .pkl file is missing or has a version error
phish_model = load_model()

# --- ROUTES ---

@app.route('/')
def login():
    """Serves the login page. Matches url_for('login') in your HTML."""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Serves the main dashboard. Matches url_for('dashboard') in your HTML."""
    return render_template('dashboard.html')

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """
    Endpoint for the Chrome Extension.
    Receives email content and returns a score + AI explanation.
    """
    try:
        data = request.json
        content = data.get('content', '')
        subject = data.get('subject', 'No Subject')
        
        # 1. ML Prediction (returns 0.5 as fallback if model failed to load)
        ml_res = analyze_email(content, phish_model)
        
        # 2. AI Explanation using Gemini/GPT
        gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
        
        return jsonify({
            "subject": subject,
            "score": round(float(ml_res['phishing_score']) * 100, 2),
            "verdict": gpt_res.get('verdict', 'Unknown'),
            "explanation": gpt_res.get('explanation', 'AI could not generate an explanation at this time.')
        })
    except Exception as e:
        print(f"Error in /analyze-single: {e}")
        return jsonify({"error": "Internal server error during analysis"}), 500

@app.route('/scan-inbox')
def scan_inbox():
    """
    Endpoint for the Dashboard charts.
    Provides dummy data for the inbox health and global risk charts.
    """
    # If the model failed to load (Error 118), we show a warning in the dashboard
    if phish_model is None:
        return jsonify([{
            "subject": "System Warning", 
            "score": 0, 
            "status": "safe", 
            "explanation": "ML Model failed to load (Error 118). Verify requirements.txt versions."
        }])
    
    # Sample data to populate the charts
    results = [
        {"subject": "Urgent: Verify Your Account", "score": 89, "status": "phishing", "explanation": "Urgent language and suspicious link detected."},
        {"subject": "Project Deadline Update", "score": 12, "status": "safe", "explanation": "Standard business communication."},
        {"subject": "You Won a Gift Card!", "score": 95, "status": "phishing", "explanation": "Common phishing lure identified."}
    ]
    return jsonify(results)

# --- START SERVER ---

if __name__ == "__main__":
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
