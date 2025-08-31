import whois
import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import ssl
import socket
import OpenSSL

# 🔑 Secure API key from Streamlit secrets
GEMINI_API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# --- Lexical Features ---
def lexical_features(url):
    features = {}
    features['has_ip'] = any(c.isdigit() for c in url.split("//")[-1].split("/")[0])
    features['has_https'] = url.lower().startswith("https://")
    return features


# --- SSL Certificate Info ---
def ssl_info(url):
    try:
        hostname = url.split("//")[-1].split("/")[0]
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert = s.getpeercert(binary_form=True)
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)
            return {
                "subject": dict(x509.get_subject().get_components()),
                "issuer": dict(x509.get_issuer().get_components()),
                "not_before": x509.get_notBefore().decode(),
                "not_after": x509.get_notAfter().decode()
            }
    except Exception as e:
        return {"error": str(e)}


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


def gemini_verdict(url, page_data, whois_data, lexical_data, ssl_data):
    """
    Use Gemini AI to analyze phishing risk
    """
    prompt = f"""
    Analyze this website for phishing risk:

    URL: {url}
    Lexical Features: {lexical_data}
    Page Title: {page_data.get('title')}
    Login Field Present: {page_data.get('has_login')}
    Page Error: {page_data.get('error')}
    WHOIS Info: {whois_data}
    SSL Info: {ssl_data}

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
    Full pipeline: lexical features, page details, WHOIS info, SSL, AI verdict
    Returns 3 values: page_data, whois_data, verdict
    """
    lexical_data = lexical_features(url)
    page_data = get_page_details(url)
    whois_data = check_whois(url)
    ssl_data = ssl_info(url)
    verdict = gemini_verdict(url, page_data, whois_data, lexical_data, ssl_data)

    return page_data, whois_data, verdict
