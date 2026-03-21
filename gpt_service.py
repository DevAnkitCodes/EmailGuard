# gpt_service.py
import os
import google.generativeai as genai

def scan_with_gpt(email_text, ml_score):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Analyze this email: "{email_text}"
    The Machine Learning model gave it a risk score of {ml_score*100}%.
    
    Provide a JSON response with:
    1. "verdict": (Safe, Suspicious, or Dangerous)
    2. "explanation": (A 1-sentence reason why)
    """
    
    try:
        response = model.generate_content(prompt)
        # Simple parsing (In production, use a JSON parser)
        text = response.text
        verdict = "Suspicious"
        if "Safe" in text: verdict = "Safe"
        if "Dangerous" in text: verdict = "Dangerous"
        
        return {
            "verdict": verdict,
            "explanation": text.split("explanation\":")[-1].replace("}", "").strip().strip('"')
        }
    except:
        return {"verdict": "Suspicious", "explanation": "AI analysis currently unavailable."}