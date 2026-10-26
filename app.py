import streamlit as st
from pathlib import Path
import sys
import re
import json
import csv
import io
import time
import base64
from pypdf import PdfReader


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "cybersecurity_logo.png"

if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as logo_file:
        LOGO_BASE64 = base64.b64encode(logo_file.read()).decode("utf-8")
else:
    LOGO_BASE64 = ""

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# BACKEND MODULES
# ============================================================

from rag import build_rag_context
import gemini_llm


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CyberIncident AI",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FRONTEND CSS (Vibrant Button & High-Contrast Box Text)
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   MAIN BACKGROUND
   ============================================================ */

.stApp {
    background:
        radial-gradient(
            circle at 85% 8%,
            rgba(37, 126, 245, 0.28),
            transparent 27%
        ),
        radial-gradient(
            circle at 8% 42%,
            rgba(92, 182, 255, 0.20),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #ffffff 0%,
            #f4faff 25%,
            #e3f2ff 55%,
            #c9e5ff 100%
        );
    color: #0b2238;
}


/* ============================================================
   SUBTLE CYBER GRID
   ============================================================ */

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    right: 0;
    width: 500px;
    height: 500px;
    pointer-events: none;
    opacity: 0.32;
    background-image:
        linear-gradient(
            rgba(23, 105, 224, 0.10) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(23, 105, 224, 0.10) 1px,
            transparent 1px
        );
    background-size: 35px 35px;
    mask-image:
        radial-gradient(
            circle,
            black 0%,
            transparent 72%
        );
    z-index: 0;
}


/* ============================================================
   MAIN CONTAINER (Balanced width 1280px, centered)
   ============================================================ */

.block-container {
    max-width: 1280px !important;
    margin: 0 auto !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    position: relative;
    z-index: 1;
}


/* ============================================================
   FONT
   ============================================================ */

html,
body,
[class*="css"] {
    font-family:
        "Segoe UI",
        "Inter",
        Arial,
        sans-serif;
}


/* ============================================================
   HIDE STREAMLIT DEFAULT UI
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

header {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   HERO
   ============================================================ */

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    margin-top: 15px;
    margin-bottom: 12px;
    border-radius: 30px;
    background: rgba(23, 105, 224, 0.12);
    border: 1px solid #9ec6f5;
    color: #0b59b0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}


.hero-title {
    font-size: 48px !important;
    font-weight: 850 !important;
    line-height: 1.1 !important;
    letter-spacing: -1.5px;
    color: #092f63 !important;
    margin-top: 5px !important;
    margin-bottom: 8px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px;
    white-space: nowrap;
}


.hero-title span {
    color: #0066ff !important;
}


/* ============================================================
   SECTION HEADINGS
   ============================================================ */

h1 {
    color: #0b2f5f !important;
    font-weight: 850 !important;
}


h2 {
    color: #103f73 !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    margin-top: 1.8rem !important;
}


h3 {
    color: #174f85 !important;
    font-size: 21px !important;
    font-weight: 750 !important;
}


/* ============================================================
   NORMAL TEXT & INPUTS (High Contrast & Clear Readability)
   ============================================================ */

.stApp p {
    color: #163654;
}

[data-testid="stTextArea"] {
    background: rgba(255,255,255,0.98) !important;
    border: 1px solid #8abff5 !important;
    border-radius: 18px !important;
    box-shadow: 0 10px 28px rgba(25, 90, 145, 0.08);
}


textarea {
    background: #ffffff !important;
    color: #092642 !important;
    border-radius: 15px !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
    font-weight: 600 !important;
}


textarea::placeholder {
    color: #55789a !important;
}


/* ============================================================
   VIBRANT & ULTRA-VISIBLE ANALYZE BUTTON
   ============================================================ */

.stButton > button {
    width: 100%;
    min-height: 58px;
    border-radius: 14px;
    border: 2px solid rgba(255, 255, 255, 0.4) !important;
    background:
        linear-gradient(
            135deg,
            #0055ff,
            #0038b8
        ) !important;
    color: #ffffff !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
    box-shadow: 0 12px 32px rgba(0, 85, 255, 0.4);
    transition: all 0.2s ease;
}


.stButton > button:hover {
    transform: translateY(-2px);
    background:
        linear-gradient(
            135deg,
            #1a66ff,
            #002ca0
        ) !important;
    color: #ffffff !important;
    box-shadow: 0 15px 38px rgba(0, 85, 255, 0.5);
}


/* ============================================================
   CENTERED FOOTER STYLING
   ============================================================ */

