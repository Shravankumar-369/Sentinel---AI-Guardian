
import whois
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

GEMINI_API_KEY = "enteryourapikey"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_page_details(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    page_data = {"title": None, "has_login": False, "error": None}

    try:
        driver.get(url)
        page_data["title"] = driver.title
        html = driver.page_source.lower()
        if "password" in html or "login" in html:
            page_data["has_login"] = True
    except Exception as e:
        page_data["error"] = f"Could not load page: {str(e)}"
    finally:
        driver.quit()
    return page_data

def check_whois(url):
    try:
        domain_info = whois.whois(url)
        return {
            "registrar": domain_info.registrar,
            "creation_date": domain_info.creation_date,
            "expiration_date": domain_info.expiration_date,
        }
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}"}

def gemini_verdict(url, page_data, whois_data):
    prompt = f"""
    Analyze this website for phishing risk:

    URL: {url}
    Page Title: {page_data.get('title')}
    Login Field Present: {page_data.get('has_login')}
    Page Error: {page_data.get('error')}

    WHOIS Info: {whois_data}

    Return verdict:
    - Safe ✅
    - Suspicious ⚠️
    - Phishing ❌
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI analysis failed: {str(e)}"

def phishing_detector(url):
    page_data = get_page_details(url)
    whois_data = check_whois(url)
    verdict = gemini_verdict(url, page_data, whois_data)
    return page_data, whois_data, verdict
