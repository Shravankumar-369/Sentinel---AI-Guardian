import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from PIL import Image
import json
import time

from fake_news_detection import fetch_related_articles, analyze_with_gemini
from fake_url_detection import phishing_detector

# ===============================
# Helper to load local Lottie JSON
# ===============================
def load_local_lottie(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠ Could not load animation: {e}")
        return None

# ===============================
# Session State for History
# ===============================
if "news_history" not in st.session_state:
    st.session_state.news_history = []

if "url_history" not in st.session_state:
    st.session_state.url_history = []

# ===============================
# Streamlit page config
# ===============================
st.set_page_config(page_title="Sentinel", page_icon="🛡", layout="wide")

# ===============================
# Sidebar Navigation
# ===============================
with st.sidebar:
    selected = option_menu(
        menu_title="Sentinel Menu",
         options=["Home", "Fake News Detection", "Phishing URL Detection","Notice","Report Now" , "About"],
        icons=["house", "newspaper", "link","Article","Report", "info-circle"],
        menu_icon="shield",
        default_index=0
    )

# ===============================
# Home Page
# ===============================
if selected == "Home":
    st.markdown(
        """
        <div style='text-align:center; background: linear-gradient(to right, #e0f7fa, #e8f5e9);
                     padding:50px; border-radius:20px'>
            <h1 style='color:#2f7a2e; font-size:48px; font-weight:bold'>
                🛡 Sentinel – Your AI Guardian Against Fake News & Phishing
            </h1>
            <p style='font-size:22px; color:#555;'>Verify news, check URLs, stay safe online</p>
        </div>
        """, unsafe_allow_html=True
    )

    # Hero Image
    hero_image = Image.open("assets/logo.jpg")
    st.image(hero_image, use_container_width=True)


# ===============================
# Fake News Detection Page
# ===============================
elif selected == "Fake News Detection":
    st.header("📰 Fake News Detection")
    # Lottie Animation
    lottie_ai = load_local_lottie("assets/lottie/news.json")
    if lottie_ai:
        st_lottie(lottie_ai, height=300)
    else:
        st.write("🎬 Animation not available")

    user_news = st.text_area("Enter a news headline or claim:")

    if st.button("Check News"):
        if user_news.strip() != "":
            with st.spinner("🔍 Fetching related articles..."):
                articles = fetch_related_articles(user_news, num_results=5)

            # Animated progress bar
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i+1)

            if not articles:
                st.warning("⚠ No related articles found. Claim is Unverified.")
                verdict = "Unverified"
            else:
                verdict = analyze_with_gemini(user_news, articles)
                st.success(verdict)

            # Save to history
            st.session_state.news_history.insert(0, {"claim": user_news, "verdict": verdict})
            if len(st.session_state.news_history) > 5:
                st.session_state.news_history.pop()

    # Display history as cards
    if st.session_state.news_history:
        st.subheader("📜 Recent News Checks")
        for item in st.session_state.news_history:
            st.markdown(f"""
            <div style='border:1px solid #2f7a2e; border-radius:10px; padding:10px; margin-bottom:10px;
                        background-color:#f0f9f0'>
                <b>Claim:</b> {item['claim']} <br>
                <b>Verdict:</b> <span style='color:#2f7a2e;'>{item['verdict']}</span>
            </div>
            """, unsafe_allow_html=True)

# ===============================
# Phishing URL Detection Page
# ===============================
elif selected == "Phishing URL Detection":
    st.header("🔗 Phishing URL Detection")
    # Lottie Animation
    lottie_ai = load_local_lottie("assets/lottie/phishing.json")
    if lottie_ai:
        st_lottie(lottie_ai, height=300)
    else:
        st.write("🎬 Animation not available")

    url_input = st.text_input("Enter a URL:")

    if st.button("Check URL"):
        if url_input.strip() != "":
            # Animated progress bar
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress.progress(i+1)

            _, _, verdict = phishing_detector(url_input)

            # Final Verdict Card
            if "Safe" in verdict:
                st.success(f"✅ {url_input} is Safe! Always stay cautious online.")
            elif "Suspicious" in verdict:
                st.warning(f"⚠ {url_input} is Suspicious! Avoid sharing sensitive info.")
            else:
                st.error(f"❌ {url_input} is Phishing! Do NOT visit this site.")

            # Save to history
            st.session_state.url_history.insert(0, {"url": url_input, "verdict": verdict})
            if len(st.session_state.url_history) > 5:
                st.session_state.url_history.pop()

    # Display URL history as cards
    if st.session_state.url_history:
        st.subheader("📜 Recent URL Checks")
        for item in st.session_state.url_history:
            color = "#2f7a2e" if "Safe" in item['verdict'] else "#ff9900" if "Suspicious" in item['verdict'] else "#ff3333"
            st.markdown(f"""
            <div style='border:1px solid {color}; border-radius:10px; padding:10px; margin-bottom:10px;
                        background-color:#f0f9f0'>
                <b>URL:</b> {item['url']} <br>
                <b>Verdict:</b> <span style='color:{color};'>{item['verdict']}</span>
            </div>
            """, unsafe_allow_html=True)

