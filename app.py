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
# FRONTEND CSS
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

    color: #102a43;

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
   MAIN CONTAINER
   ============================================================ */

.block-container {

    max-width: 1200px;

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

    background: rgba(23, 105, 224, 0.10);

    border: 1px solid #b9d9f5;

    color: #155da8;

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

}

.hero-title {
    display: flex !important;
    align-items: center !important;
    gap: 10px;
    white-space: nowrap;
}

.title-logo {
    width: 95px;
    height: 95px;
    object-fit: contain;
    display: inline-block;
    flex-shrink: 0;
}


.hero-title span {

    color: #1769e0 !important;

}


.hero-description {

    max-width: 570px;

    color: #4d6d8c !important;

    font-size: 18px !important;

    line-height: 1.6;

    margin-bottom: 25px;

}


/* ============================================================
   HERO IMAGE PLACEHOLDER
   ============================================================ */

.image-placeholder {

    height: 300px;

    width: 100%;

    border-radius: 24px;

    background:

        radial-gradient(
            circle at 50% 35%,
            rgba(255,255,255,0.9),
            transparent 32%
        ),

        linear-gradient(
            145deg,
            #eaf6ff,
            #c5e4ff
        );

    border: 1px solid #afd4f2;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    box-shadow:

        0 16px 35px
        rgba(20,90,155,0.13);

}


.shield-icon {

    font-size: 62px;

    margin-bottom: 10px;

}


.placeholder-title {

    color: #155a9e;

    font-size: 19px;

    font-weight: 800;

}


