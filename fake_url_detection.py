import whois
import requests
import google.generativeai as genai
import streamlit as st

# Configure Gemini AI
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- WHOIS CHECK ----------------
def check_whois(url):
    try:
        domain_info = whois.whois(url)
        return {
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
        }
    except Exception as e:
        return {"error": str(e)}

# ---------------- VIRUSTOTAL CHECK ----------------
def check_virustotal(url):
    api_key = st.secrets["VIRUSTOTAL_API_KEY"]
    headers = {"x-apikey": api_key}
    vt_url = f"https://www.virustotal.com/api/v3/urls"
    
    # Encode URL as required by VT API
    import base64
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    
    try:
        response = requests.get(f"{vt_url}/{url_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            return stats  # Contains harmless, malicious, suspicious counts
        else:
            return {"error": f"VirusTotal response: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ---------------- AI VERDICT ----------------
def ai_verdict(url, whois_data, vt_data):
    prompt = f"""
Analyze this website for phishing risk:

URL: {url}
WHOIS Info: {whois_data}
VirusTotal Data: {vt_data}

Return the final verdict as one of:
- Safe ✅
- Suspicious ⚠️
- Phishing ❌

Also provide a short suggestion for the user.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI analysis failed: {str(e)}"

# ---------------- MAIN FUNCTION ----------------
def phishing_detector(url):
    whois_data = check_whois(url)
    vt_data = check_virustotal(url)
    verdict = ai_verdict(url, whois_data, vt_data)
    return verdict
