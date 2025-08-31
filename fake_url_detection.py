import streamlit as st
import requests
import socket
import ssl
import whois
from bs4 import BeautifulSoup
import google.generativeai as genai

# ----------------------------
# CONFIGURE GEMINI
# ----------------------------
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def check_ssl_certificate(domain):
    """Check if SSL certificate is valid for a domain"""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return True, cert.get("subject", [])
    except Exception as e:
        return False, str(e)


def check_dns(domain):
    """Check DNS resolution"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None


def get_whois_info(domain):
    """Fetch WHOIS information"""
    try:
        w = whois.whois(domain)
        return True, w
    except Exception as e:
        return False, str(e)


def get_page_content(url):
    """Fetch and parse page HTML with BeautifulSoup"""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            return True, soup.get_text()[:1000]  # limit to 1000 chars
        return False, f"Status {r.status_code}"
    except Exception as e:
        return False, str(e)


def gemini_analysis(url, page_text, whois_info, ssl_info, dns_info):
    """Ask Gemini to analyze if the URL is suspicious"""
    prompt = f"""
    Analyze the following URL and metadata to decide if it's a legitimate or fake/malicious site.

    URL: {url}

    Page Text (first 1000 chars): {page_text}

    WHOIS Info: {whois_info}

    SSL Info: {ssl_info}

    DNS Info: {dns_info}

    Respond with:
    - RISK LEVEL: (Safe / Suspicious / High Risk)
    - KEY REASONS: Bullet points
    - FINAL VERDICT: Short explanation
    """
    response = model.generate_content(prompt)
    return response.text