# ===============================
# About Page
# ===============================
elif selected == "Notice":
    st.header("Cyber Awareness")

    st.markdown("""
### Cyber Awareness and Hygiene  

#### 1. For Parents
- *Talk & Monitor*: Discuss online threats (grooming, bullying, stalking) with children and monitor their online activity. Set clear internet and game usage guidelines.  
- *Watch Behavior Changes*: Defensive or secretive behavior may indicate cyber grooming. Engage children in offline activities.  
- *Protect Against Grooming*: Explain responsible social media use and ensure strong privacy settings.  
- *Avoid Suspicious Links*: Do not click unknown links or attachments to prevent malware infection.  
- *Cover Webcams*: Protect against unauthorized observation by covering webcams when not in use.  
- *Install Security Software*: Use antivirus and parental control software. Review social media privacy settings.  
- *Update Software*: Regularly update OS and applications to patch vulnerabilities. Download apps from trusted sources only.  
- *Secure Browsing*: Use updated browsers and safe browsing tools to prevent attacks.  

#### 2. For Teens and Young Adults
- *Secure Online Presence*: Use proper privacy settings on social media; share content only with trusted contacts.  
- *Friend Requests & Blocking*: Accept requests carefully, know how to block or remove uncomfortable contacts.  
- *Logout & Passwords*: Always log out and secure devices with passwords.  
- *Fake Accounts*: Report impersonation to social media providers immediately.  
- *Video & Chat Safety*: Be cautious on video calls; private chats can be recorded. Avoid taking sensitive photos/videos on cloud-connected devices.  
- *Cyber Stalking Protection*: Disable location services, avoid sharing personal info, and consult trusted people if targeted.  
- *Sensitive Browsing*: Access banking or shopping sites only from personal, secure devices or networks.  
- *Device Security*: Use passwords/PINs, install apps from trusted sources, erase private data before servicing or selling devices.  

#### 3. For Organizations
- *HR Policies*: Implement clear rules for handling CP/CSAM or sexually explicit material.  
- *Device Usage*: Define proper use of organizational devices.  
- *Investigation & Reporting*: Investigate and act against employees found possessing obscene content. Report incidents to police and preserve evidence securely.  
- *Legal Compliance*: Publishing, collecting, or distributing CP/CSAM is illegal under Sections 67, 67A, and 67B of the IT Act, 2000.  

*Key Takeaway:* Be vigilant, follow safe practices online, and report any illegal or suspicious activity. *Be Safe, Browse Safe!*
    """)

    st.header("Awareness regarding OTP usage")
    st.markdown("""
- ⚠ *Never share your OTP* with anyone – not even with us. We will never ask for your OTP over call, SMS, or email.  
- 🛡 *Protect your account*: OTPs are private keys. If someone asks for your OTP, it’s a scam. Report suspicious activity immediately.  
- 🚨 *Warning*: Fraudsters may trick you into sharing OTPs. Remember: Genuine organizations never ask for OTPs outside the app. Stay alert, stay safe.  
- 🔒 *Your OTP = Your Digital Identity*. Keep it safe. Together, let’s stop OTP fraud and protect our community.  
- 💡 *Did you know?* Most online frauds start with OTP sharing. Never share your OTP. If in doubt, report it instantly.  

*Reference:*  
[A Handbook for Students on Cyber Safety]  

*Download the Cyber Dost – Awareness Document*  
Published by:  
Ministry of Home Affairs, Government of India  
    """)

    # PDF download button
    with open("Cyber-security-tips-by-cyber-dost.pdf", "rb") as pdf_file:
        st.download_button(
            label="📥 Click here to download",
            data=pdf_file,
            file_name="Cyber-security-tips-by-cyber-dost.pdf",
            mime="application/pdf"
        )

    

elif selected == "Report Now":
    st.header("Register or Track Complaints")

    # Link to official cybercrime website
    st.markdown(
        "[Access the official Cyber Crime website](https://cybercrime.gov.in/) to register complaints and track them",
        unsafe_allow_html=True
    )

    # Helpline numbers
    st.markdown("""
*To report cyber crimes, you can use the following helpline numbers:*

- *1930*: Toll-free number for reporting financial frauds and cyber crimes.  
- *155260*: Operational from 09:00 AM to 06:00 PM for reporting cyber crime complaints.  
""")

    
else:
    st.header("About Sentinel")
    st.markdown("""
        Sentinel is an AI-powered platform that detects Fake News and Phishing URLs in real-time.  
        Built with Python, Streamlit, Google Gemini AI, Selenium, and web scraping.  
        Stay safe online by verifying news and checking suspicious URLs before clicking!
    """)
    image = Image.open("assets/hero_image.jpg")

    st.image(image, width=200)