.placeholder-subtitle {

    color: #5480a5;

    font-size: 14px;

    margin-top: 4px;

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


/* Section underline */

h2::after {

    content: "";

    display: block;

    width: 52px;

    height: 4px;

    margin-top: 8px;

    border-radius: 20px;

    background:

        linear-gradient(
            90deg,
            #1769e0,
            #65b9ff
        );

}


/* ============================================================
   NORMAL TEXT
   ============================================================ */

.stApp p {

    color: #506b84;

}


/* ============================================================
   INPUT AREA
   ============================================================ */

[data-testid="stTextArea"] {

    background:
        rgba(255,255,255,0.94) !important;

    border:
        1px solid #b9d8f2 !important;

    border-radius:
        18px !important;

    box-shadow:

        0 10px 28px
        rgba(25, 90, 145, 0.08);

}


textarea {

    background:
        #ffffff !important;

    color:
        #173b60 !important;

    border-radius:
        15px !important;

    font-size:
        15px !important;

    line-height:
        1.65 !important;

}


textarea::placeholder {

    color:
        #8aa4bd !important;

}


/* ============================================================
   FILE UPLOAD
   ============================================================ */

[data-testid="stFileUploader"] {

    background:
        rgba(255,255,255,0.92) !important;

    border:
        1px solid #b9d8f2 !important;

    border-radius:
        18px !important;

    padding:
        9px !important;

    box-shadow:

        0 9px 25px
        rgba(30, 90, 145, 0.07);

}


[data-testid="stFileUploaderDropzone"] {

    background:

        linear-gradient(
            135deg,
            #fbfdff,
            #edf7ff
        ) !important;

    border:
        1.5px dashed #78b6ed !important;

    border-radius:
        14px !important;

}


[data-testid="stFileUploaderDropzone"]:hover {

    background:
        #edf7ff !important;

    border-color:
        #1769e0 !important;

}


/* Upload button */

[data-testid="stFileUploader"] button {

    background:
        #ffffff !important;

    color:
        #155a9e !important;

    border:
        1px solid #b7d4ee !important;

    border-radius:
        9px !important;

}


[data-testid="stFileUploader"] button:hover {

    border-color:
        #1769e0 !important;

    color:
        #1769e0 !important;

}


/* ============================================================
   INPUT TEXT VISIBILITY FIX
   ============================================================ */

[data-testid="stTextArea"] textarea {
    color: #173b60 !important;
    -webkit-text-fill-color: #173b60 !important;
    background: #ffffff !important;
    opacity: 1 !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #8aa4bd !important;
    -webkit-text-fill-color: #8aa4bd !important;
    opacity: 1 !important;
}

/* Keep upload control white and readable */

[data-testid="stFileUploaderDropzone"] button {
    background: #ffffff !important;
    color: #155a9e !important;
    border: 1px solid #b7d4ee !important;
}

[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button span {
    color: #155a9e !important;
}

/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

.stButton > button {

    width: 100%;

    min-height: 55px;

    border-radius: 14px;

    border: none !important;

    background:

        linear-gradient(
            135deg,
            #0b83ff,
            #0757d8
        ) !important;

    color:
        #ffffff !important;

    font-size:
        15px !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.2px;

    box-shadow:

        0 11px 28px
        rgba(8, 91, 218, 0.28);

    transition:
        all 0.18s ease;

}


.stButton > button p {

    color:
        #ffffff !important;

}


.stButton > button span {

    color:
        #ffffff !important;

}


.stButton > button:hover {

    transform:
        translateY(-2px);

    background:

        linear-gradient(
            135deg,
            #1490ff,
            #0750c8
        ) !important;

    box-shadow:

        0 15px 32px
        rgba(8, 91, 218, 0.34);

}


/* ============================================================
   METRIC CARDS
   ============================================================ */

[data-testid="stMetric"] {

    position: relative;

    background:

        linear-gradient(
            145deg,
            #ffffff,
            #f2f9ff
        ) !important;

    border:
        1px solid #c4ddf3 !important;

    border-radius:
        18px !important;

    padding:
        20px !important;

    min-height:
        135px;

    box-shadow:

        0 10px 28px
        rgba(26, 83, 132, 0.09);

    overflow:
        hidden;

    transition:
        all 0.18s ease;

}


[data-testid="stMetric"]::before {

    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;

    height: 4px;

    background:

        linear-gradient(
            90deg,
            #1769e0,
            #67baff
        );

}


[data-testid="stMetric"]:hover {

    transform:
        translateY(-3px);

    box-shadow:

        0 15px 34px
        rgba(26, 83, 132, 0.13);

}


[data-testid="stMetricLabel"] {

    color:
        #607d98 !important;

    font-size:
        13px !important;

    font-weight:
        700 !important;

}


[data-testid="stMetricValue"] {

    color:
        #0c427b !important;

    font-size:
        20px !important;

    font-weight:
        850 !important;

    line-height:
        1.3 !important;

    white-space:
        normal !important;

    overflow-wrap:
        anywhere !important;

}


/* ============================================================
   BORDERED ENTITY CARDS
   ============================================================ */

div[data-testid="stVerticalBlockBorderWrapper"] {

    background:

        linear-gradient(
            145deg,
            #ffffff,
            #f6fbff
        ) !important;

    border:
        1px solid #c7def3 !important;

    border-radius:
        18px !important;

    box-shadow:

        0 9px 26px
        rgba(26, 83, 132, 0.07);

}


/* ============================================================
   ALERT BOXES
   ============================================================ */

[data-testid="stAlert"] {

    border-radius:
        15px !important;

    border:
        1px solid #c5ddf3 !important;

    box-shadow:

        0 7px 20px
        rgba(30, 75, 120, 0.06);

}


/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {

    background:
        rgba(255,255,255,0.92) !important;

    border:
        1px solid #c6def3 !important;

    border-radius:
        15px !important;

    box-shadow:

        0 7px 20px
        rgba(30, 75, 120, 0.06);

    margin-bottom:
        10px;

}


[data-testid="stExpander"] summary {

    color:
        #164f87 !important;

    font-weight:
        750 !important;

}

/* ============================================================
   RAG CONTEXT CODE BOX
   ============================================================ */

[data-testid="stCodeBlock"] {

    background: #0b1726 !important;

    border: 1px solid #284b6b !important;

    border-radius: 14px !important;

}


[data-testid="stCodeBlock"] pre {

    background: #0b1726 !important;

    color: #d9ecff !important;

    font-size: 13px !important;

    line-height: 1.6 !important;

}


[data-testid="stCodeBlock"] code {

    color: #d9ecff !important;

    background: transparent !important;

}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {

    text-align:
        center;

    color:
        #7891a9;

    font-size:
        12px;

    padding:
        18px 0 8px;

    margin-top:
        24px;

    border-top:
        1px solid #d7e7f5;

}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 800px) {

    .hero-title {

        font-size:
            34px !important;

    }

    .hero-section {

        padding:
            25px;

    }

    h2 {

        font-size:
            23px !important;

    }

    [data-testid="stMetricValue"] {

        font-size:
            18px !important;

    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# BRANDED NAVIGATION BAR (SHARED BY ALL PAGES)
# ============================================================

st.markdown(
    """
    <style>
    /* Shared one-row navigation bar: logo/title on the left, page links on the right */
    div[data-testid="stHorizontalBlock"]:has(.app-brand){
      background:rgba(255,255,255,.96);border:1px solid #d6e8fb;border-radius:20px;
      padding:10px 18px;margin:0 auto 24px;box-shadow:0 8px 24px rgba(31,100,170,.09);
      align-items:center;gap:14px;max-width:1180px;
    }
    .app-brand{display:flex !important;flex-direction:row !important;align-items:center !important;gap:12px;padding:0;margin:0;min-width:0;white-space:nowrap}
    .app-brand-logo{width:48px;height:48px;object-fit:contain;background:transparent !important;border-radius:0 !important;padding:0 !important;border:0 !important;box-shadow:none !important;flex:0 0 48px}
    .app-brand-copy{display:flex;flex-direction:column;justify-content:center;min-width:0}
    .app-brand-title{font-size:24px;line-height:1.08;font-weight:850;color:#092f63;white-space:nowrap}
    .app-brand-title span{color:#0875ed}
    .app-brand-subtitle{font-size:10px;color:#6886a6;margin-top:4px;white-space:nowrap;letter-spacing:.2px}
    div[data-testid="stRadio"]{margin:0 !important}
    div[data-testid="stRadio"] > label{display:none !important}
    div[data-testid="stRadio"] > div{gap:8px;align-items:center;flex-wrap:nowrap}
    div[data-testid="stRadio"] [role="radiogroup"]{gap:8px}
    div[data-testid="stRadio"] label{background:#f8fbff;border:1px solid #d7e8f9;border-radius:12px;padding:10px 12px;min-height:44px;white-space:nowrap;margin:0 !important;transition:all .18s ease;box-shadow:0 2px 5px rgba(30,100,170,.025)}
    div[data-testid="stRadio"] label:hover{border-color:#83bdff;background:#eef7ff}
    div[data-testid="stRadio"] label p{font-size:13px !important;font-weight:750;color:#123b70;margin:0}
    div[data-testid="stRadio"] label:has(input:checked){background:#0875ed;border-color:#0875ed}
    div[data-testid="stRadio"] label:has(input:checked) p{color:white !important}
    @media(max-width:1050px){.app-brand-title{font-size:20px}.app-brand-logo{width:40px;height:40px;flex-basis:40px}.app-brand-subtitle{font-size:9px}div[data-testid="stRadio"] label{padding:7px 7px}div[data-testid="stRadio"] label p{font-size:11px !important}}
    .eval-heading{color:#103d73;font-size:31px;font-weight:850;margin:8px 0 4px}
    .eval-subtitle{color:#6886a6;font-size:15px;margin:0 0 18px}
    div[data-testid="stMetric"]{background:rgba(255,255,255,.91);border:1px solid #d3e6f8;border-radius:14px;padding:15px 14px;box-shadow:0 6px 18px rgba(35,100,170,.06)}
    div[data-testid="stMetricLabel"]{color:#456b94;font-size:14px;font-weight:700}
    div[data-testid="stMetricValue"]{color:#103d73;font-size:27px;font-weight:850}
    .eval-note{background:#eef7ff;border:1px solid #cfe5fb;border-radius:12px;padding:12px 15px;color:#456b94;font-size:15px;margin:12px 0}
    </style>
    """,
    unsafe_allow_html=True
)

# Update navigation state before the radio widget is created.
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

# Keep the most recently submitted incident available when the user
# moves between pages. The analysis is not run again unless required.
incident_text = st.session_state.get("last_incident_text", "")
analyze = False


# ============================================================
# ATTACK CLASSIFICATION
# ============================================================

ATTACK_PATTERNS = [

    (
        "Ransomware Attack",
        [
            "ransomware",
            "ransom note",
            "files were encrypted",
            "files encrypted",
            "data encrypted",
            "encrypted files",
            "crypto locker",
            "cryptolocker",
            "demanded ransom",
            "ransom demand"
        ]
    ),

    (
        "Spear Phishing Attack",
        [
            "spear phishing",
            "targeted phishing",
            "targeted email attack"
        ]
    ),

    (
        "Phishing Attack",
        [
            "phishing",
            "phishing email",
            "fake login page",
            "fake login website",
            "fake website",
            "malicious email",
            "suspicious email",
            "credential harvesting",
            "credential theft",
            "deceptive email"
        ]
    ),

    (
        "SQL Injection",
        [
            "sql injection",
            "sql attack",
            "sql payload",
            "union select",
            "database injection",
            "malicious sql statement"
        ]
    ),

    (
        "Cross-Site Scripting (XSS)",
        [
            "cross-site scripting",
            "cross site scripting",
            "xss attack",
            "xss payload",
            "javascript payload"
        ]
    ),

    (
        "DDoS Attack",
        [
            "ddos",
            "distributed denial of service",
            "distributed denial-of-service",
            "traffic flood",
            "network flood",
            "application flood",
            "overwhelming traffic"
        ]
    ),

    (
        "DoS Attack",
        [
            "denial of service",
            "denial-of-service",
            "dos attack",
            "service unavailable",
            "service disruption"
        ]
    ),

    (
        "Brute Force Attack",
        [
            "brute force",
            "brute-force",
            "multiple failed login",
            "multiple failed logins",
            "repeated failed login",
            "repeated failed logins",
            "repeated login attempts",
            "repeated authentication attempts",
            "password guessing",
            "credential guessing",
            "many failed authentication attempts"
        ]
    ),

    (
        "Credential Stuffing Attack",
        [
            "credential stuffing",
            "stolen credentials",
            "reused credentials",
            "credential reuse",
            "login attempts using stolen credentials"
        ]
    ),

    (
        "Password Spraying Attack",
        [
            "password spraying",
            "password spray",
            "password spray attack"
        ]
    ),

    (
        "Malware Attack",
        [
            "malware",
            "malicious software",
            "malicious executable",
            "malicious file",
            "malware infection",
            "infected system",
            "infected workstation",
            "malicious program"
        ]
    ),

    (
        "Trojan Attack",
        [
            "trojan",
            "trojan horse"
        ]
    ),

    (
        "Spyware Attack",
        [
            "spyware",
            "keylogger",
            "key logging",
            "keystroke logging"
        ]
    ),

    (
        "Worm Attack",
        [
            "computer worm",
            "network worm",
            "worm infection"
        ]
    ),

    (
        "Command Injection",
        [
            "command injection",
            "os command injection",
            "shell injection",
            "arbitrary command execution"
        ]
    ),

    (
        "Privilege Escalation",
        [
            "privilege escalation",
            "elevated privileges",
            "administrator privileges",
            "admin privileges",
            "unauthorized privilege"
        ]
    ),

    (
        "Data Exfiltration",
        [
            "data exfiltration",
            "data theft",
            "stolen data",
            "sensitive data transferred",
            "unauthorized data transfer",
            "data was transferred"
        ]
    ),

    (
        "Man-in-the-Middle Attack",
        [
            "man-in-the-middle",
            "man in the middle",
            "mitm attack",
            "traffic interception",
            "intercepted communication"
        ]
    ),

    (
        "Port Scanning",
        [
            "port scan",
            "port scanning",
            "scanned multiple ports",
            "open port discovery",
            "network reconnaissance"
        ]
    ),

    (
        "Account Takeover",
        [
            "account takeover",
            "account compromised",
            "compromised account",
            "unauthorized account access",
            "attacker accessed the account"
        ]
    ),

    (
        "Insider Threat",
        [
            "insider threat",
            "malicious employee",
            "employee misuse",
            "unauthorized employee activity"
        ]
    ),

    (
        "DNS Attack",
        [
            "dns attack",
            "dns poisoning",
            "dns spoofing",
            "dns hijacking"
        ]
    ),

    (
        "ARP Spoofing",
        [
            "arp spoofing",
            "arp poisoning",
            "arp attack"
        ]
    ),

    (
        "IP Spoofing",
        [
            "ip spoofing",
            "spoofed ip",
            "spoofed source ip"
        ]
    ),

    (
        "Session Hijacking",
        [
            "session hijacking",
            "session takeover",
            "stolen session",
            "session token theft"
        ]
    ),

    (
        "Web Shell Attack",
        [
            "web shell",
            "webshell",
            "web shell attack"
        ]
    ),

    (
        "Supply Chain Attack",
        [
            "supply chain attack",
            "compromised dependency",
            "malicious dependency",
            "third party compromise"
        ]
    )
]


# ============================================================
# ATTACK DETECTION
# ============================================================

def detect_attack_type(
    incident_text,
    extracted_attack_types=None
):

    text = incident_text.lower()

    matches = []

    for attack_name, keywords in ATTACK_PATTERNS:

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        if score > 0:

            matches.append(
                (
                    score,
                    attack_name
                )
            )

    if matches:

        matches.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return matches[0][1]

    if extracted_attack_types:

        for value in extracted_attack_types:

            value = str(
                value
            ).strip()

            if not value:
                continue

            lower = value.lower()

            if "brute force" in lower:
                return "Brute Force Attack"

            if "phishing" in lower:
                return "Phishing Attack"

            if "ransomware" in lower:
                return "Ransomware Attack"

            if "malware" in lower:
                return "Malware Attack"

            if "sql injection" in lower:
                return "SQL Injection"

            if "ddos" in lower:
                return "DDoS Attack"

            if "denial of service" in lower:
                return "DoS Attack"

            return value.title()

    suspicious_terms = [

        "unauthorized access",
        "suspicious login",
        "suspicious activity",
        "security incident",
        "unauthorized activity",
        "compromised account",
        "malicious activity",
        "security breach",
        "cyber attack",
        "cyberattack",
        "intrusion"

    ]

    for term in suspicious_terms:

        if term in text:

            return "Suspicious / Unauthorized Activity"

    return "Security Incident"


# ============================================================
# SEVERITY
# ============================================================

def detect_severity(
    incident_text,
    extracted_severities=None
):

    text = incident_text.lower()

    severity_patterns = [

        (r"\bcritical severity\b", "CRITICAL"),
        (r"\bcritical\b", "CRITICAL"),

        (r"\bhigh severity\b", "HIGH"),
        (r"\bhigh\b", "HIGH"),

        (r"\bmedium severity\b", "MEDIUM"),
        (r"\bmedium\b", "MEDIUM"),

        (r"\blow severity\b", "LOW"),
        (r"\blow\b", "LOW")

    ]

    for pattern, value in severity_patterns:

        if re.search(
            pattern,
            text
        ):

            return value

    if extracted_severities:

        value = str(
            extracted_severities[0]
        ).strip().upper()

        if value in [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]:

            return value

    if any(
        phrase in text
        for phrase in [
            "ransomware",
            "data exfiltration",
            "data breach",
            "system compromise",
            "account takeover"
        ]
    ):

        return "HIGH"

    return "Not Specified"


# ============================================================
# AFFECTED SYSTEM
# ============================================================

SYSTEM_PATTERNS = [

    (r"\bvpn server\b", "VPN Server"),
    (r"\bvpn\b", "VPN Server"),

    (r"\bemail server\b", "Email Server"),
    (r"\bmail server\b", "Mail Server"),
    (r"\bemail system\b", "Email System"),

    (r"\bweb server\b", "Web Server"),
    (r"\bweb application\b", "Web Application"),
    (r"\bwebsite\b", "Web Application"),

    (r"\bcustomer database\b", "Database"),
    (r"\bdatabase server\b", "Database Server"),
    (r"\bdatabase\b", "Database"),

    (r"\bfile server\b", "File Server"),
    (r"\bfile system\b", "File System"),

    (r"\bcloud server\b", "Cloud Server"),
    (r"\bcloud system\b", "Cloud System"),

    (r"\bfirewall\b", "Firewall"),
    (r"\brouter\b", "Router"),
    (r"\bswitch\b", "Network Switch"),

    (r"\bworkstation\b", "Workstation"),
    (r"\bdesktop\b", "Workstation"),
    (r"\blaptop\b", "Laptop"),
    (r"\bcomputer\b", "Computer"),

    (r"\bendpoint\b", "Endpoint"),

    (r"\bapi\b", "API"),
    (r"\bserver\b", "Server"),
    (r"\bapplication\b", "Application"),
    (r"\bnetwork\b", "Network")
]


def detect_affected_system(
    incident_text,
    extracted_systems
):

    text = incident_text.lower()

    for pattern, name in SYSTEM_PATTERNS:

        if re.search(
            pattern,
            text
        ):

            return name

    if extracted_systems:

        value = str(
            extracted_systems[0]
        ).strip()

        if value:

            return value.title()

    return "Not Specified"


# ============================================================
# IP EXTRACTION
# ============================================================

def extract_ips(text):

    ips = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        text
    )

    valid = []

    for ip in ips:

        parts = ip.split(".")

        if len(parts) != 4:
            continue

        try:

            if all(
                0 <= int(part) <= 255
                for part in parts
            ):

                if ip not in valid:

                    valid.append(ip)

        except ValueError:

            continue

    return valid


# ============================================================
# PERSON / ORGANIZATION / LOCATION EXTRACTION
# ============================================================

def extract_named_entities(
    incident_text,
    entities
):

    text = incident_text.strip()

    def values_from(*keys):

        values = []

        for key in keys:

            value = entities.get(
                key,
                []
            )

            if isinstance(value, str):
                value = [value]

            if isinstance(value, list):

                for item in value:

                    item = str(item).strip()

                    if item and item not in values:
                        values.append(item)

        return values

    # --------------------------------------------------------
    # First use the NER output
    # --------------------------------------------------------

    persons = values_from(
        "PERSON",
        "PERSONS",
        "person",
        "persons"
    )

    organizations = values_from(
        "ORGANIZATION",
        "ORGANIZATIONS",
        "ORG",
        "ORGS",
        "organization",
        "organizations"
    )

    locations = values_from(
        "LOCATION",
        "LOCATIONS",
        "GPE",
        "location",
        "locations"
    )

    # --------------------------------------------------------
    # Safe fallback for common incident wording
    # --------------------------------------------------------

    if not persons:

        patterns = [
            r"\b(?:employee|user|victim|involving)\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"
            r"(?=\s+(?:at|from|in|of|was|confirmed|did)\b|[.,])",

            r"\b(?:employee|user|victim)\s+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )

            if match:

                candidate = match.group(1).strip()

                if candidate not in persons:
                    persons.append(candidate)

                break

    if not organizations:

        patterns = [
            r"\bat\s+"
            r"([A-Z][A-Za-z0-9&.-]+"
            r"(?:\s+[A-Z][A-Za-z0-9&.-]+){0,4})"
            r"(?=\s+(?:involving|from|where|"
            r"was|and|with)\b|[.,])",

            r"\b([A-Z][A-Za-z0-9&.-]+\s+"
            r"(?:Corporation|Corp|Company|"
            r"Technologies|Technology|Systems|"
            r"Solutions|Labs|Limited|Ltd|Inc))\b"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for candidate in matches:

                candidate = candidate.strip()

                if (
                    candidate
                    and candidate.lower()
                    not in {
                        "the security team",
                        "the company",
                        "the employee",
                        "the attacker"
                    }
                    and candidate not in organizations
                ):

                    organizations.append(candidate)

            if organizations:
                break

    if not locations:

        patterns = [
            r"\bunusual location in\s+"
            r"([A-Z][A-Za-z]+(?:,\s*[A-Z][A-Za-z]+)?)",

            r"\blocation\s+in\s+"
            r"([A-Z][A-Za-z]+(?:,\s*[A-Z][A-Za-z]+)?)",

            r"\b(?:from|in)\s+"
            r"([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)"
        ]

        invalid = {
            "Cloud",
            "VPN",
            "Email",
            "Multiple",
            "The",
            "HIGH",
            "NovaGrid",
            "Sarah"
        }

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for candidate in matches:

                candidate = candidate.strip()

                if (
                    candidate
                    and candidate not in invalid
                    and candidate not in locations
                ):

                    locations.append(candidate)

            if locations:
                break

    return {
        "PERSON": persons,
        "ORGANIZATION": organizations,
        "LOCATION": locations
    }


# ============================================================
# INDICATOR CLEANING
# ============================================================

def clean_indicators(
    indicators,
    incident_text
):

    candidates = []

    for ip in extract_ips(
        incident_text
    ):

        if ip not in candidates:

            candidates.append(ip)

    for item in indicators:

        item = str(
            item
        ).strip()

        if not item:
            continue

        lower = item.lower()

        if lower in [
            "ip",
            "ip address",
            "source ip",
            "source ip address",
            "indicator",
            "indicators"
        ]:

            continue

        if re.fullmatch(
            r"(?:\d{1,3}\.){3}\d{1,3}",
            item
        ):

            if item not in candidates:

                candidates.append(item)

            continue

        if not any(
            item.lower() == existing.lower()
            for existing in candidates
        ):

            candidates.append(item)

    unique = []

    for item in candidates:

        if not any(
            item.lower() == existing.lower()
            for existing in unique
        ):

            unique.append(item)

    final = []

    for item in unique:

        item_lower = item.lower().strip()

        redundant = False

        for other in unique:

            other_lower = other.lower().strip()

            if item_lower == other_lower:
                continue

            if (
                item_lower in other_lower
                and len(other_lower) > len(item_lower)
            ):

                redundant = True
                break

        if not redundant:

            final.append(item)

    return final


# ============================================================
# POSSIBLE IMPACT
# ============================================================

def get_possible_impact(
    attack_type,
    affected_system
):

    attack = attack_type.lower()

    if "brute force" in attack:

        return (
            f"Repeated authentication attempts against the "
            f"{affected_system} may result in unauthorized "
            "account access if successful."
        )

    if "phishing" in attack:

        return (
            "User credentials or sensitive information may have "
            "been exposed, potentially enabling unauthorized "
            "account access."
        )

    if "ransomware" in attack:

        return (
            "Systems or files may become unavailable due to "
            "encryption, potentially causing operational "
            "disruption and data loss."
        )

    if "sql injection" in attack:

        return (
            f"The {affected_system} may be exposed to unauthorized "
            "database access, modification, or data disclosure."
        )

    if "ddos" in attack or attack == "dos attack":

        return (
            f"The {affected_system} may experience service "
            "degradation or complete unavailability."
        )

    if "malware" in attack:

        return (
            "The affected system may experience unauthorized "
            "activity, data exposure, persistence, or further "
            "network compromise."
        )

    if "data exfiltration" in attack:

        return (
            "Sensitive organizational or user information may "
            "have been transferred to an unauthorized destination."
        )

    if "privilege escalation" in attack:

        return (
            "An attacker may gain elevated permissions and access "
            "resources beyond the originally compromised account."
        )

    if "account takeover" in attack:

        return (
            "The compromised account may be used for unauthorized "
            "access, data exposure, or additional malicious activity."
        )

    if "suspicious" in attack:

        return (
            "The observed activity may indicate unauthorized access "
            "or attempted compromise. Further investigation is "
            "required to determine the actual impact."
        )

    return (
        f"The incident may affect the {affected_system} through "
        "unauthorized access, disruption, data exposure, or "
        "additional malicious activity depending on the findings."
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

def get_recommendations(
    attack_type,
    indicators
):

    attack = attack_type.lower()

    if "brute force" in attack:

        return [

            "Investigate the affected account and successful login activity.",

            "Block or monitor the suspicious source IP.",

            "Reset credentials for the affected account.",

            "Enable Multi-Factor Authentication (MFA).",

            "Review authentication logs for related attempts."

        ]

    if "phishing" in attack:

        return [

            "Investigate the affected account and email activity.",

            "Reset potentially exposed credentials.",

            "Enable Multi-Factor Authentication (MFA).",

            "Block malicious links, domains, or sender addresses.",

            "Review authentication and email security logs."

        ]

    if "ransomware" in attack:

        return [

            "Isolate affected systems from the network.",

            "Preserve evidence and investigate the initial infection vector.",

            "Verify the integrity of available backups.",

            "Reset potentially compromised credentials.",

            "Monitor the environment for additional infected systems."

        ]

    if "sql injection" in attack:

        return [

            "Review and block malicious requests.",

            "Validate and sanitize application input.",

            "Use parameterized queries or prepared statements.",

            "Review database access logs.",

            "Investigate whether unauthorized data was accessed."

        ]

    if "ddos" in attack or attack == "dos attack":

        return [

            "Identify and filter malicious traffic sources.",

            "Enable appropriate network or application-level DDoS protection.",

            "Monitor traffic volume and affected services.",

            "Review firewall and network security logs.",

            "Verify service availability after mitigation."

        ]

    if "malware" in attack:

        return [

            "Isolate the affected endpoint or system.",

            "Identify and preserve the malicious file or process.",

            "Run endpoint security scans.",

            "Review network connections and persistence mechanisms.",

            "Monitor other systems for related activity."

        ]

    if "data exfiltration" in attack:

        return [

            "Identify the affected data and destination.",

            "Block unauthorized transfer channels.",

            "Review data access and network logs.",

            "Reset credentials if account compromise is suspected.",

            "Assess the scope of potentially exposed information."

        ]

    if "privilege escalation" in attack:

        return [

            "Investigate how elevated privileges were obtained.",

            "Review administrator and system authentication logs.",

            "Remove unauthorized privileges.",

            "Reset potentially compromised credentials.",

            "Check for additional unauthorized activity."

        ]

    return [

        "Investigate the affected system and user activity.",

        "Review relevant security and authentication logs.",

        "Preserve evidence for further investigation.",

        "Reset potentially compromised credentials.",

        "Continue monitoring for related activity."

    ]


# ============================================================
# INCIDENT SUMMARY
# ============================================================

def create_summary(
    attack_type,
    affected_system,
    severity
):

    attack = attack_type.lower()

    if "brute force" in attack:

        return (
            f"Repeated authentication activity was identified "
            f"against the {affected_system}. The observed activity "
            f"is consistent with a brute force attack and is "
            f"classified as {severity} severity."
        )

    if "phishing" in attack:

        return (
            f"Phishing-related activity was identified involving "
            f"the {affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "ransomware" in attack:

        return (
            f"Ransomware-related activity was identified affecting "
            f"the {affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "sql injection" in attack:

        return (
            f"SQL injection activity was identified against the "
            f"{affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    if "malware" in attack:

        return (
            f"Malware-related activity was identified on the "
            f"{affected_system}. The incident is classified as "
            f"{severity} severity."
        )

    return (
        f"{attack_type} activity was identified involving the "
        f"{affected_system}. The reported severity is "
        f"{severity}."
    )


# ============================================================
# FILE READER
# ============================================================

def read_uploaded_file(
    uploaded_file
):

    extension = Path(
        uploaded_file.name
    ).suffix.lower()

    raw = uploaded_file.read()

    if extension in [
        ".txt",
        ".log"
    ]:

        return raw.decode(
            "utf-8",
            errors="ignore"
        )

    if extension == ".json":

        try:

            data = json.loads(
                raw.decode(
                    "utf-8",
                    errors="ignore"
                )
            )

            return json.dumps(
                data,
                indent=2
            )

        except Exception:

            return raw.decode(
                "utf-8",
                errors="ignore"
            )

    if extension == ".csv":

        try:

            text = raw.decode(
                "utf-8",
                errors="ignore"
            )

            reader = csv.reader(
                io.StringIO(text)
            )

            rows = list(reader)

            return "\n".join(
                " | ".join(row)
                for row in rows
            )

        except Exception:

            return raw.decode(
                "utf-8",
                errors="ignore"
            )

    return raw.decode(
        "utf-8",
        errors="ignore"
    )


if page == "Home":
    hero_left, hero_right = st.columns([1.1, 0.9], gap="large")
    
    with hero_left:
        st.markdown('<div class="hero-badge">🔒 AI-POWERED CYBERSECURITY ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">Cyber<span>Incident AI</span></h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 16px; font-weight: 700; color: #335475; margin-bottom: 12px;">CYBERSECURITY INCIDENT ANALYSIS REPORT</p>', unsafe_allow_html=True)
        st.markdown('<p class="hero-description">Upload incident reports or enter incident details to get AI-assisted analysis, extracted entities, relevant cybersecurity knowledge, potential impact and recommended response actions.</p>', unsafe_allow_html=True)
        
        if st.button("Get Started →", type="primary", key="home_get_started"):
            st.session_state["navigate_to_upload"] = True
            st.rerun()

    with hero_right:
        hero_image = ASSETS_DIR / "cybersecurity_hero.png"
        if hero_image.exists():
            st.image(str(hero_image))  # Clean syntax compatible with modern Streamlit
        else:
            st.markdown("""
                <div class="image-placeholder">
                    <div class="shield-icon">🛡️</div>
                    <div class="placeholder-title">Cyber Incident Analysis</div>
                    <div class="placeholder-subtitle">Detect • Analyze • Respond</div>
                </div>
            """, unsafe_allow_html=True)

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



if page == "Upload Incident":
    # ============================================================
    # UPLOAD INCIDENT PAGE - INPUTS INSIDE THEIR CARDS
    # ============================================================

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
            color:#0875ee; font-size:27px; font-weight:800;
            box-shadow:0 5px 16px rgba(27,116,224,.10);
        }
        .upload-page-heading h2 {
            color:#103d73; font-size:30px; line-height:1.2;
            margin:0 0 5px; font-weight:800;
        }
        .upload-page-heading p { color:#6886a6; font-size:16px; margin:0; }

        /* The Streamlit containers themselves form the white cards.
           This keeps file uploader/text area/buttons INSIDE the cards. */
        .st-key-upload_file_card, .st-key-upload_details_card {
            background:rgba(255,255,255,.92);
            border:1px solid #cfe3f8;
            border-radius:18px;
            padding:16px 14px 14px;
            min-height:330px;
            box-shadow:0 10px 28px rgba(38,113,191,.07);
        }
        .upload-panel-title {
            display:flex; align-items:center; gap:10px;
            color:#103d73; font-size:16px; font-weight:750;
            margin:0 0 7px;
        }
        .upload-panel-subtitle {
            color:#6d89a7; font-size:13px; line-height:1.45;
            margin-bottom:12px;
        }
        .upload-drop-hint {
            text-align:center; padding:6px 8px 2px;
            color:#6583a4; font-size:13px;
        }
        .upload-cloud { color:#0875ee; font-size:29px; line-height:1.25; }
        .upload-formats {
            color:#6987a8; font-size:12px; line-height:1.45; margin-top:9px;
        }
        .or-divider {
            min-height:330px; display:flex; align-items:center;
            justify-content:center; color:#6c8aaa; font-size:14px;
        }
        .or-divider span {
            display:inline-flex; width:34px; height:34px; border-radius:50%;
            align-items:center; justify-content:center; background:#e1effd;
            border:1px solid #c5def7; color:#245b92; font-weight:700;
        }
        div[data-testid="stFileUploader"] {
            background:#f5faff; border:1px dashed #8bbfff;
            border-radius:12px; padding:7px;
        }
        div[data-testid="stFileUploader"] section { padding:6px !important; }
        div[data-testid="stTextArea"] textarea {
            min-height:170px !important; background:#fbfdff !important;
            color:#163f6b !important; border:1px solid #cbdff3 !important;
            border-radius:11px !important; font-size:14px !important;
            line-height:1.5 !important;
        }
        .upload-footer-note {
            color:#7993ae; font-size:12px; line-height:1.45; margin-top:7px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    upload_col, divider_col, details_col = st.columns([1, 0.12, 1], gap="medium")
    uploaded_text = ""
    uploaded_file = None

    with upload_col:
        # Use a real Streamlit container so the uploader is inside the card.
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
                        pages = [
                            pdf_page.extract_text()
                            for pdf_page in pdf_reader.pages
                            if pdf_page.extract_text()
                        ]
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
        # Text input and its heading share the same real Streamlit card.
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
    button_col_left, button_col, button_col_right = st.columns([1, 1, 1])

    with button_col:
        analyze = st.button(
            "🔎  Analyze Incident",
            type="primary",
            use_container_width=True,
            key="analyze_incident_button"
        )

    if analyze and not incident_text.strip():
        st.warning("Please upload a readable report or enter incident details before analyzing.")

    if analyze and incident_text.strip():
        st.session_state["last_incident_text"] = incident_text

# ============================================================
# ANALYSIS
# ============================================================

if analyze or (page in ("Analysis Results", "Evaluation") and st.session_state.get("analysis_ready", False)):
    analysis_start_time = time.perf_counter()

    if not incident_text.strip():

        st.warning(
            "⚠️ Please enter or upload an incident report first."
        )

        st.stop()

    if analyze:
        st.session_state["last_incident_text"] = incident_text
        st.session_state["analysis_ready"] = False
        st.session_state.pop("detailed_analysis", None)


    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    if analyze or "rag_result" not in st.session_state:

        with st.spinner(
            "🔍 Analyzing incident..."
        ):

            try:

                rag_result = build_rag_context(
                    incident_text
                )
                st.session_state["rag_result"] = rag_result
                st.session_state["analysis_ready"] = True

            except Exception as error:

                st.session_state["analysis_ready"] = False
                st.error(
                    f"RAG processing failed: {error}"
                )

                st.stop()

    else:

        rag_result = st.session_state["rag_result"]


    # ========================================================
    # ENTITIES
    # ========================================================

    entities = rag_result.get(
        "entities",
        {}
    )


    attack_types = list(
        dict.fromkeys(
            entities.get(
                "ATTACK_TYPE",
                []
            )
        )
    )


    severities = list(
        dict.fromkeys(
            entities.get(
                "SEVERITY",
                []
            )
        )
    )


    affected_systems = list(
        dict.fromkeys(
            entities.get(
                "AFFECTED_SYSTEM",
                []
            )
        )
    )


    raw_indicators = entities.get(
        "INDICATORS",
        []
    )


    # ========================================================
    # FINAL DETECTION
    # ========================================================

    attack_type = detect_attack_type(
        incident_text,
        attack_types
    )


    severity = detect_severity(
        incident_text,
        severities
    )


    affected_system = detect_affected_system(
        incident_text,
        affected_systems
    )


    indicators = clean_indicators(
        raw_indicators,
        incident_text
    )


    # ========================================================
    # PERSON / ORGANIZATION / LOCATION
    # ========================================================

    named_entities = extract_named_entities(
        incident_text,
        entities
    )

    persons = named_entities["PERSON"]
    organizations = named_entities["ORGANIZATION"]
    locations = named_entities["LOCATION"]


    person_text = (
        ", ".join(persons)
        if persons
        else "Not detected"
    )

    organization_text = (
        ", ".join(organizations)
        if organizations
        else "Not detected"
    )

    location_text = (
        ", ".join(locations)
        if locations
        else "Not detected"
    )


    # ========================================================
    if page == "Analysis Results":
        # Redesigned results page. Incident upload/input page is intentionally unchanged.
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
        .results-page-subtitle{font-size:15px;color:#6886a6;margin-bottom:12px}
        .result-card{height:100%;background:rgba(255,255,255,.95);border:1px solid #cfe3f8;
          border-radius:14px;padding:13px 15px;box-shadow:0 5px 14px rgba(35,100,170,.07);margin-bottom:8px}
        .result-card-label{font-size:14px;color:#57799b;margin-bottom:7px;font-weight:650}
        .result-card-value{font-size:21px;line-height:1.25;color:#234f7b;font-weight:850;overflow-wrap:anywhere}
        .result-section-title{font-size:22px;color:#103d73;font-weight:850;margin:13px 0 8px}
        .result-soft-panel{background:rgba(220,239,255,.75);border:1px solid #c6e1fb;border-radius:12px;
          padding:14px 16px;color:#42678b;font-size:16px;line-height:1.65;margin:6px 0 14px}
        .result-detail-box{min-height:155px;background:rgba(255,255,255,.95);border:1px solid #cfe3f8;
          border-radius:14px;padding:14px 15px;box-shadow:0 5px 14px rgba(35,100,170,.06);margin-bottom:8px}
        .result-detail-title{color:#315d88;font-size:17px;font-weight:800;margin-bottom:10px}
        .result-detail-body{color:#42678b;font-size:15px;line-height:1.55}
        .result-impact-box{min-height:190px;background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(235,246,255,.96));
          border:1px solid #bcdcf8;border-top:4px solid #ffad42;border-radius:14px;padding:16px 17px;
          box-shadow:0 7px 18px rgba(35,100,170,.08);margin-bottom:8px}
        .result-impact-title{font-size:16px;color:#315d88;font-weight:800;margin-bottom:9px}
        .result-impact-text{font-size:16px;color:#42678b;line-height:1.65}
        .result-recommendation{padding:7px 0;color:#42678b;font-size:17px;line-height:1.6;border-bottom:1px solid rgba(190,216,240,.55)}
        .result-recommendation:last-child{border-bottom:0}
        </style>
        """, unsafe_allow_html=True)

        # Top summary cards, matching the supplied dashboard mock-up.
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
        # Recommendations are shown directly without an extra empty coloured box.
        for idx, recommendation in enumerate(recommendations, start=1):
            st.markdown(f'<div class="result-recommendation"><b>{idx}.</b> {recommendation}</div>', unsafe_allow_html=True)

        # RAG panel: styled to match the supplied reference while preserving the
        # actual retrieved text and similarity scores from the existing pipeline.
        retrieved_results = rag_result.get("retrieved_knowledge", []) if isinstance(rag_result, dict) else []
        retrieved_results = retrieved_results if isinstance(retrieved_results, list) else []
        rag_rows = []
        for result in retrieved_results:
            if not isinstance(result, dict):
                continue
            raw_score = result.get("score", result.get("similarity", 0))
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                score = 0.0
            source_text = re.sub(r"={3,}", "", str(result.get("text", "")).strip()).strip()
            if source_text:
                rag_rows.append({"score": max(0.0, score), "text": source_text})

        rag_rows.sort(key=lambda item: item["score"], reverse=True)
        rag_scores = [item["score"] for item in rag_rows]
        rag_avg = sum(rag_scores) / len(rag_scores) if rag_scores else 0.0
        rag_best = max(rag_scores) if rag_scores else 0.0

        st.markdown("""
        <style>
        .rag-wrap{background:rgba(255,255,255,.72);border:1px solid #cfe4fa;border-radius:18px;
          padding:18px;margin:18px 0 12px;box-shadow:0 8px 24px rgba(34,108,180,.07)}
        .rag-heading{display:flex;align-items:center;gap:10px;color:#103d73;font-size:25px;font-weight:850;margin:0 0 2px}
        .rag-subheading{color:#6383a5;font-size:14px;margin:0 0 15px 42px}
        .rag-metric{height:100%;min-height:98px;background:#fff;border:1px solid #d4e7fa;border-radius:13px;
          padding:13px 14px;box-shadow:0 4px 12px rgba(35,100,170,.04)}
        .rag-metric-label{color:#5d7c9e;font-size:13px;font-weight:650;margin-bottom:6px}
        .rag-metric-value{color:#103d73;font-size:23px;font-weight:850;line-height:1.15}
        .rag-metric-note{color:#6e8ba9;font-size:12px;margin-top:5px}
        .rag-mini-track{height:8px;background:#e8f0fa;border-radius:99px;overflow:hidden;margin-top:9px}
        .rag-mini-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#2587ff,#55b9ff)}
        .rag-chart{height:100%;background:#fff;border:1px solid #d4e7fa;border-radius:13px;padding:14px 16px}
        .rag-chart-title{color:#103d73;font-size:16px;font-weight:800;margin-bottom:13px}
        .rag-chart-row{display:grid;grid-template-columns:62px 1fr 52px;align-items:center;gap:10px;margin:10px 0}
        .rag-chart-name{font-size:13px;color:#244f7d;font-weight:750}
        .rag-chart-track{height:12px;background:#e5eef8;border-radius:99px;overflow:hidden}
        .rag-chart-fill{height:100%;border-radius:99px}
        .rag-chart-score{text-align:right;color:#6482a2;font-size:12px;font-weight:700}
        .rag-source-card{height:100%;background:#fff;border:1px solid #d4e7fa;border-radius:15px;
          padding:13px;box-shadow:0 5px 14px rgba(35,100,170,.05);margin-top:12px}
        .rag-source-head{display:flex;align-items:center;gap:9px;margin-bottom:10px}
        .rag-source-icon{display:flex;align-items:center;justify-content:center;width:38px;height:38px;flex:0 0 38px;
          border-radius:50%;background:#e5f1ff;font-size:20px}
        .rag-source-name{font-size:15px;font-weight:850;color:#103d73}
        .rag-source-type{font-size:12px;color:#5d7c9e;margin-top:2px}
        .rag-score-pill{margin-left:auto;white-space:nowrap;background:#e8f3ff;border:1px solid #c6e2ff;
          border-radius:99px;padding:5px 8px;color:#0875ed;font-size:11px;font-weight:800}
        .rag-source-content{background:#f0f7ff;border:1px solid #d9eafb;border-radius:10px;padding:10px;
          color:#355b82;font-size:12.5px;line-height:1.5;overflow-wrap:anywhere}
        .rag-source-label{color:#0b4c8e;font-size:12px;font-weight:850;margin-bottom:4px}
        .rag-why{background:#e8fbf4;border:1px solid #c9f1e2;border-radius:10px;padding:10px;margin-top:8px;
          color:#326b61;font-size:12px;line-height:1.45}
        .rag-expand{margin-top:8px}
        .rag-disclaimer{background:#edf7ff;border:1px solid #d1e8fb;border-radius:10px;padding:9px 12px;
          color:#587a9d;font-size:12px;line-height:1.45;margin-top:10px}
        @media(max-width:900px){.rag-wrap{padding:12px}.rag-chart-row{grid-template-columns:52px 1fr 48px;gap:6px}.rag-source-card{padding:10px}}
        </style>
        <div class="rag-wrap">
          <div class="rag-heading">📚 RAG Retrieval Evaluation</div>
          <div class="rag-subheading">Relevant security guidance retrieved from the cybersecurity knowledge base.</div>
        </div>
        """, unsafe_allow_html=True)

        if rag_rows:
            metric_col, avg_col, best_col, chart_col = st.columns([.82, .95, .88, 1.7], gap="small")
            with metric_col:
                st.markdown(f'<div class="rag-metric"><div class="rag-metric-label">📄 Retrieved Sources</div><div class="rag-metric-value">{len(rag_rows)}</div><div class="rag-metric-note">knowledge passages</div></div>', unsafe_allow_html=True)
            with avg_col:
                avg_width = max(0, min(100, rag_avg * 100))
                st.markdown(f'<div class="rag-metric"><div class="rag-metric-label">⚙️ Average Similarity</div><div class="rag-metric-value">{rag_avg:.4f}</div><div class="rag-mini-track"><div class="rag-mini-fill" style="width:{avg_width:.1f}%"></div></div></div>', unsafe_allow_html=True)
            with best_col:
                best_width = max(0, min(100, rag_best * 100))
                st.markdown(f'<div class="rag-metric"><div class="rag-metric-label">🏆 Best Match</div><div class="rag-metric-value">{rag_best:.4f}</div><div class="rag-mini-track"><div class="rag-mini-fill" style="width:{best_width:.1f}%;background:linear-gradient(90deg,#8b5cf6,#b69cff)"></div></div></div>', unsafe_allow_html=True)
            with chart_col:
                palette = ["#3697f5", "#19bba9", "#8b5cf6", "#ffad42", "#f45b69", "#14a8d4"]
                max_score = max(rag_scores) if rag_scores else 0.0
                chart_html = '<div class="rag-chart"><div class="rag-chart-title">📊 Source Similarity Comparison</div>'
                for idx, item in enumerate(rag_rows):
                    width = (item["score"] / max_score * 100) if max_score > 0 else 0
                    colour = palette[idx % len(palette)]
                    chart_html += (f'<div class="rag-chart-row"><div class="rag-chart-name">Source {idx+1}</div>'
                                   f'<div class="rag-chart-track"><div class="rag-chart-fill" style="width:{width:.1f}%;background:{colour}"></div></div>'
                                   f'<div class="rag-chart-score">{item["score"]:.4f}</div></div>')
                chart_html += '</div>'
                st.markdown(chart_html, unsafe_allow_html=True)

            source_cols = st.columns(min(3, len(rag_rows)), gap="small")
            source_titles = ["Incident Response Guidance", "Authentication Monitoring", "Threat Mitigation Guidance"]
            source_icons = ["📄", "🟩", "📘"]
            for idx, item in enumerate(rag_rows):
                col = source_cols[idx % len(source_cols)]
                source_text = item["text"]
                # Keep cards readable while preserving the full actual retrieved passage in an expander.
                preview = source_text if len(source_text) <= 470 else source_text[:467].rsplit(" ", 1)[0] + "…"
                title = source_titles[idx] if idx < len(source_titles) else "Retrieved Security Guidance"
                icon = source_icons[idx] if idx < len(source_icons) else "📄"
                with col:
                    st.markdown(
                        f'<div class="rag-source-card"><div class="rag-source-head"><div class="rag-source-icon">{icon}</div>'
                        f'<div><div class="rag-source-name">Source {idx+1}</div><div class="rag-source-type">{title}</div></div>'
                        f'<div class="rag-score-pill">Similarity: {item["score"]:.4f}</div></div>'
                        f'<div class="rag-source-content"><div class="rag-source-label">📑 Retrieved Information</div>{preview}</div>'
                        f'<div class="rag-why"><b>💡 Why it matters</b><br>Retrieved because this passage matched the current incident query. Review the full passage to confirm its relevance to the incident.</div></div>',
                        unsafe_allow_html=True
                    )
                    with st.expander("View Retrieved Content"):
                        st.write(source_text)
            st.markdown('<div class="rag-disclaimer">ℹ️ Similarity scores show how closely a retrieved passage matches the incident query according to the retrieval model. Higher scores mean stronger similarity within this retrieval setup; they do not guarantee factual correctness.</div>', unsafe_allow_html=True)
        else:
            st.info("No matching cybersecurity knowledge was retrieved for this incident.")

        detailed_analysis = st.session_state.get("detailed_analysis", "")
        if not detailed_analysis:
            try:
                if hasattr(gemini_llm, "generate_incident_analysis"):
                    detailed_analysis = gemini_llm.generate_incident_analysis(incident_text, rag_result)
                    st.session_state["detailed_analysis"] = detailed_analysis
            except Exception:
                detailed_analysis = ""
        if detailed_analysis:
            with st.expander("✨ View Detailed AI Analysis"):
                st.markdown(detailed_analysis)

    # Save the elapsed analysis time after the first successful processing pass.
if analyze and st.session_state.get("analysis_ready", False):
    st.session_state["analysis_processing_time"] = (
        time.perf_counter() - analysis_start_time
    )

if analyze and page == "Upload Incident" and st.session_state.get("analysis_ready", False):
    st.success("Incident analyzed successfully. Open **Analysis Results** or **Evaluation** from the navigation bar.")

if page == "Analysis Results" and not st.session_state.get("analysis_ready", False):
    st.info("No analysis results yet. Open **Upload Incident**, enter or upload an incident report, and click **Analyze Incident**.")

if page == "Evaluation" and not st.session_state.get("analysis_ready", False):
    st.info("Evaluation will appear here after you analyze an incident from **Upload Incident**.")


# ============================================================
# LIVE INCIDENT EVALUATION & PERFORMANCE
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
        .eval-subtitle{color:#6886a6;font-size:15px;margin:0 0 18px}
        .eval-card{height:100%;background:rgba(255,255,255,.93);border:1px solid #d3e6f8;border-top:4px solid #328cff;
          border-radius:13px;padding:14px 14px;box-shadow:0 6px 18px rgba(35,100,170,.06);margin-bottom:12px}
        .eval-label{color:#58799b;font-size:14px;margin-bottom:7px}
        .eval-value{color:#234f7b;font-size:24px;font-weight:850;line-height:1.2;overflow-wrap:anywhere}
        .eval-panel{background:rgba(255,255,255,.91);border:1px solid #d3e6f8;border-radius:14px;padding:16px;margin:10px 0}
        .eval-panel-title{color:#103d73;font-size:21px;font-weight:800;margin-bottom:10px}
        .colour-chart{background:rgba(255,255,255,.94);border:1px solid #d3e6f8;border-radius:13px;padding:15px 16px;margin-top:10px;box-shadow:0 5px 14px rgba(35,100,170,.05)}
        .chart-row{margin:0 0 13px}
        .chart-row:last-child{margin-bottom:0}
        .chart-row-label{display:flex;justify-content:space-between;gap:10px;color:#315d88;font-size:15px;font-weight:700;margin-bottom:6px}
        .chart-row-label span{color:#6b86a3;font-size:14px;font-weight:600;white-space:nowrap}
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
            # Bright horizontal bars are used instead of the dark default Streamlit chart.
            # Bars show only the entity categories detected in this actual incident.
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
                st.caption("Bar lengths are scaled relative to the highest similarity score in this retrieval.")
            else:
                st.info("The retrieval pipeline did not return numeric similarity scores.")

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
        st.dataframe(metric_rows, use_container_width=True, hide_index=True)
        st.info("These live measurements describe this incident's extraction and retrieval. They are not benchmark accuracy scores. To calculate accuracy, precision, recall, or F1-score, evaluate a labelled set of incidents with known correct answers.")
    except Exception as evaluation_error:
        st.warning(f"Live evaluation could not be calculated: {evaluation_error}")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    🔐 CyberIncident AI
    • AI-Powered Cybersecurity Incident Analysis
</div>
""",
    unsafe_allow_html=True
)