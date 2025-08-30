# fake_url_detection.py

import whois
import streamlit as st
from playwright.sync_api import sync_playwright
import google.generativeai as genai

# ---------------- CONFIG ----------------
# Make sure you store your GEMINI API key in Streamlit Secrets
# st.secrets["API_KEY"]
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

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

# ---------------- PLAYWRIGHT PAGE ANALYSIS ----------------
def analyze_page_playwright(url: str) -> dict:
    """
    Headlessly opens the page using Playwright.
    Checks for login/password fields.
    """
    data = {"title": None, "has_login": False, "error": None}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            data["title"] = page.title()
            html = page.content().lower()
            if "password" in html or "login" in html:
                data["has_login"] = True
            browser.close()
    except Exception as e:
        data["error"] = str(e)
    return data

# ---------------- GEMINI AI VERDICT ----------------
def gemini_verdict(url: str, whois_data: dict, page_data: dict) -> str:
    """
    Uses Gemini AI to give final verdict + suggestions
    """
    prompt = f"""
You are an AI cybersecurity assistant.

Analyze the following URL and determine if it is safe, suspicious, or phishing.

URL: {url}
WHOIS Info: {whois_data}
Page Analysis: {page_data}

Return only:
- Final Verdict: Safe ✅ / Suspicious ⚠️ / Phishing ❌
- Short suggestion for the user (1-2 sentences)
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI analysis failed: {str(e)}"

# ---------------- MAIN DETECTOR ----------------
def phishing_detector(url: str) -> str:
    """
    Returns Gemini verdict only
    """
    whois_data = check_whois(url)
    page_data = analyze_page_playwright(url)
    verdict = phishing_detector(url)
    return verdict
