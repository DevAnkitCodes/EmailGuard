import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Internal helper imports
from utils import analyze_email, load_model
from gpt_service import scan_with_gpt

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_77_secure")

# Enable CORS for Chrome Extension support
CORS(app)

# Load ML model once at startup safely
phish_model = load_model()

@app.route('/')
def login():
    """Serves login.html. Matches url_for('login')"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Serves dashboard.html. Matches url_for('dashboard')"""
    return render_template('dashboard.html')

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """Deep analysis endpoint for the Chrome Extension."""
    try:
        data = request.json or {}
        content = data.get('content', '')
        subject = data.get('subject', 'No Subject')
        
        # 1. Get ML Score from utils.py
        ml_res = analyze_email(content, phish_model)
        
        # 2. Get AI Explanation from gpt_service.py
        gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
        
        return jsonify({
            "subject": subject,
            "score": round(ml_res['phishing_score'] * 100, 2),
            "verdict": gpt_res.get('verdict', 'Neutral'),
            "explanation": gpt_res.get('explanation', 'Analysis complete.')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scan-inbox')
def scan_inbox():
    """Data source for Dashboard Charts."""
    return jsonify([
        {"subject": "Urgent Account Verification", "score": 94, "status": "phishing"},
        {"subject": "Team Lunch Sync", "score": 4, "status": "safe"},
        {"subject": "Your Invoice is Overdue", "score": 82, "status": "phishing"}
    ])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
