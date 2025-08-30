import whois
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 🔑 Secure API key from Streamlit secrets
GEMINI_API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def get_page_details(url):
    """
    Fetch basic webpage info using requests + BeautifulSoup.
    Detects title and whether login fields are present.
    """
    page_data = {"title": None, "has_login": False, "error": None}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        if soup.title:
            page_data["title"] = soup.title.string.strip()

        # Look for login/password fields
        html = response.text.lower()
        if "password" in html or "login" in html:
            page_data["has_login"] = True

    except Exception as e:
        page_data["error"] = f"Could not load page: {str(e)}"

    return page_data


def check_whois(url):
    """
    Perform WHOIS lookup for domain info
    """
    try:
        domain_info = whois.whois(url)
        return {
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
        }
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}"}


def gemini_verdict(url, page_data, whois_data):
    """
    Use Gemini AI to analyze phishing risk
    """
    prompt = f"""
    Analyze this website for phishing risk:

    URL: {url}
    Page Title: {page_data.get('title')}
    Login Field Present: {page_data.get('has_login')}
    Page Error: {page_data.get('error')}

    WHOIS Info: {whois_data}

    Return verdict:
    - Safe ✅
    - Suspicious ⚠
    - Phishing ❌
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI analysis failed: {str(e)}"


def phishing_detector(url):
    """
    Full pipeline: fetch page details, WHOIS info, AI verdict
    """
    page_data = get_page_details(url)
    whois_data = check_whois(url)
    verdict = gemini_verdict(url, page_data, whois_data)

    return page_data, whois_data, verdict
