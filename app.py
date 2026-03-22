import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Import your custom modules
from utils import analyze_email
from gpt_service import scan_with_gpt
from gmail_service import fetch_latest_emails

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_77")

# Required for Render/Chrome Extension Cookies
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
)
CORS(app, supports_credentials=True)

# --- Google OAuth Setup ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = google.authorize_access_token()
    session['google_token'] = token
    return redirect(url_for('dashboard_view'))

@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html')

# NEW: Route for the Extension "Analyze" Button
@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', 'No Subject')
    
    # ML Analysis
    ml_res = analyze_email(content)
    # GPT Deep Dive
    gpt_res = scan_with_gpt(content, ml_res['phishing_score'])
    
    return jsonify({
        "subject": subject,
        "score": round(float(ml_res['phishing_score']) * 100, 2),
        "verdict": gpt_res['verdict'],
        "explanation": gpt_res['explanation']
    })

@app.route('/scan-inbox')
def scan_inbox():
    token = session.get('google_token')
    if not token: return jsonify({"error": "Unauthorized"}), 401
    
    emails = fetch_latest_emails(token)
    results = []
    for em in emails:
        ml = analyze_email(em['snippet'])
        gpt = scan_with_gpt(em['snippet'], ml['phishing_score'])
        results.append({
            "subject": em['subject'],
            "score": round(float(ml['phishing_score']) * 100, 2),
            "status": gpt['verdict'].lower(),
            "explanation": gpt['explanation']
        })
    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
