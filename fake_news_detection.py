
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSoup

GEMINI_API_KEY = "enteryourapikey"
genai.configure(api_key=GEMINI_API_KEY)

def fetch_related_articles(query, num_results=5):
    articles = []
    for url in search(query, num_results=num_results, lang="en"):
        try:
            resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else "No title"
            articles.append({"title": title.strip(), "url": url})
        except Exception:
            continue
    return articles

def analyze_with_gemini(user_input, articles):
    model = genai.GenerativeModel("gemini-1.5-flash")
    article_texts = "\n".join([f"- {a['title']} ({a['url']})" for a in articles])
    prompt = f"""
    A user submitted this news claim: "{user_input}"

    Here are some related articles from the web:
    {article_texts}

    Classify the claim as:
    - Likely True
    - Likely Fake
    - Unverified

    Give a short 2-3 sentence explanation.
    """
    response = model.generate_content(prompt)
    return response.text.strip()
