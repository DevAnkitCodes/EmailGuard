import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Import your helper functions
from utils import analyze_email, load_model
from gpt_service import scan_with_gpt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_77")

# Allow the Extension to talk to the Flask server
CORS(app, supports_credentials=True)

# Load the ML model at startup
# Ensure your file is named 'phishing_model.pkl' inside the 'ml' folder
phish_model = load_model()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')

# --- EXTENSION ROUTE: Analyzes the specific email you click in Gmail ---
@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    try:
        data = request.json
        content = data.get('content', '')
        subject = data.get('subject', 'No Subject')
        
        # 1. Get ML Score (uses the loaded model)
        ml_res = analyze_email(content, phish_model)
        
        # 2. Get GPT Detailed Explanation
        gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
        
        return jsonify({
            "subject": subject,
            "score": round(float(ml_res['phishing_score']) * 100, 2),
            "verdict": gpt_res['verdict'],
            "explanation": gpt_res['explanation']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- DASHBOARD ROUTE: Scans the general inbox ---
@app.route('/scan-inbox')
def scan_inbox():
    # If model failed to load (Error 118), we return a default message instead of crashing
    if phish_model is None:
        return jsonify([{"subject": "System Warning", "score": 0, "status": "safe", "explanation": "ML Model failed to load. Check Render logs for Error 118."}])
    
    # Normally you'd fetch real emails here. For now, we return sample data:
    results = [
        {"subject": "Urgent: Account Verification", "score": 88, "status": "phishing", "explanation": "Suspicious urgency and link."},
        {"subject": "Project Update", "score": 5, "status": "safe", "explanation": "Regular business communication."}
    ]
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
