# fake_url_detection.py

import whois
import requests
from openai import OpenAI
import streamlit as st

# ---------------- CONFIG ----------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- WHOIS CHECK ----------------
def check_whois(url: str) -> dict:
    try:
        domain_info = whois.whois(url)
        return {
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
        }
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}"}

# ---------------- GOOGLE SAFE BROWSING ----------------
def check_google_safe(url: str) -> dict:
    api_key = st.secrets["GSB_API_KEY"]
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "sentinel", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", 
                            "POTENTIALLY_HARMFUL_APPLICATION", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        res = requests.post(endpoint, json=payload, timeout=10)
        data = res.json()
        if "matches" in data:
            return {"status": "malicious", "details": data["matches"]}
        else:
            return {"status": "safe"}
    except Exception as e:
        return {"status": "error", "details": str(e)}

# ---------------- GPT-5 VERDICT ----------------
def ai_verdict_gpt(url: str, whois_data: dict, safe_data: dict) -> str:
    prompt = f"""
You are an AI cybersecurity assistant.

Analyze the following URL and determine if it is safe, suspicious, or phishing.

URL: {url}
WHOIS Info: {whois_data}
Google Safe Browsing: {safe_data}

Return only:
- Final Verdict: Safe ✅ / Suspicious ⚠️ / Phishing ❌
- Short suggestion for the user (1-2 sentences)
"""
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()

# ---------------- MAIN DETECTOR ----------------
def phishing_detector(url: str) -> str:
    """
    Input: URL string
    Output: GPT-5 verdict + suggestion
    """
    whois_data = check_whois(url)
    safe_data = check_google_safe(url)
    verdict = ai_verdict_gpt(url, whois_data, safe_data)
    return verdict