.footer {
    text-align: center !important;
    color: #3b6185 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    margin-top: 3rem !important;
    margin-bottom: 1.5rem !important;
    width: 100% !important;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# BRANDED NAVIGATION BAR
# ============================================================

st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"]:has(.app-brand){
      background:rgba(255,255,255,.96);border:1px solid #d6e8fb;border-radius:20px;
      padding:10px 22px;margin:0 auto 28px;box-shadow:0 8px 24px rgba(31,100,170,.09);
      align-items:center;gap:14px;max-width:1280px !important;
    }
    .app-brand{display:flex !important;flex-direction:row !important;align-items:center !important;gap:12px;padding:0;margin:0;min-width:0;white-space:nowrap}
    .app-brand-logo{width:48px;height:48px;object-fit:contain;background:transparent !important;border-radius:0 !important;padding:0 !important;border:0 !important;box-shadow:none !important;flex:0 0 48px}
    .app-brand-copy{display:flex;flex-direction:column;justify-content:center;min-width:0}
    .app-brand-title{font-size:24px;line-height:1.08;font-weight:850;color:#092f63;white-space:nowrap}
    .app-brand-title span{color:#0055ff}
    .app-brand-subtitle{font-size:10px;color:#3b6185;margin-top:4px;white-space:nowrap;letter-spacing:.2px}
    div[data-testid="stRadio"]{margin:0 !important}
    div[data-testid="stRadio"] > label{display:none !important}
    div[data-testid="stRadio"] > div{gap:8px;align-items:center;flex-wrap:nowrap}
    div[data-testid="stRadio"] [role="radiogroup"]{gap:8px}
    div[data-testid="stRadio"] label{background:#f8fbff;border:1px solid #d7e8f9;border-radius:12px;padding:10px 12px;min-height:44px;white-space:nowrap;margin:0 !important;transition:all .18s ease;box-shadow:0 2px 5px rgba(30,100,170,.025)}
    div[data-testid="stRadio"] label:hover{border-color:#83bdff;background:#eef7ff}
    div[data-testid="stRadio"] label p{font-size:13px !important;font-weight:750;color:#0c305c;margin:0}
    div[data-testid="stRadio"] label:has(input:checked){background:#0055ff;border-color:#0055ff}
    div[data-testid="stRadio"] label:has(input:checked) p{color:white !important}
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.pop("navigate_to_upload", False):
    st.session_state["main_navigation"] = "Upload Incident"

nav_brand_col, nav_links_col = st.columns([1.35, 2.05], gap="small")
with nav_brand_col:
    if LOGO_BASE64:
        logo_html = f'<img class="app-brand-logo" src="data:image/png;base64,{LOGO_BASE64}" alt="CyberIncident AI logo">'
    else:
        logo_html = '<div class="app-brand-logo" style="display:flex;align-items:center;justify-content:center;font-size:32px">🔐</div>'
    st.markdown(
        '<div class="app-brand">' + logo_html + '<div class="app-brand-copy"><div class="app-brand-title">Cyber<span>Incident AI</span></div><div class="app-brand-subtitle">CYBERSECURITY INCIDENT ANALYSIS SYSTEM</div></div></div>',
        unsafe_allow_html=True
    )
with nav_links_col:
    nav_icons = {
        "Home": "🏠  Home",
        "Upload Incident": "📤  Upload Incident",
        "Analysis Results": "📊  Analysis Results",
        "Evaluation": "📈  Evaluation",
    }
    page = st.radio(
        "Main navigation",
        ["Home", "Upload Incident", "Analysis Results", "Evaluation"],
        format_func=lambda value: nav_icons[value],
        horizontal=True,
        key="main_navigation",
        label_visibility="collapsed"
    )

incident_text = st.session_state.get("last_incident_text", "")
analyze = False


# ============================================================
# ATTACK CLASSIFICATION & DETECTION
# ============================================================

ATTACK_PATTERNS = [
    ("Ransomware Attack", ["ransomware", "ransom note", "files were encrypted", "files encrypted", "data encrypted", "encrypted files", "crypto locker", "cryptolocker", "demanded ransom", "ransom demand"]),
    ("Spear Phishing Attack", ["spear phishing", "targeted phishing", "targeted email attack"]),
    ("Phishing Attack", ["phishing", "phishing email", "fake login page", "fake login website", "fake website", "malicious email", "suspicious email", "credential harvesting", "credential theft", "deceptive email"]),
    ("SQL Injection", ["sql injection", "sql attack", "sql payload", "union select", "database injection", "malicious sql statement"]),
    ("Cross-Site Scripting (XSS)", ["cross-site scripting", "cross site scripting", "xss attack", "xss payload", "javascript payload"]),
    ("DDoS Attack", ["ddos", "distributed denial of service", "distributed denial-of-service", "traffic flood", "network flood", "application flood", "overwhelming traffic"]),
    ("DoS Attack", ["denial of service", "denial-of-service", "dos attack", "service unavailable", "service disruption"]),
    ("Brute Force Attack", ["brute force", "brute-force", "multiple failed login", "multiple failed logins", "repeated failed login", "repeated failed logins", "repeated login attempts", "repeated authentication attempts", "password guessing", "credential guessing", "many failed authentication attempts"]),
    ("Credential Stuffing Attack", ["credential stuffing", "stolen credentials", "reused credentials", "credential reuse", "login attempts using stolen credentials"]),
    ("Password Spraying Attack", ["password spraying", "password spray", "password spray attack"]),
    ("Malware Attack", ["malware", "malicious software", "malicious executable", "malicious file", "malware infection", "infected system", "infected workstation", "malicious program"]),
    ("Trojan Attack", ["trojan", "trojan horse"]),
    ("Spyware Attack", ["spyware", "keylogger", "key logging", "keystroke logging"]),
    ("Worm Attack", ["computer worm", "network worm", "worm infection"]),
    ("Command Injection", ["command injection", "os command injection", "shell injection", "arbitrary command execution"]),
    ("Privilege Escalation", ["privilege escalation", "elevated privileges", "administrator privileges", "admin privileges", "unauthorized privilege"]),
    ("Data Exfiltration", ["data exfiltration", "data theft", "stolen data", "sensitive data transferred", "unauthorized data transfer", "data was transferred"]),
    ("Man-in-the-Middle Attack", ["man-in-the-middle", "man in the middle", "mitm attack", "traffic interception", "intercepted communication"]),
    ("Port Scanning", ["port scan", "port scanning", "scanned multiple ports", "open port discovery", "network reconnaissance"]),
    ("Account Takeover", ["account takeover", "account compromised", "compromised account", "unauthorized account access", "attacker accessed the account"]),
    ("Insider Threat", ["insider threat", "malicious employee", "employee misuse", "unauthorized employee activity"]),
    ("DNS Attack", ["dns attack", "dns poisoning", "dns spoofing", "dns hijacking"]),
    ("ARP Spoofing", ["arp spoofing", "arp poisoning", "arp attack"]),
    ("IP Spoofing", ["ip spoofing", "spoofed ip", "spoofed source ip"]),
    ("Session Hijacking", ["session hijacking", "session takeover", "stolen session", "session token theft"]),
    ("Web Shell Attack", ["web shell", "webshell", "web shell attack"]),
    ("Supply Chain Attack", ["supply chain attack", "compromised dependency", "malicious dependency", "third party compromise"])
]

def detect_attack_type(incident_text, extracted_attack_types=None):
    text = incident_text.lower()
    matches = []
    for attack_name, keywords in ATTACK_PATTERNS:
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            matches.append((score, attack_name))
    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1]
    if extracted_attack_types:
        for value in extracted_attack_types:
            value = str(value).strip()
            if value:
                return value.title()
    return "Security Incident"

def detect_severity(incident_text, extracted_severities=None):
    text = incident_text.lower()
    if re.search(r"\bcritical\b", text): return "CRITICAL"
    if re.search(r"\bhigh\b", text): return "HIGH"
    if re.search(r"\bmedium\b", text): return "MEDIUM"
    if re.search(r"\blow\b", text): return "LOW"
    if extracted_severities:
        val = str(extracted_severities[0]).strip().upper()
        if val in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]: return val
    return "Not Specified"

SYSTEM_PATTERNS = [
    (r"\bvpn server\b", "VPN Server"), (r"\bemail server\b", "Email Server"),
    (r"\bweb server\b", "Web Server"), (r"\bdatabase\b", "Database"),
    (r"\bfile server\b", "File Server"), (r"\bcloud server\b", "Cloud Server"),
    (r"\bfirewall\b", "Firewall"), (r"\bserver\b", "Server")
]

def detect_affected_system(incident_text, extracted_systems):
    text = incident_text.lower()
    for pattern, name in SYSTEM_PATTERNS:
        if re.search(pattern, text): return name
    if extracted_systems:
        return str(extracted_systems[0]).strip().title()
    return "Not Specified"

def extract_ips(text):
    ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    valid = []
    for ip in ips:
        parts = ip.split(".")
        if len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts):
            if ip not in valid: valid.append(ip)
    return valid

def clean_indicators(indicators, incident_text):
    candidates = extract_ips(incident_text)
    for item in indicators:
        item = str(item).strip()
        if item and item.lower() not in ["ip", "indicator", "indicators"]:
            if item not in candidates: candidates.append(item)
    return candidates

def get_possible_impact(attack_type, affected_system):
    return f"Repeated authentication or unauthorized attempts against the {affected_system} may result in compromised access if successful."

def get_recommendations(attack_type, indicators):
    return [
        "Investigate the affected account and successful login activity.",
        "Block or monitor the suspicious source IP.",
        "Reset credentials for the affected account.",
        "Enable Multi-Factor Authentication (MFA).",
        "Review authentication logs for related attempts."
    ]

def create_summary(attack_type, affected_system, severity):
    return f"{attack_type} activity was identified involving the {affected_system}. The observed activity is classified as {severity} severity."


# ============================================================
# HOME PAGE
# ============================================================

if page == "Home":
    st.markdown(
        """
        <style>
        .home-badge{display:inline-block;padding:9px 16px;border-radius:24px;
          background:#d7eaff;border:1px solid #b7d9ff;color:#0758b7;
          font-size:13px;font-weight:800;letter-spacing:.55px;margin:0 0 18px}
        .home-title{color:#092f63;font-size:clamp(42px,4.5vw,61px);line-height:1.04;
          letter-spacing:-1.7px;font-weight:900;margin:0 0 12px}
        .home-title span{color:#0055ff}
        .home-subtitle{color:#345d87;font-size:25px;line-height:1.2;
          font-weight:850;letter-spacing:.1px;margin:0 0 13px}
        .home-description{color:#2e5379;font-size:19px;line-height:1.55;
          max-width:660px;margin:0 0 20px}
        .home-highlights{display:flex;gap:26px;flex-wrap:wrap;color:#2e5379;
          font-size:16px;font-weight:750;margin:18px 0 24px}
        .home-feature-card{box-sizing:border-box;height:100%;min-height:166px;text-align:center;
          background:rgba(255,255,255,.96);border:1px solid #d2e6fb;
          border-radius:18px;padding:16px 12px 14px;
          box-shadow:0 8px 20px rgba(40,105,171,.07)}
        .home-feature-icon{width:60px;height:60px;display:flex;align-items:center;
          justify-content:center;margin:0 auto 10px;border-radius:50%;
          background:#e0efff;color:#0055ff;font-size:29px}
        .home-feature-title{color:#0b3268;font-weight:850;font-size:17px;line-height:1.25;margin-bottom:6px}
        .home-feature-description{color:#2e5379;font-size:14px;line-height:1.4}
        </style>
        """,
        unsafe_allow_html=True
    )

    hero_left, hero_right = st.columns([1.1, 0.9], gap="large")

    with hero_left:
        st.markdown(
            """
            <div class="home-badge">🔐 AI-POWERED CYBERSECURITY ANALYSIS</div>
            <h1 class="home-title">Cyber<span>Incident AI</span></h1>
            <p class="home-subtitle">CYBERSECURITY INCIDENT ANALYSIS REPORT</p>
            <p class="home-description">
                Upload incident reports or enter incident details to get AI-assisted
                analysis, extracted entities, relevant cybersecurity knowledge,
                potential impact and recommended response actions.
            </p>
            <div class="home-highlights">
                <span>🛡️ Threat Detection</span>
                <span>🔎 Incident Analysis</span>
                <span>🧠 AI Intelligence</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Get Started  →", type="primary", key="home_get_started"):
            st.session_state["navigate_to_upload"] = True
            st.rerun()

    with hero_right:
        hero_image = ASSETS_DIR / "cybersecurity_hero.png"
        logo_image = ASSETS_DIR / "cybersecurity_logo.png"
        if hero_image.exists():
            st.image(str(hero_image))
        elif logo_image.exists():
            st.image(str(logo_image), width=360)
        else:
            st.markdown(
                """
                <div style="text-align:center;padding:80px 20px;color:#0a4b91;">
                  <div style="font-size:100px;">🛡️</div>
                  <h3>Cybersecurity Incident Analysis</h3>
                  <p>Detect • Analyze • Respond</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    feature_columns = st.columns(4, gap="small")
    features = [
        ("📄", "Incident Analysis", "AI-assisted analysis of unstructured incident reports."),
        ("👤", "Entity Extraction", "Identify key entities and security indicators using NER."),
        ("▤", "Knowledge Retrieval", "Retrieve relevant cybersecurity guidance from the knowledge base."),
        ("🛡️", "Actionable Insights", "Review potential impact and recommended response actions."),
    ]
    for column, (icon, title, description) in zip(feature_columns, features):
        with column:
            st.markdown(
                f"""
                <div class="home-feature-card">
                  <div class="home-feature-icon">{icon}</div>
                  <div class="home-feature-title">{title}</div>
                  <div class="home-feature-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# UPLOAD INCIDENT PAGE
# ============================================================

if page == "Upload Incident":
    st.markdown(
        """
        <div class="upload-page-heading">
            <div class="upload-heading-icon">▣</div>
            <div>
                <h2>Upload Incident</h2>
                <p>Upload a cybersecurity incident report or enter incident details to analyze.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .upload-page-heading {
            display:flex; align-items:center; gap:14px; margin:12px 0 22px;
        }
        .upload-heading-icon {
            width:48px; height:48px; display:flex; align-items:center;
            justify-content:center; border-radius:15px;
            background:linear-gradient(135deg,#e7f3ff,#c8e5ff);
            color:#0055ff; font-size:27px; font-weight:800;
            box-shadow:0 5px 16px rgba(27,116,224,.10);
        }
        .upload-page-heading h2 {
            color:#0c305c; font-size:30px; line-height:1.2;
            margin:0 0 5px; font-weight:800;
        }
        .upload-page-heading p { color:#2e5379; font-size:16px; margin:0; font-weight:600; }
        .st-key-upload_file_card, .st-key-upload_details_card {
            background:rgba(255,255,255,.98);
            border:1px solid #b8d7f8;
            border-radius:18px;
            padding:18px 16px 16px;
            min-height:340px;
            box-shadow:0 10px 28px rgba(38,113,191,.08);
        }
        .upload-panel-title {
            display:flex; align-items:center; gap:10px;
            color:#0c305c; font-size:17px; font-weight:800;
            margin:0 0 8px;
        }
        .upload-panel-subtitle {
            color:#3b6185; font-size:13.5px; line-height:1.5;
            margin-bottom:14px; font-weight:600;
        }
        .upload-drop-hint {
            text-align:center; padding:8px 8px 4px;
            color:#1e4468; font-size:13.5px; font-weight:700;
        }
        .upload-cloud { color:#0055ff; font-size:30px; line-height:1.25; }
        .upload-formats {
            color:#3b6185; font-size:12.5px; line-height:1.5; margin-top:10px; font-weight:600;
        }
        .or-divider {
            min-height:340px; display:flex; align-items:center;
            justify-content:center; color:#2e5379; font-size:14px;
        }
        .or-divider span {
            display:inline-flex; width:36px; height:36px; border-radius:50%;
            align-items:center; justify-content:center; background:#e1effd;
            border:1px solid #b2d5f7; color:#0c305c; font-weight:800;
        }
        div[data-testid="stFileUploader"] {
            background:#f4f9ff; border:1px dashed #0055ff;
            border-radius:12px; padding:8px;
        }
        div[data-testid="stTextArea"] textarea {
            min-height:180px !important; background:#ffffff !important;
            color:#0c305c !important; border:1px solid #8abff5 !important;
            border-radius:11px !important; font-size:14.5px !important;
            line-height:1.55 !important; font-weight:600 !important;
        }
        .upload-footer-note {
            color:#3b6185; font-size:12.5px; line-height:1.5; margin-top:8px; font-weight:600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    upload_col, divider_col, details_col = st.columns([1, 0.12, 1], gap="medium")
    uploaded_text = ""
    uploaded_file = None

    with upload_col:
        with st.container(key="upload_file_card"):
            st.markdown(
                """
                <div class="upload-panel-title">📄 Upload Incident Report</div>
                <div class="upload-panel-subtitle">
                    Choose a report file from your computer. The text will be extracted for analysis.
                </div>
                """,
                unsafe_allow_html=True
            )

            uploaded_file = st.file_uploader(
                "Upload a file",
                type=["pdf", "txt", "csv", "json", "log"],
                help="Supported formats: PDF, TXT, CSV, JSON and LOG.",
                key="incident_report_uploader",
                label_visibility="collapsed"
            )

            st.markdown(
                """
                <div class="upload-drop-hint">
                    <div class="upload-cloud">⇧</div>
                    <strong>Upload your incident report</strong><br>
                    Select a file using the Upload button above.
                </div>
                <div class="upload-formats">
                    Supported formats: PDF, TXT, CSV, JSON, LOG<br>
                    Upload a text-based PDF for best results.
                </div>
                """,
                unsafe_allow_html=True
            )

            if uploaded_file is not None:
                try:
                    file_name = uploaded_file.name.lower()
                    if file_name.endswith(".pdf"):
                        pdf_reader = PdfReader(uploaded_file)
                        pages = [pdf_page.extract_text() for pdf_page in pdf_reader.pages if pdf_page.extract_text()]
                        uploaded_text = "\n".join(pages)
                    elif file_name.endswith(".json"):
                        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                        try:
                            uploaded_text = json.dumps(json.loads(raw_text), indent=2)
                        except Exception:
                            uploaded_text = raw_text
                    else:
                        uploaded_text = uploaded_file.read().decode("utf-8", errors="ignore")

                    if uploaded_text.strip():
                        st.success(f"Uploaded: {uploaded_file.name}")
                    else:
                        st.warning("The file was uploaded, but no readable text was found.")
                except Exception as error:
                    st.error(f"Unable to read uploaded file: {error}")

    with divider_col:
        st.markdown('<div class="or-divider"><span>OR</span></div>', unsafe_allow_html=True)

    with details_col:
        with st.container(key="upload_details_card"):
            st.markdown(
                """
                <div class="upload-panel-title">📝 Enter Incident Details</div>
                <div class="upload-panel-subtitle">
                    Enter a brief description of the incident if you do not have a report file.
                </div>
                """,
                unsafe_allow_html=True
            )

            default_incident = uploaded_text or st.session_state.get("last_incident_text", "")
            incident_text = st.text_area(
                "Incident description",
                value=default_incident,
                height=175,
                max_chars=20000,
                placeholder=(
                    "Example:\n"
                    "Multiple failed login attempts were detected from an unknown IP address. "
                    "The activity was followed by a successful login to the VPN server. "
                    "This may indicate a brute force attack targeting an employee account."
                ),
                key="incident_details_input",
                label_visibility="collapsed"
            )

            st.markdown(
                '<div class="upload-footer-note">Include affected systems, timestamps, IP addresses, suspicious activity and known severity, if available.</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    _, button_col, _ = st.columns([1, 1, 1])

    with button_col:
        analyze = st.button(
            "🔎  Analyze Incident",
            type="primary",
            key="analyze_incident_button"
        )

    if analyze and not incident_text.strip():
        st.warning("Please upload a readable report or enter incident details before analyzing.")

    if analyze and incident_text.strip():
        st.session_state["last_incident_text"] = incident_text


# ============================================================
# ANALYSIS & RESULTS PAGE (RAG & GEMINI INTEGRATION)
# ============================================================

if analyze or (page in ("Analysis Results", "Evaluation") and st.session_state.get("analysis_ready", False)):
    analysis_start_time = time.perf_counter()

    if not incident_text.strip():
        st.warning("⚠️ Please enter or upload an incident report first.")
        st.stop()

    if analyze:
        st.session_state["last_incident_text"] = incident_text
        st.session_state["analysis_ready"] = False
        st.session_state.pop("detailed_analysis", None)

    if analyze or "rag_result" not in st.session_state:
        with st.spinner("🔍 Analyzing incident with RAG & Gemini AI..."):
            try:
                rag_result = build_rag_context(incident_text)
                st.session_state["rag_result"] = rag_result
                st.session_state["analysis_ready"] = True
            except Exception as error:
                st.session_state["analysis_ready"] = False
                st.error(f"RAG processing failed: {error}")
                st.stop()
    else:
        rag_result = st.session_state["rag_result"]

    entities = rag_result.get("entities", {})
    attack_types = list(dict.fromkeys(entities.get("ATTACK_TYPE", [])))
    severities = list(dict.fromkeys(entities.get("SEVERITY", [])))
    affected_systems = list(dict.fromkeys(entities.get("AFFECTED_SYSTEM", [])))
    raw_indicators = entities.get("INDICATORS", [])

    attack_type = detect_attack_type(incident_text, attack_types)
    severity = detect_severity(incident_text, severities)
    affected_system = detect_affected_system(incident_text, affected_systems)
    indicators = clean_indicators(raw_indicators, incident_text)

    if page == "Analysis Results":
        st.markdown("""
        <div class="results-page-title">📊 Analysis Results</div>
        <div class="results-page-subtitle">AI-generated analysis for the incident you provided.</div>
        """, unsafe_allow_html=True)

        summary = create_summary(attack_type, affected_system, severity)
        impact = get_possible_impact(attack_type, affected_system)
        recommendations = get_recommendations(attack_type, indicators)
        ip_addresses = extract_ips(incident_text)
        ip_text = ", ".join(ip_addresses) if ip_addresses else "Not detected"

        st.markdown("""
        <style>
        .results-page-title{font-size:32px;font-weight:850;color:#103d73;margin:3px 0 2px;letter-spacing:.2px}
        .results-page-subtitle{font-size:15px;color:#3b6185;margin-bottom:12px;font-weight:600}
        .result-card{height:100%;background:rgba(255,255,255,.98);border:1px solid #cfe3f8;
          border-radius:14px;padding:13px 15px;box-shadow:0 5px 14px rgba(35,100,170,.07);margin-bottom:8px}
        .result-card-label{font-size:14px;color:#3b6185;margin-bottom:7px;font-weight:700}
        .result-card-value{font-size:21px;line-height:1.25;color:#0c305c;font-weight:900;overflow-wrap:anywhere}
        .result-section-title{font-size:22px;color:#0c305c;font-weight:850;margin:13px 0 8px}
        .result-soft-panel{background:rgba(220,239,255,.85);border:1px solid #b6daf9;border-radius:12px;
          padding:14px 16px;color:#0c305c;font-size:16px;line-height:1.65;margin:6px 0 14px;font-weight:600}
        .result-detail-box{min-height:155px;background:rgba(255,255,255,.98);border:1px solid #cfe3f8;
          border-radius:14px;padding:14px 15px;box-shadow:0 5px 14px rgba(35,100,170,.06);margin-bottom:8px}
        .result-detail-title{color:#103d73;font-size:17px;font-weight:800;margin-bottom:10px}
        .result-detail-body{color:#0c305c;font-size:15px;line-height:1.55;font-weight:600}
        .result-impact-box{min-height:190px;background:linear-gradient(135deg,rgba(255,255,255,.99),rgba(235,246,255,.97));
          border:1px solid #bcdcf8;border-top:4px solid #ff9900;border-radius:14px;padding:16px 17px;
          box-shadow:0 7px 18px rgba(35,100,170,.08);margin-bottom:8px}
        .result-impact-title{font-size:16px;color:#103d73;font-weight:800;margin-bottom:9px}
        .result-impact-text{font-size:16px;color:#0c305c;line-height:1.65;font-weight:600}
        .result-recommendation{padding:7px 0;color:#0c305c;font-size:17px;line-height:1.6;border-bottom:1px solid rgba(190,216,240,.55);font-weight:600}
        .result-recommendation:last-child{border-bottom:0}
        </style>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([1.0, 1.25, 1.15, .85], gap="small")
        top_cards = [
            (c1, "🚨 Severity", severity),
            (c2, "🎯 Attack Type", attack_type),
            (c3, "🖥️ Affected System", affected_system),
            (c4, "🔎 Indicators", str(len(indicators) if isinstance(indicators, list) else (1 if indicators else 0))),
        ]
        for col, label, value in top_cards:
            with col:
                st.markdown(f'<div class="result-card"><div class="result-card-label">{label}</div><div class="result-card-value">{value}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="result-section-title">🧩 Extracted Information</div>', unsafe_allow_html=True)
        entity_col, indicator_col, impact_col = st.columns([1.0, 1.25, 1.15], gap="small")
        with entity_col:
            st.markdown('<div class="result-card"><div class="result-card-label">🌐 IP Address</div><div class="result-card-value" style="font-size:17px">' + ip_text + '</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="result-card"><div class="result-card-label">🖥️ Affected System</div><div class="result-card-value" style="font-size:17px">' + str(affected_system) + '</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="result-card"><div class="result-card-label">⚠️ Severity</div><div class="result-card-value" style="font-size:17px">' + str(severity) + '</div></div>', unsafe_allow_html=True)
        with indicator_col:
            indicator_items = indicators if isinstance(indicators, list) else ([indicators] if indicators else [])
            unique_indicators = []
            seen_indicators = set()
            for item in indicator_items:
                item_text = str(item).strip()
                if item_text and item_text.casefold() not in seen_indicators:
                    seen_indicators.add(item_text.casefold())
                    unique_indicators.append(item_text)
            indicator_html = "".join(f'<div class="result-recommendation">• {item}</div>' for item in unique_indicators)
            if not indicator_html:
                indicator_html = '<div class="result-detail-body">No specific security indicators detected.</div>'
            st.markdown(f'<div class="result-detail-box"><div class="result-detail-title">🛡️ Security Indicators</div><div class="result-detail-body">{indicator_html}</div></div>', unsafe_allow_html=True)
        with impact_col:
            st.markdown(f'<div class="result-impact-box"><div class="result-impact-title">⚠️ Possible Impact</div><div class="result-impact-text">{impact}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-detail-box" style="min-height:0;padding:13px 15px"><div class="result-detail-title">🧠 Attack Information</div><div class="result-detail-body"><b>Attack Type:</b> {attack_type}<br><br><b>Affected System:</b> {affected_system}<br><br><b>Severity:</b> {severity}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="result-section-title">📌 Incident Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-soft-panel">{summary}</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-section-title">✅ Recommended Actions</div>', unsafe_allow_html=True)
        for idx, recommendation in enumerate(recommendations, start=1):
            st.markdown(f'<div class="result-recommendation"><b>{idx}.</b> {recommendation}</div>', unsafe_allow_html=True)

    detailed_analysis = st.session_state.get("detailed_analysis", "")
    if not detailed_analysis and page == "Analysis Results":
        try:
            if hasattr(gemini_llm, "generate_incident_analysis"):
                detailed_analysis = gemini_llm.generate_incident_analysis(incident_text, rag_result)
                st.session_state["detailed_analysis"] = detailed_analysis
        except Exception:
            detailed_analysis = ""
    if detailed_analysis and page == "Analysis Results":
        with st.expander("✨ View Detailed AI Analysis"):
            st.markdown(detailed_analysis)

if analyze and st.session_state.get("analysis_ready", False):
    st.session_state["analysis_processing_time"] = time.perf_counter() - analysis_start_time

if analyze and page == "Upload Incident" and st.session_state.get("analysis_ready", False):
    st.success("Incident analyzed successfully. Open **Analysis Results** or **Evaluation** from the navigation bar.")

if page == "Analysis Results" and not st.session_state.get("analysis_ready", False):
    st.info("No analysis results yet. Open **Upload Incident**, enter or upload an incident report, and click **Analyze Incident**.")

if page == "Evaluation" and not st.session_state.get("analysis_ready", False):
    st.info("Evaluation will appear here after you analyze an incident from **Upload Incident**.")


# ============================================================
# EVALUATION & PERFORMANCE PAGE
# ============================================================

if page == "Evaluation" and st.session_state.get("analysis_ready", False) and "rag_result" in locals():
    try:
        retrieved = rag_result.get("retrieved_knowledge", []) if isinstance(rag_result, dict) else []
        entities = rag_result.get("entities", {}) if isinstance(rag_result, dict) else {}
        entity_categories = ["PERSON", "ORGANIZATION", "LOCATION", "ATTACK_TYPE", "SEVERITY", "AFFECTED_SYSTEM", "INDICATORS"]
        detected_by_category = {category: bool(entities.get(category, [])) for category in entity_categories}
        detected_categories = sum(detected_by_category.values())
        extraction_coverage = detected_categories / len(entity_categories) if entity_categories else 0.0
        similarity_scores = []
        for item in retrieved:
            if isinstance(item, dict):
                score = item.get("score", item.get("similarity"))
                try:
                    score = float(score)
                    if score >= 0:
                        similarity_scores.append(score)
                except (TypeError, ValueError):
                    pass
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        best_similarity = max(similarity_scores) if similarity_scores else 0.0
        indicator_items = indicators if isinstance(indicators, list) else ([indicators] if indicators else [])
        indicator_count = len({str(x).strip().casefold() for x in indicator_items if str(x).strip()})
        processing_time = float(st.session_state.get("analysis_processing_time", 0.0) or 0.0)

        st.markdown("""
        <style>
        .eval-heading{color:#103d73;font-size:32px;font-weight:850;margin:8px 0 4px}
        .eval-subtitle{color:#3b6185;font-size:15px;margin:0 0 18px;font-weight:600}
        .eval-card{height:100%;background:rgba(255,255,255,.96);border:1px solid #d3e6f8;border-top:4px solid #0055ff;
          border-radius:13px;padding:14px 14px;box-shadow:0 6px 18px rgba(35,100,170,.06);margin-bottom:12px}
        .eval-label{color:#3b6185;font-size:14px;margin-bottom:7px;font-weight:700}
        .eval-value{color:#0c305c;font-size:24px;font-weight:900;line-height:1.2;overflow-wrap:anywhere}
        .eval-panel{background:rgba(255,255,255,.94);border:1px solid #d3e6f8;border-radius:14px;padding:16px;margin:10px 0}
        .eval-panel-title{color:#103d73;font-size:21px;font-weight:800;margin-bottom:10px}
        .colour-chart{background:rgba(255,255,255,.96);border:1px solid #d3e6f8;border-radius:13px;padding:15px 16px;margin-top:10px;box-shadow:0 5px 14px rgba(35,100,170,.05)}
        .chart-row{margin:0 0 13px}
        .chart-row:last-child{margin-bottom:0}
        .chart-row-label{display:flex;justify-content:space-between;gap:10px;color:#0c305c;font-size:15px;font-weight:800;margin-bottom:6px}
        .chart-row-label span{color:#3b6185;font-size:14px;font-weight:700;white-space:nowrap}
        .chart-track{height:13px;background:#eaf2fb;border-radius:99px;overflow:hidden}
        .chart-fill{height:100%;border-radius:99px;min-width:0;transition:width .25s ease}
        </style>
        <div class="eval-heading">📊 Evaluation &amp; Performance</div>
        <div class="eval-subtitle">Live measurements from the incident currently analyzed. Classification accuracy and F1-score require labelled test data and are not inferred from one incident.</div>
        """, unsafe_allow_html=True)

        k1, k2, k3, k4 = st.columns(4, gap="small")
        for col, label, value in [
            (k1, "🎯 Detected Attack Type", str(attack_type)),
            (k2, "🧩 Entity Coverage", f"{extraction_coverage * 100:.1f}%"),
            (k3, "📚 Average RAG Similarity", f"{avg_similarity:.4f}" if similarity_scores else "N/A"),
            (k4, "🔎 Indicators Detected", str(indicator_count)),
        ]:
            with col:
                st.markdown(f'<div class="eval-card"><div class="eval-label">{label}</div><div class="eval-value">{value}</div></div>', unsafe_allow_html=True)

        left_panel, right_panel = st.columns([1.05, 1], gap="medium")
        with left_panel:
            st.markdown('<div class="eval-panel"><div class="eval-panel-title">🧩 Entity Detection</div></div>', unsafe_allow_html=True)
            st.caption(f"Detected entity categories: {detected_categories} of {len(entity_categories)}")
            st.progress(extraction_coverage, text=f"Entity coverage · {extraction_coverage * 100:.1f}%")
            category_colours = ["#2787F5", "#19B8A6", "#FFAD42", "#8B5CF6", "#F45B69", "#14A8D4", "#5B78E5"]
            entity_rows_html = []
            for idx, (name, found) in enumerate(detected_by_category.items()):
                pct = 100 if found else 0
                colour = category_colours[idx % len(category_colours)]
                status = "Detected" if found else "Not detected"
                entity_rows_html.append(
                    f'<div class="chart-row"><div class="chart-row-label">{name.replace("_", " ").title()}<span>{status}</span></div>'
                    f'<div class="chart-track"><div class="chart-fill" style="width:{pct}%;background:{colour};"></div></div></div>'
                )
            st.markdown('<div class="colour-chart">' + ''.join(entity_rows_html) + '</div>', unsafe_allow_html=True)
        with right_panel:
            st.markdown('<div class="eval-panel"><div class="eval-panel-title">📚 RAG Retrieval Evaluation</div></div>', unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            r1.metric("Retrieved Sources", len(retrieved))
            r2.metric("Average Similarity", f"{avg_similarity:.4f}" if similarity_scores else "N/A")
            r3.metric("Best Similarity", f"{best_similarity:.4f}" if similarity_scores else "N/A")
            if similarity_scores:
                rag_colours = ["#2787F5", "#19B8A6", "#8B5CF6", "#FFAD42", "#F45B69", "#14A8D4"]
                max_score = max(max(similarity_scores), 0.0001)
                rag_rows_html = []
                for idx, score in enumerate(similarity_scores, start=1):
                    width = max(0, min(100, (score / max_score) * 100))
                    colour = rag_colours[(idx - 1) % len(rag_colours)]
                    rag_rows_html.append(
                        f'<div class="chart-row"><div class="chart-row-label">Source {idx}<span>{score:.4f}</span></div>'
                        f'<div class="chart-track"><div class="chart-fill" style="width:{width:.2f}%;background:{colour};"></div></div></div>'
                    )
                st.markdown('<div class="colour-chart">' + ''.join(rag_rows_html) + '</div>', unsafe_allow_html=True)
            else:
                st.info("The retrieval pipeline did not return numeric similarity scores.")

        # Evaluation Details Table placed at the bottom
        st.markdown('<div class="eval-panel"><div class="eval-panel-title">📋 Evaluation Details</div></div>', unsafe_allow_html=True)
        metric_rows = [
            {"Metric": "Detected attack type", "Description": "Attack type reported for the current incident", "Value": str(attack_type)},
            {"Metric": "Entity categories detected", "Description": "Number of entity categories with at least one value", "Value": f"{detected_categories}/{len(entity_categories)}"},
            {"Metric": "Entity coverage", "Description": "Detected categories divided by the seven tracked categories", "Value": f"{extraction_coverage * 100:.1f}%"},
            {"Metric": "Security indicators", "Description": "Unique indicators found in the current incident", "Value": str(indicator_count)},
            {"Metric": "RAG sources retrieved", "Description": "Number of knowledge chunks returned by retrieval", "Value": str(len(retrieved))},
            {"Metric": "Average RAG similarity", "Description": "Mean of numeric retrieval scores returned by RAG", "Value": f"{avg_similarity:.4f}" if similarity_scores else "N/A"},
            {"Metric": "Analysis processing time", "Description": "Elapsed time recorded for the incident analysis", "Value": f"{processing_time:.2f} seconds"},
            {"Metric": "Classification accuracy / precision / recall / F1", "Description": "Requires a labelled test dataset with expected outputs; not measured from one incident", "Value": "Not measured"},
        ]
        st.markdown("<style>div[data-testid='stDataFrame']{font-size:15px} div[data-testid='stCaptionContainer'] p{font-size:14px !important}</style>", unsafe_allow_html=True)
        st.dataframe(metric_rows, width="stretch", hide_index=True)
        st.info("These live measurements describe this incident's extraction and retrieval. They are not benchmark accuracy scores. To calculate accuracy, precision, recall, or F1-score, evaluate a labelled set of incidents with known correct answers.")
    except Exception as evaluation_error:
        st.warning(f"Live evaluation could not be calculated: {evaluation_error}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    🔐 CyberIncident AI • AI-Powered Cybersecurity Incident Analysis
</div>
""",
    unsafe_allow_html=True
)