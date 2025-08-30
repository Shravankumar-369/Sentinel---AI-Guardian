# fake_url_detection.py

import whois
import streamlit as st
from openai import OpenAI
from playwright.sync_api import sync_playwright

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

# ---------------- PLAYWRIGHT PAGE ANALYSIS ----------------
def analyze_page_playwright(url: str) -> dict:
    """
    Opens the page headlessly using Playwright and checks if it has login/password fields.
    Returns a simple dict for AI input.
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

# ---------------- GPT-5 VERDICT ----------------
def ai_verdict_gpt(url: str, whois_data: dict, page_data: dict) -> str:
    """
    Uses GPT-5 to give a final verdict + short suggestions based on WHOIS and page info.
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
    page_data = analyze_page_playwright(url)
    verdict = ai_verdict_gpt(url, whois_data, page_data)
    return verdict
