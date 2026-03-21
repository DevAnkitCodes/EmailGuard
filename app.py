import os
from flask import Flask, render_template, redirect, url_for, session, jsonify, request
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Import your helper scripts
from utils import analyze_email
from gpt_service import scan_with_gpt
from gmail_service import fetch_latest_emails

load_dotenv()

app = Flask(__name__)
# Render will use the SECRET_KEY set in its environment variables
app.secret_key = os.getenv("SECRET_KEY", "cyber_guard_secure_77")

# Allow cookies to work across the domain (Lax is safer for Render)
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True if os.getenv("RENDER") else False,
)

CORS(app, supports_credentials=True)

# --- Google OAuth Configuration ---
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
    # Use _external=True to generate absolute URLs for Google
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

@app.route('/scan-inbox')
def scan_inbox():
    token = session.get('google_token')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        emails = fetch_latest_emails(token)
        results = []
        for em in emails:
            ml_res = analyze_email(em['snippet'])
            gpt_res = scan_with_gpt(em['snippet'], ml_res['phishing_score'])
            
            results.append({
                "subject": str(em['subject'])[:50],
                "score": round(float(ml_res['phishing_score']), 2),
                "status": str(gpt_res['verdict']).lower(),
                "explanation": str(gpt_res['explanation'])
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Render provides the PORT variable; default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)