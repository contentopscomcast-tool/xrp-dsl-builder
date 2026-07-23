"""
XRP Visual Rule Builder - A Streamlit application for building targeting rules visually.
"""

from typing import List, Tuple, Dict, Union
import re
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="XRP DSL Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== AUTH ====================

def _check_credentials(username: str, password: str) -> bool:
    """Validate username/password against st.secrets."""
    try:
        users = st.secrets["users"]
        return username in users and users[username] == password
    except Exception:
        return False


def _render_login_page() -> None:
    """Render the full-screen login page."""
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    * { font-family: inherit; }

    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"]   { display: none !important; }
    #MainMenu, footer                { display: none !important; }

    /* Full-bleed gradient backdrop */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main, .main > div {
        background: linear-gradient(135deg, #0f0c29 0%, #1e1b4b 25%, #312e81 55%, #4f46e5 80%, #6366f1 100%) !important;
        min-height: 100vh !important;
    }

    /* Animated orbs */
    [data-testid="stAppViewContainer"]::before,
    [data-testid="stAppViewContainer"]::after {
        content: ''; position: fixed; border-radius: 50%;
        filter: blur(90px); opacity: 0.3; pointer-events: none; z-index: 0;
        animation: floatOrb 9s ease-in-out infinite alternate;
    }
    [data-testid="stAppViewContainer"]::before {
        width: 560px; height: 560px;
        background: radial-gradient(circle, #818cf8, #4f46e5);
        top: -140px; left: -120px;
    }
    [data-testid="stAppViewContainer"]::after {
        width: 420px; height: 420px;
        background: radial-gradient(circle, #a78bfa, #7c3aed);
        bottom: -100px; right: -80px; animation-delay: -4.5s;
    }
    @keyframes floatOrb {
        0%   { transform: translate(0,0) scale(1); }
        100% { transform: translate(35px,45px) scale(1.1); }
    }

    .block-container {
        max-width: 980px !important;
        padding-top: 6vh !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
        position: relative; z-index: 1;
    }

    /* ── RIGHT PANEL / FORM ───────────────────────── */
    [data-testid="stForm"] {
        background: rgba(255,255,255,0.97) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 28px !important;
        padding: 2.8rem 2.6rem 2.2rem 2.6rem !important;
        box-shadow: 0 30px 70px rgba(0,0,0,0.45),
                    0 0 0 1px rgba(255,255,255,0.18),
                    inset 0 1px 0 rgba(255,255,255,0.9) !important;
        border: none !important;
    }
    [data-testid="stForm"] label {
        font-weight: 600 !important; font-size: 0.83rem !important;
        color: #374151 !important; letter-spacing: 0.2px !important;
    }
    [data-testid="stForm"] input[type="text"],
    [data-testid="stForm"] input[type="password"] {
        border: 1.5px solid #e2e8f0 !important; border-radius: 12px !important;
        padding: 0.68rem 0.95rem !important; font-size: 0.92rem !important;
        background: #f8fafc !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    [data-testid="stForm"] input[type="text"]:focus,
    [data-testid="stForm"] input[type="password"]:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3.5px rgba(99,102,241,0.18) !important;
        background: #fff !important;
    }
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] {
        margin-top: 1.3rem !important; position: relative !important;
    }
    [data-testid="stForm"] small,
    [data-testid="stForm"] .stFormSubmitButton ~ small,
    small.st-emotion-cache-ztfqz8,
    p.st-emotion-cache-ztfqz8 { display: none !important; }
    [data-testid="stForm"] .stFormSubmitButton > button {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; font-weight: 700 !important;
        font-size: 0.96rem !important; width: 100% !important;
        padding: 0.72rem 1rem !important; letter-spacing: 0.3px !important;
        transition: all 0.18s ease !important;
        box-shadow: 0 4px 18px rgba(99,102,241,0.4) !important;
    }
    [data-testid="stForm"] .stFormSubmitButton > button:hover {
        filter: brightness(1.1) !important;
        box-shadow: 0 10px 30px rgba(99,102,241,0.55) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="stForm"] [data-testid="stAlert"] {
        border-radius: 10px !important; font-size: 0.84rem !important;
    }
    @keyframes badgePop {
        from { opacity:0; transform:scale(0.8) translateY(6px); }
        to   { opacity:1; transform:scale(1) translateY(0); }
    }
    </style>
    """)

    left_col, right_col = st.columns([1.25, 1], gap="large")

    # ── LEFT: illustrated product mockup ──────────
    with left_col:
        st.html("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;padding:1rem 0;">

            <!-- glow ring behind mockup -->
            <div style="position:relative;width:100%;max-width:480px;">
                <div style="position:absolute;inset:-30px;background:radial-gradient(ellipse at 50% 50%,rgba(99,102,241,0.35) 0%,transparent 70%);border-radius:50%;filter:blur(30px);z-index:0;"></div>

                <!-- App window mockup -->
                <svg viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;position:relative;z-index:1;filter:drop-shadow(0 24px 48px rgba(0,0,0,0.5));">
                  <defs>
                    <linearGradient id="winGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stop-color="#1e1b4b"/>
                      <stop offset="100%" stop-color="#0f0c29"/>
                    </linearGradient>
                    <linearGradient id="btnGrad" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#4338ca"/>
                      <stop offset="100%" stop-color="#6366f1"/>
                    </linearGradient>
                    <linearGradient id="sideGrad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stop-color="#1e1b4b"/>
                      <stop offset="100%" stop-color="#272462"/>
                    </linearGradient>
                    <linearGradient id="cardBorder" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.8"/>
                      <stop offset="100%" stop-color="#a78bfa" stop-opacity="0.3"/>
                    </linearGradient>
                    <filter id="glow">
                      <feGaussianBlur stdDeviation="3" result="blur"/>
                      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                    <clipPath id="winClip">
                      <rect x="0" y="0" width="480" height="360" rx="16"/>
                    </clipPath>
                  </defs>

                  <!-- Window background -->
                  <rect width="480" height="360" rx="16" fill="url(#winGrad)" clip-path="url(#winClip)"/>

                  <!-- Title bar -->
                  <rect x="0" y="0" width="480" height="38" fill="#312e81" rx="16"/>
                  <rect x="0" y="22" width="480" height="16" fill="#312e81"/>
                  <!-- Traffic lights -->
                  <circle cx="20" cy="19" r="5.5" fill="#ff5f57"/>
                  <circle cx="36" cy="19" r="5.5" fill="#febc2e"/>
                  <circle cx="52" cy="19" r="5.5" fill="#28c840"/>
                  <!-- Title -->
                  <text x="240" y="23" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.7)" font-family="Inter,sans-serif" font-weight="600">⚡ XRP DSL Builder</text>
                  <!-- Tab -->
                  <rect x="80" y="10" width="110" height="18" rx="5" fill="rgba(255,255,255,0.08)"/>
                  <text x="135" y="22" text-anchor="middle" font-size="8" fill="rgba(255,255,255,0.5)" font-family="Inter,sans-serif">🧩 Build Rule</text>

                  <!-- Sidebar -->
                  <rect x="0" y="38" width="108" height="322" fill="url(#sideGrad)"/>
                  <rect x="107" y="38" width="1" height="322" fill="rgba(99,102,241,0.2)"/>
                  <!-- Sidebar logo -->
                  <rect x="14" y="52" width="80" height="28" rx="8" fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.3)" stroke-width="1"/>
                  <text x="54" y="70" text-anchor="middle" font-size="9" fill="#a5b4fc" font-family="Inter,sans-serif" font-weight="700">👤 Profile</text>
                  <!-- Sidebar fields -->
                  <rect x="14" y="90" width="80" height="7" rx="3.5" fill="rgba(255,255,255,0.12)"/>
                  <rect x="14" y="103" width="65" height="7" rx="3.5" fill="rgba(99,102,241,0.4)"/>
                  <rect x="14" y="118" width="80" height="7" rx="3.5" fill="rgba(255,255,255,0.08)"/>
                  <rect x="14" y="131" width="55" height="7" rx="3.5" fill="rgba(255,255,255,0.08)"/>
                  <rect x="14" y="148" width="80" height="1" fill="rgba(255,255,255,0.08)"/>
                  <!-- Active profile card -->
                  <rect x="14" y="158" width="80" height="70" rx="8" fill="rgba(14,165,233,0.1)" stroke="rgba(14,165,233,0.25)" stroke-width="1"/>
                  <text x="54" y="173" text-anchor="middle" font-size="7" fill="#38bdf8" font-family="Inter,sans-serif" font-weight="700">📊 Active Profile</text>
                  <rect x="22" y="180" width="55" height="5" rx="2.5" fill="rgba(255,255,255,0.12)"/>
                  <rect x="22" y="190" width="45" height="5" rx="2.5" fill="rgba(255,255,255,0.12)"/>
                  <rect x="22" y="200" width="60" height="5" rx="2.5" fill="rgba(255,255,255,0.12)"/>
                  <rect x="22" y="210" width="50" height="5" rx="2.5" fill="rgba(255,255,255,0.12)"/>

                  <!-- Main content area -->
                  <!-- Header -->
                  <rect x="118" y="48" width="352" height="36" rx="10" fill="rgba(79,70,229,0.25)" stroke="rgba(99,102,241,0.3)" stroke-width="1"/>
                  <text x="128" y="70" font-size="11" fill="white" font-family="Inter,sans-serif" font-weight="800">⚡ XRP DSL Builder</text>
                  <rect x="390" y="56" width="72" height="20" rx="10" fill="rgba(99,102,241,0.3)" stroke="rgba(99,102,241,0.5)" stroke-width="1"/>
                  <text x="426" y="69" text-anchor="middle" font-size="7" fill="#c7d2fe" font-family="Inter,sans-serif" font-weight="700">VISUAL RULE ENGINE</text>

                  <!-- Section label -->
                  <text x="128" y="104" font-size="7.5" fill="#6366f1" font-family="Inter,sans-serif" font-weight="800" letter-spacing="1">📋  CONDITIONS</text>
                  <rect x="182" y="100" width="278" height="1" fill="rgba(99,102,241,0.2)"/>

                  <!-- AND/OR radio -->
                  <rect x="128" y="110" width="100" height="16" rx="8" fill="rgba(99,102,241,0.1)" stroke="rgba(99,102,241,0.2)" stroke-width="1"/>
                  <rect x="130" y="112" width="40" height="12" rx="6" fill="url(#btnGrad)"/>
                  <text x="150" y="121" text-anchor="middle" font-size="7" fill="white" font-family="Inter,sans-serif" font-weight="700">AND</text>
                  <text x="195" y="121" text-anchor="middle" font-size="7" fill="rgba(255,255,255,0.5)" font-family="Inter,sans-serif">OR</text>

                  <!-- Condition Card 1 -->
                  <rect x="118" y="134" width="230" height="56" rx="10" fill="white" stroke="#e0e7ff" stroke-width="1"/>
                  <rect x="118" y="134" width="4" height="56" rx="2" fill="#6366f1"/>
                  <circle cx="134" cy="152" r="8" fill="url(#btnGrad)" filter="url(#glow)"/>
                  <text x="134" y="156" text-anchor="middle" font-size="7" fill="white" font-family="Inter,sans-serif" font-weight="800">1</text>
                  <rect x="148" y="146" width="55" height="7" rx="3.5" fill="#e0e7ff"/>
                  <rect x="210" y="146" width="30" height="7" rx="3.5" fill="#ede9fe"/>
                  <rect x="247" y="146" width="45" height="7" rx="3.5" fill="#e0e7ff"/>
                  <rect x="148" y="160" width="45" height="6" rx="3" fill="#ede9fe"/>
                  <rect x="200" y="160" width="60" height="6" rx="3" fill="#f0fdf4"/>
                  <!-- DSL snippet -->
                  <rect x="128" y="175" width="210" height="10" rx="5" fill="#f8fafc" stroke="#e0e7ff" stroke-width="1"/>
                  <rect x="132" y="178" width="80" height="4" rx="2" fill="#93c5fd"/>
                  <rect x="218" y="178" width="50" height="4" rx="2" fill="#86efac"/>

                  <!-- AND pill -->
                  <rect x="213" y="196" width="36" height="13" rx="6.5" fill="#ede9fe" stroke="#c4b5fd" stroke-width="1"/>
                  <text x="231" y="205" text-anchor="middle" font-size="7" fill="#5b21b6" font-family="Inter,sans-serif" font-weight="800">AND</text>

                  <!-- Condition Card 2 -->
                  <rect x="118" y="214" width="230" height="56" rx="10" fill="white" stroke="#e0e7ff" stroke-width="1"/>
                  <rect x="118" y="214" width="4" height="56" rx="2" fill="#818cf8"/>
                  <circle cx="134" cy="232" r="8" fill="url(#btnGrad)"/>
                  <text x="134" y="236" text-anchor="middle" font-size="7" fill="white" font-family="Inter,sans-serif" font-weight="800">2</text>
                  <rect x="148" y="226" width="65" height="7" rx="3.5" fill="#e0e7ff"/>
                  <rect x="220" y="226" width="25" height="7" rx="3.5" fill="#ede9fe"/>
                  <rect x="252" y="226" width="40" height="7" rx="3.5" fill="#e0e7ff"/>
                  <rect x="148" y="240" width="100" height="6" rx="3" fill="#ede9fe"/>
                  <rect x="128" y="255" width="210" height="10" rx="5" fill="#f8fafc" stroke="#e0e7ff" stroke-width="1"/>
                  <rect x="132" y="258" width="120" height="4" rx="2" fill="#86efac"/>

                  <!-- DSL Output panel (right) -->
                  <rect x="358" y="90" width="112" height="190" rx="10" fill="rgba(0,0,0,0.5)" stroke="rgba(99,102,241,0.3)" stroke-width="1"/>
                  <text x="368" y="107" font-size="7" fill="#a5b4fc" font-family="monospace,sans-serif" font-weight="700">⚡ DSL Output</text>
                  <rect x="362" y="112" width="104" height="1" fill="rgba(255,255,255,0.1)"/>
                  <!-- Code lines -->
                  <rect x="366" y="120" width="70" height="5" rx="2.5" fill="#79c0ff" opacity="0.7"/>
                  <rect x="366" y="130" width="85" height="5" rx="2.5" fill="#a5d6a7" opacity="0.7"/>
                  <rect x="366" y="140" width="60" height="5" rx="2.5" fill="#79c0ff" opacity="0.7"/>
                  <rect x="366" y="150" width="92" height="5" rx="2.5" fill="#ffd180" opacity="0.7"/>
                  <rect x="366" y="160" width="78" height="5" rx="2.5" fill="#a5d6a7" opacity="0.7"/>
                  <rect x="366" y="170" width="65" height="5" rx="2.5" fill="#79c0ff" opacity="0.7"/>
                  <rect x="366" y="180" width="88" height="5" rx="2.5" fill="#ffd180" opacity="0.7"/>
                  <rect x="366" y="190" width="72" height="5" rx="2.5" fill="#a5d6a7" opacity="0.7"/>
                  <!-- Cursor blink -->
                  <rect x="366" y="202" width="2" height="9" rx="1" fill="#6366f1">
                    <animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/>
                  </rect>
                  <!-- Copy button -->
                  <rect x="362" y="252" width="104" height="20" rx="7" fill="url(#btnGrad)" opacity="0.9"/>
                  <text x="414" y="265" text-anchor="middle" font-size="8" fill="white" font-family="Inter,sans-serif" font-weight="700">📋 Copy DSL</text>

                  <!-- Bottom stats bar -->
                  <rect x="118" y="298" width="342" height="38" rx="10" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
                  <!-- Stat 1 -->
                  <text x="160" y="312" text-anchor="middle" font-size="11" fill="#e0e7ff" font-family="Inter,sans-serif" font-weight="800">2</text>
                  <text x="160" y="327" text-anchor="middle" font-size="7" fill="rgba(255,255,255,0.4)" font-family="Inter,sans-serif">Conditions</text>
                  <rect x="205" y="306" width="1" height="22" fill="rgba(255,255,255,0.1)"/>
                  <!-- Stat 2 -->
                  <text x="248" y="312" text-anchor="middle" font-size="9" fill="#e0e7ff" font-family="Inter,sans-serif" font-weight="800">AND</text>
                  <text x="248" y="327" text-anchor="middle" font-size="7" fill="rgba(255,255,255,0.4)" font-family="Inter,sans-serif">Logic</text>
                  <rect x="295" y="306" width="1" height="22" fill="rgba(255,255,255,0.1)"/>
                  <!-- Stat 3 -->
                  <circle cx="338" cy="315" r="7" fill="#22c55e" opacity="0.2"/>
                  <circle cx="338" cy="315" r="4" fill="#22c55e"/>
                  <text x="360" y="312" font-size="9" fill="#e0e7ff" font-family="Inter,sans-serif" font-weight="700">DSL Ready</text>
                  <text x="360" y="326" font-size="7" fill="rgba(255,255,255,0.4)" font-family="Inter,sans-serif">✓ Valid expression</text>

                  <!-- Floating badge top-right -->
                  <rect x="330" y="52" width="50" height="18" rx="9" fill="#22c55e" opacity="0.15" stroke="#22c55e" stroke-width="1" stroke-opacity="0.4"/>
                  <circle cx="341" cy="61" r="3" fill="#22c55e"/>
                  <text x="358" y="65" text-anchor="middle" font-size="7" fill="#86efac" font-family="Inter,sans-serif" font-weight="700">LIVE</text>
                </svg>

                <!-- Floating decorative badges -->
                <div style="position:absolute;top:-12px;right:-10px;
                    background:linear-gradient(135deg,#4338ca,#6366f1);
                    color:white;font-size:0.7rem;font-weight:700;
                    padding:0.35rem 0.8rem;border-radius:20px;
                    box-shadow:0 4px 16px rgba(99,102,241,0.5);
                    border:1px solid rgba(255,255,255,0.2);
                    animation:badgePop 0.6s ease 0.5s both;">
                    ⚡ Visual Rule Engine
                </div>
                <div style="position:absolute;bottom:8px;left:-14px;
                    background:rgba(34,197,94,0.15);
                    border:1px solid rgba(34,197,94,0.4);
                    color:#86efac;font-size:0.68rem;font-weight:700;
                    padding:0.3rem 0.75rem;border-radius:20px;
                    backdrop-filter:blur(10px);
                    animation:badgePop 0.6s ease 1s both;">
                    ✓ DSL Generated
                </div>
            </div>

            <div style="text-align:center;margin-top:1.6rem;">
                <div style="color:rgba(255,255,255,0.85);font-size:1.15rem;font-weight:800;letter-spacing:-0.4px;margin-bottom:0.35rem;">
                    Build Targeting Rules Visually
                </div>
                <div style="color:rgba(255,255,255,0.45);font-size:0.8rem;line-height:1.6;max-width:320px;margin:0 auto;">
                    Point-and-click rule builder that generates XRP DSL expressions instantly — no coding required.
                </div>
            </div>
        </div>

        """)

    # ── RIGHT: login form ──────────────────────────
    with right_col:
        with st.form("login_form", clear_on_submit=False):
            st.html("""
            <div style="text-align:center; margin-bottom:1.8rem;">
                <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:62px;height:62px;border-radius:18px;margin-bottom:1rem;
                    background:linear-gradient(135deg,#4338ca,#6366f1);
                    box-shadow:0 8px 24px rgba(99,102,241,0.45);font-size:1.9rem;">⚡</div>
                <div style="font-size:1.55rem;font-weight:800;color:#1e1b4b;letter-spacing:-0.6px;margin-bottom:0.35rem;">XRP Visual Tool</div>
                <div style="font-size:0.83rem;color:#64748b;font-weight:400;">Sign in to access the rule builder</div>
                <hr style="margin:1.4rem 0 0.6rem 0;border:none;border-top:1px solid #e2e8f0;">
            </div>
            """)

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif _check_credentials(username.strip(), password):
                    st.session_state["authenticated"] = True
                    st.session_state["logged_in_user"] = username.strip()
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")

            st.html("""
            <div style="text-align:center;font-size:0.72rem;color:#94a3b8;margin-top:1.4rem;line-height:1.7;">
                🔒 Access restricted to authorized personnel only.<br>
                Contact your administrator if you need access.
            </div>
            """)


# Gate: show login if not authenticated
if not st.session_state.get("authenticated", False):
    _render_login_page()
    st.stop()

# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
/* Inherit Inter everywhere — but without !important so icon fonts (Material Symbols) can override */
* { font-family: inherit; }

.block-container { padding-top: 1.4rem !important; padding-bottom: 1rem !important; }

/* ═══ HEADER ═══ */
.header-banner {
    background: linear-gradient(120deg, #312e81 0%, #4f46e5 45%, #6366f1 75%, #818cf8 100%);
    padding: 1.2rem 2rem; border-radius: 18px; margin-bottom: 1.3rem;
    box-shadow: 0 10px 40px rgba(79,70,229,0.28), inset 0 1px 0 rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
}
.header-left {}
.header-title { color: white; font-size: 1.55rem; font-weight: 800; margin: 0; letter-spacing: -0.6px; }
.header-sub { color: rgba(255,255,255,0.62); font-size: 0.81rem; margin: 0.3rem 0 0 0; font-weight: 400; }
.header-badge {
    background: rgba(255,255,255,0.16); backdrop-filter: blur(10px);
    color: white; padding: 0.45rem 1.2rem; border-radius: 25px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; border: 1px solid rgba(255,255,255,0.22);
    white-space: nowrap;
}

/* ═══ SECTION TITLE ═══ */
.section-title {
    font-size: 0.68rem; font-weight: 800; color: #4f46e5;
    text-transform: uppercase; letter-spacing: 1.4px; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.55rem;
}
.section-title::after { content: ''; flex: 1; height: 1.5px; background: linear-gradient(to right, #e0e7ff, transparent); }

/* ═══ CONDITION CARD ═══ */
.condition-card {
    background: #ffffff; border: 1px solid #e0e7ff; border-left: 4px solid #6366f1;
    border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: 0.45rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.07); transition: all 0.15s ease;
}
.condition-card:hover { box-shadow: 0 6px 24px rgba(99,102,241,0.14); border-left-color: #4f46e5; transform: translateY(-1px); }

.cond-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 23px; height: 23px; background: linear-gradient(135deg, #6366f1, #4338ca);
    color: white; border-radius: 50%; font-size: 0.69rem; font-weight: 800;
    margin-right: 0.5rem; box-shadow: 0 2px 6px rgba(99,102,241,0.45); flex-shrink: 0;
}
.field-label {
    font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.9px; color: #94a3b8; margin-bottom: 0.18rem; display: block;
}
/* ═══ AND/OR CONNECTOR ═══ */
.logic-connector {
    display: flex; align-items: center; gap: 0.6rem; margin: 0.3rem 0 0.3rem 0.5rem;
}
.logic-line { flex: 1; height: 1px; background: linear-gradient(to right, #e0e7ff 60%, transparent); }
.logic-and-badge { background: #e0e7ff; color: #3730a3; font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.5px; }
.logic-or-badge  { background: #fef3c7; color: #92400e; font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.5px; }

/* ═══ DSL OUTPUT BOX ═══ */
.dsl-box {
    background: #0d1117; border: 1px solid #21262d; border-radius: 16px;
    padding: 1.3rem 1.5rem; font-family: 'Courier New', Courier, monospace;
    font-size: 0.84rem; color: #c9d1d9; line-height: 1.85;
    word-break: break-all; min-height: 90px;
    box-shadow: inset 0 2px 12px rgba(0,0,0,0.45), 0 4px 20px rgba(0,0,0,0.15);
}
.dsl-empty { color: #484f58; font-style: italic; font-size: 0.82rem; }

/* ═══ BUTTONS — primary (default) ═══ */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important; border: none !important; border-radius: 9px !important;
    padding: 0.42rem 0.9rem !important; font-weight: 600 !important;
    font-size: 0.83rem !important; letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important; width: 100% !important;
    min-height: 2.15rem !important; white-space: nowrap !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.stButton > button:hover {
    filter: brightness(1.1) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.42) !important;
    transform: translateY(-1px) !important;
}
.stButton > button p, .stButton > button span { margin: 0 !important; color: white !important; font-weight: 600 !important; }

/* ═══ COMPACT ± BUTTONS — wrap with class="compact-btn-row" div ═══ */
.compact-btn-row .stButton > button {
    background: white !important; color: #4b5563 !important;
    border: 1.5px solid #d1d5db !important; border-radius: 7px !important;
    padding: 0.25rem 0.5rem !important; font-size: 1rem !important;
    font-weight: 700 !important; min-height: 1.9rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.compact-btn-row .stButton > button:hover {
    border-color: #6366f1 !important; color: #6366f1 !important;
    background: #f5f3ff !important; box-shadow: none !important; transform: none !important; filter: none !important;
}
.compact-btn-row .stButton > button p,
.compact-btn-row .stButton > button span { color: inherit !important; font-weight: 700 !important; }

/* ═══ ADD/REMOVE CONDITION buttons ═══ */
.add-cond-btn .stButton > button { background: #f5f3ff !important; color: #4f46e5 !important; border: 1.5px dashed #a5b4fc !important; }
.add-cond-btn .stButton > button:hover { background: #e0e7ff !important; border-color: #6366f1 !important; box-shadow: none !important; transform: none !important; filter: none !important; }
.add-cond-btn .stButton > button p,
.add-cond-btn .stButton > button span { color: #4f46e5 !important; }
.rem-cond-btn .stButton > button { background: #fff1f2 !important; color: #e11d48 !important; border: 1.5px solid #fecdd3 !important; }
.rem-cond-btn .stButton > button:hover { background: #ffe4e6 !important; border-color: #f43f5e !important; box-shadow: none !important; transform: none !important; filter: none !important; }
.rem-cond-btn .stButton > button p,
.rem-cond-btn .stButton > button span { color: #e11d48 !important; }

/* ═══ RESULT BOXES ═══ */
.result-pass {
    background: linear-gradient(135deg, #052e16, #065f46); border: 1px solid #34d399;
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center; color: white;
    margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(52,211,153,0.2);
}
.result-fail {
    background: linear-gradient(135deg, #450a0a, #7f1d1d); border: 1px solid #f87171;
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center; color: white;
    margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(248,113,113,0.2);
}
.result-icon { font-size: 2rem; margin-bottom: 0.3rem; }
.result-title { font-size: 1.25rem; font-weight: 800; }
.result-desc { font-size: 0.82rem; opacity: 0.75; margin-top: 0.2rem; }
.debug-pass { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 0.45rem 0.9rem; border-radius: 0 8px 8px 0; margin-bottom: 0.3rem; font-size: 0.83rem; color: #14532d; }
.debug-fail { background: #fef2f2; border-left: 4px solid #ef4444; padding: 0.45rem 0.9rem; border-radius: 0 8px 8px 0; margin-bottom: 0.3rem; font-size: 0.83rem; color: #7f1d1d; }
.pill { display: inline-block; padding: 0.22rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-right: 0.35rem; }
.pill-total { background: #e0e7ff; color: #3730a3; }
.pill-pass  { background: #dcfce7; color: #166534; }
.pill-fail  { background: #fee2e2; color: #991b1b; }

/* ═══ SIDEBAR ═══ */
section[data-testid="stSidebar"] { background: #f5f7ff !important; border-right: 1.5px solid #e0e7ff !important; }
.sidebar-card { background: white; border: 1px solid #e0e7ff; border-radius: 12px; padding: 0.8rem 0.95rem; margin-bottom: 0.5rem; box-shadow: 0 1px 4px rgba(99,102,241,0.05); }
.sidebar-card-title { font-size: 0.67rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.1px; color: #4f46e5; margin-bottom: 0.5rem; padding-bottom: 0.4rem; border-bottom: 1.5px solid #f0f0fc; }

/* ═══ MISC ═══ */
hr { border: none !important; border-top: 1px solid #f0f0fc !important; margin: 0.75rem 0 !important; }
.stTabs [data-baseweb="tab-list"] { background: #eeeffc; padding: 0.2rem; border-radius: 10px; gap: 0.2rem; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-weight: 500 !important; padding: 0.3rem 1rem !important; font-size: 0.87rem !important; }
.stTabs [aria-selected="true"] { background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.09) !important; font-weight: 700 !important; color: #4f46e5 !important; }
</style>
""", unsafe_allow_html=True)


# ==================== CONFIGURATION ====================

RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "XIT_AIQ_PREDICTIVE_WAN_SCORE": {
        "title": "WiFi Alert",
        "en-US": "An issue may be affecting your home internet. A technician can help.",
        "es-US": "Parece que hay un problema con el internet de tu hogar. Un técnico puede ayudarte."
    },
    "XIT_AIQ_PREDICTIVE_OUTSIDE_HOME": {
        "title": "Outside Technician",
        "en-US": "To fix an internet issue, a technician may access equipment outside your home.",
        "es-US": "Para solucionar el problema, un técnico podría acceder al equipo que se encuentra afuera de tu hogar."
    }
}

FACT_DSL_MAP: Dict[str, str] = {
    "Client Device Make": "facts.client.device.make",
    "Permissions (toArray)": "__toarray__",
    "Client Device Model": "facts.client.device.model",
    "Client Device OS Name": "facts.client.device.os.name",
    "Client Device OS Version": "facts.client.device.os.version",
    "Client Platform": "facts.client.platform",
    "Client App Version": "facts.client.version",
    "Service Account ID": "serviceAccount.id",
    "Service Account Partner": "serviceAccount.partner",
    "User Role": "facts.auth.user_role",
    "Has Multiple Accounts": "facts.auth.has_multiple_accounts",
    "Internet Backup On": "rule.is_internet_backup_on",
    "Power Backup On": "rule.is_power_backup_on",
    "Show Line Level Experience": "rule.should_show_line_level_experience",
    "EDP Auto Optimization": "rule.edp_state_features_auto_optimization",
    "Disconnected Customer": "rule.is_disconnected_customer",
    "Has GW Device": "rule.has_gw_device",
    "Bridge Mode Enabled": "rule.is_bridge_mode_enabled",
    "Device Priority Capable": "rule.device_priority_capable",
    "Permission: Device Prioritization View": "facts.permissions.device_prioritization.view",
    "Audience": "facts.xcdp.realized",
    "Experiment Treatment": "experiment.{experiment_name}.treatment",
    "Last Account Visit": "facts.visits_account.accessedOn",
    "Last Account2 Visit": "facts.visits_account2.accessedOn",
}

FACT_VALUES: Dict[str, List[str]] = {
    "Client Device Make": ["Samsung", "Apple", "Custom"],
    "Client Device Model": ["SM-G955U", "iPhone", "Custom"],
    "Client Device OS Name": ["Android", "iOS"],
    "Client Device OS Version": ["Custom"],
    "Client Platform": ["MOBILE", "WEB"],
    "Client App Version": ["Custom"],
    "Service Account ID": ["Custom"],
    "Service Account Partner": ["comcast", "Custom"],
    "User Role": ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM", "MANAGER"],
    "Has Multiple Accounts": ["true", "false"],
    "Internet Backup On": ["true", "false"],
    "Power Backup On": ["true", "false"],
    "Show Line Level Experience": ["true", "false"],
    "EDP Auto Optimization": ["true", "false"],
    "Disconnected Customer": ["true", "false"],
    "Has GW Device": ["true", "false"],
    "Bridge Mode Enabled": ["true", "false"],
    "Device Priority Capable": ["true", "false"],
    "Permission: Device Prioritization View": ["true", "false"],
    "Audience": ["HQ_Cust_XM_Income_Above50K_Legacy", "HQ_Cust_Digital_Soccer_Likely", "Custom"],
    "Experiment Treatment": ["on", "off", "control", "Custom"],
    "Last Account Visit": ["Custom"],
    "Last Account2 Visit": ["Custom"],
}

TO_ARRAY_FACTS: Dict[str, str] = {
    "Permissions (toArray)": "facts.permissions",
}

# Maps human-readable operator labels to DSL symbols
COMPARISON_OP_MAP: Dict[str, str] = {
    "at least (>=)": ">=",
    "at most (<=)": "<=",
    "above (>)":    ">",
    "below (<)":    "<",
}

# Fact DSL paths that behave as boolean flags (truthy/falsy) but don't start with "rule."
TRUTHY_FACTS: set = {
    "facts.permissions.device_prioritization.view",
}

# Quick-start rule templates
RULE_TEMPLATES: Dict[str, dict] = {
    "iOS — Primary": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Client Device OS Name", "is", "iOS"),
            ("User Role", "is", "PRIMARY"),
        ]
    },
    "Android — Version Gate": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Client Device OS Name", "is", "Android"),
            ("Client App Version", "at least (>=)", "6.4"),
        ]
    },
    "Audience + Role": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Audience", "is", "HQ_Cust_Digital_Soccer_Likely"),
            ("User Role", "is", "PRIMARY"),
        ]
    },
    "Device Priority": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Device Priority Capable", "is", "true"),
            ("Has GW Device", "is", "true"),
        ]
    },
    "Disconnected Customer": {
        "num": 1, "logic": "AND",
        "conditions": [
            ("Disconnected Customer", "is", "true"),
        ]
    },
    "Restricted Account": {
        "num": 1, "logic": "AND",
        "conditions": [
            ("User Role", "is", "RESTRICTED_SECONDARY"),
        ]
    },
}


# ==================== UTILITY FUNCTIONS ====================

def _resolve_perm_paths(value: str, base: str) -> List[str]:
    """Expand comma-separated sub-paths into full permission paths."""
    result = []
    for p in (p.strip() for p in value.split(",") if p.strip()):
        if p.startswith("facts."):
            result.append(p)
        elif p.startswith("."):
            result.append(base + p)
        else:
            result.append(base + "." + p)
    return result

def generate_dsl(conditions: List[Tuple[str, str, str, str]], logic: Union[str, List[str]]) -> str:
    """Generate DSL. Each condition is (fact, operator, value, condition_logic).
    logic between items uses the operator stored on the NEXT condition (or global fallback)."""
    if not conditions:
        return ""
    dsl_parts = []
    for fact, operator, value, _cond_logic in conditions:
        # Raw / complex expression — emit stored expression directly, skip value check
        if fact.startswith("__raw__:"):
            _raw_expr = fact[len("__raw__:"):]
            if not _raw_expr.strip():
                raise ValueError("Empty custom DSL expression — please fill in the expression")
            dsl_parts.append(_raw_expr.strip())
            continue
        if not value or not value.strip():
            raise ValueError(f"Empty value for fact '{fact}' — please fill in all values")
        dsl_path = FACT_DSL_MAP.get(fact, fact)
        # toArray() special handling
        if dsl_path == "__toarray__":
            base = TO_ARRAY_FACTS.get(fact, "facts.permissions")
            full_paths = _resolve_perm_paths(value, base)
            bool_val = "false" if operator == "is not" else "true"
            dsl_expr = f'toArray({", ".join(full_paths)}) == {bool_val}'
        else:
            is_rule_flag = dsl_path.startswith("rule.") or dsl_path in TRUTHY_FACTS or dsl_path.startswith("facts.permissions.")
            is_boolean_value = value.lower() in ["true", "false"]
            if is_rule_flag and is_boolean_value:
                dsl_expr = f"!{dsl_path}" if operator == "is not" else dsl_path
            elif dsl_path in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
                _vals = [v.strip() for v in value.split(",") if v.strip()]
                if len(_vals) > 1:
                    _vals_str = ", ".join(f'"{v}"' for v in _vals)
                    dsl_op = "!=" if operator == "is not" else "=="
                    dsl_expr = f'{dsl_path} {dsl_op} to_array({_vals_str})'
                else:
                    dsl_operator = "==" if operator == "is" else "!="
                    dsl_expr = f'{dsl_path} {dsl_operator} "{value.strip()}"'
            elif operator in COMPARISON_OP_MAP and dsl_path == "facts.client.version":
                sym = COMPARISON_OP_MAP[operator]
                dsl_expr = f'version_compare({dsl_path}, "{value.strip()}") {sym} 0'
            elif operator in COMPARISON_OP_MAP:
                dsl_expr = f'{dsl_path} {COMPARISON_OP_MAP[operator]} "{value.strip()}"'
            else:
                dsl_operator = "==" if operator == "is" else "!="
                dsl_expr = f'{dsl_path} {dsl_operator} "{value.strip()}"'
        dsl_parts.append(dsl_expr)

    # Build final DSL joining with per-condition logic operators
    if len(dsl_parts) == 1:
        return f"({dsl_parts[0]})"
    result = dsl_parts[0]
    for idx in range(1, len(dsl_parts)):
        # The operator joining condition idx-1 and idx is stored on condition idx
        cond_logic = conditions[idx][3] if len(conditions[idx]) > 3 else (logic if isinstance(logic, str) else "AND")
        op_str = " && " if cond_logic == "AND" else " || "
        result += op_str + dsl_parts[idx]
    return f"({result})"


def get_test_value_for_fact(fact: str, test_values: Dict[str, str]) -> str:
    fact_map = {
        "Client Device Make": test_values.get("device_make"),
        "Client Device OS Name": test_values.get("device_os"),
        "User Role": test_values.get("user_role"),
        "Service Account ID": test_values.get("account_id"),
        "Has Multiple Accounts": test_values.get("has_multiple"),
        "Audience": test_values.get("audience") or "(empty)",
        "Internet Backup On": test_values.get("internet_backup"),
        "Power Backup On": test_values.get("power_backup"),
        "Show Line Level Experience": test_values.get("show_line_level"),
    }
    return fact_map.get(fact, "N/A (not supported in test)")


def _parse_version(v: str) -> tuple:
    """Parse a version string like '6.4' or '10.2.1' into a comparable tuple."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (v.strip(),)


def evaluate_condition(fact: str, operator: str, expected_value: str, actual_value: str) -> bool:
    if actual_value.startswith("N/A"):
        return False
    if operator in COMPARISON_OP_MAP:
        sym = COMPARISON_OP_MAP[operator]
        av = _parse_version(actual_value)
        ev = _parse_version(expected_value)
        if sym == ">=": return av >= ev
        if sym == "<=": return av <= ev
        if sym == ">": return av > ev
        if sym == "<": return av < ev
    match = (actual_value == expected_value)
    return (not match) if operator == "is not" else match


def _split_top_level(text: str, op: str) -> List[str]:
    """Split text by op only at parenthesis/bracket depth 0."""
    parts: List[str] = []
    current, depth, i = "", 0, 0
    op_len = len(op)
    while i < len(text):
        ch = text[i]
        if ch in "({": depth += 1; current += ch; i += 1
        elif ch in ")}": depth -= 1; current += ch; i += 1
        elif depth == 0 and text[i:i + op_len] == op:
            parts.append(current.strip()); current = ""; i += op_len
        else:
            current += ch; i += 1
    if current.strip():
        parts.append(current.strip())
    return parts


def parse_dsl_to_conditions(dsl_text: str):
    """
    Parse a DSL string into (conditions, global_logic, errors, warnings).
    conditions: List of (fact, operator, value, cond_logic)
    """
    errors: List[str] = []
    warnings: List[str] = []
    conditions: List[Tuple] = []

    text = dsl_text.strip()
    if not text:
        return [], "AND", ["Empty DSL expression."], []

    # ── Normalize: collapse newlines/tabs → spaces, then normalise spacing
    # around && and || so the depth-aware splitter always sees ' && ' / ' || '
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r' {2,}', ' ', text).strip()
    text = re.sub(r'\s*&&\s*', ' && ', text)
    text = re.sub(r'\s*\|\|\s*', ' || ', text)

    # Check unmatched parentheses
    depth = 0
    for ch in text:
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if depth < 0:
            return [], "AND", ["Unmatched closing parenthesis ')' — check your brackets."], []
    if depth != 0:
        return [], "AND", [f"Unmatched opening parenthesis '(' — {depth} bracket(s) left unclosed."], []

    # Strip one level of outer parens if balanced
    if text.startswith("(") and text.endswith(")"):
        inner, d = text[1:-1], 0
        ok = True
        for ch in inner:
            if ch == "(": d += 1
            elif ch == ")": d -= 1
            if d < 0: ok = False; break
        if ok and d == 0:
            text = inner.strip()

    # Check for spacing issues around logical operators
    if re.search(r'(?<![&|])[&][&](?![&|])', text) and " && " not in text:
        warnings.append("Missing spaces around '&&' — use ' && ' between conditions.")
    if re.search(r'(?<![|])[|][|](?![|])', text) and " || " not in text:
        warnings.append("Missing spaces around '||' — use ' || ' between conditions.")

    # Check for single-quoted strings (should be double-quoted)
    if re.search(r"(?<![\\])'", text):
        warnings.append("Single quotes detected — DSL requires double quotes around values.")

    # Split on top-level ' && ' and ' || '
    parts: List[str] = []
    ops_between: List[str] = []
    current, depth = "", 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "({":
            depth += 1; current += ch; i += 1
        elif ch in ")}":
            depth -= 1; current += ch; i += 1
        elif depth == 0 and text[i:i+4] == " && ":
            parts.append(current.strip()); ops_between.append("AND")
            current = ""; i += 4
        elif depth == 0 and text[i:i+4] == " || ":
            parts.append(current.strip()); ops_between.append("OR")
            current = ""; i += 4
        elif depth == 0 and text[i:i+2] in ("&&", "||"):
            # Handle missing-space variants
            op_sym = "AND" if text[i:i+2] == "&&" else "OR"
            parts.append(current.strip()); ops_between.append(op_sym)
            current = ""; i += 2
        else:
            current += ch; i += 1
    if current.strip():
        parts.append(current.strip())

    if not parts:
        return [], "AND", ["No conditions found in the DSL expression."], warnings

    # Determine global logic from majority operator
    if ops_between:
        global_logic = "AND" if ops_between.count("AND") >= ops_between.count("OR") else "OR"
    else:
        global_logic = "AND"

    # Reverse maps
    rev_map: Dict[str, str] = {v: k for k, v in FACT_DSL_MAP.items() if v != "__toarray__"}
    known_paths: set = {v for v in FACT_DSL_MAP.values() if v != "__toarray__"}
    rev_comp: Dict[str, str] = {v: k for k, v in COMPARISON_OP_MAP.items()}

    # ── Flatten grouped OR sub-expressions: (A || B) inside && chains ──────────
    # After top-level && split, each part may be a parenthesised OR group like
    # (!rule.X || facts.y == to_array(...)). We expand those into individual
    # conditions here so the per-condition pattern matchers can handle them.
    flat_parts: List[str] = []
    flat_ops: List[str] = []  # logic connector that joins flat_parts[i] to flat_parts[i-1]

    for _fi, _fpart in enumerate(parts):
        _incoming = ops_between[_fi - 1] if _fi > 0 else global_logic
        # Try to strip one level of balanced outer parentheses
        if _fpart.startswith("(") and _fpart.endswith(")"):
            _inner = _fpart[1:-1]
            _d, _ok = 0, True
            for _ch in _inner:
                if _ch == "(": _d += 1
                elif _ch == ")": _d -= 1
                if _d < 0: _ok = False; break
            if _ok and _d == 0:
                # Check for top-level || operators inside the group
                _sub = _split_top_level(_inner.strip(), " || ")
                if len(_sub) > 1:
                    for _si, _sp in enumerate(_sub):
                        flat_parts.append(_sp.strip())
                        flat_ops.append(_incoming if _si == 0 else "OR")
                    continue
                # No top-level ||; also try bare &&
                _sub_and = _split_top_level(_inner.strip(), " && ")
                if len(_sub_and) > 1:
                    for _si, _sp in enumerate(_sub_and):
                        flat_parts.append(_sp.strip())
                        flat_ops.append(_incoming if _si == 0 else "AND")
                    continue
        flat_parts.append(_fpart)
        flat_ops.append(_incoming)

    # Recalculate global_logic from the full flattened operator list
    _all_flat_ops = [o for o in flat_ops if o]
    if _all_flat_ops:
        global_logic = "AND" if _all_flat_ops.count("AND") >= _all_flat_ops.count("OR") else "OR"

    for idx, part in enumerate(flat_parts):
        part = part.strip()
        cond_logic = flat_ops[idx] if idx < len(flat_ops) else global_logic

        # ── toArray(...) == true/false ──────────────────────
        m = re.match(r'^toArray\((.+)\)\s*==\s*(true|false)$', part, re.IGNORECASE)
        if m:
            paths = [p.strip() for p in m.group(1).split(",")]
            bool_val = m.group(2).lower()
            operator = "is not" if bool_val == "false" else "is"
            sub = [p[len("facts.permissions."):] if p.startswith("facts.permissions.") else p for p in paths]
            conditions.append(("Permissions (toArray)", operator, ", ".join(sub), cond_logic))
            continue

        # ── !path  (negated boolean flag) ──────────────────
        m = re.match(r'^!([a-zA-Z_][a-zA-Z0-9_.{}]*)$', part)
        if m:
            path = m.group(1)
            fact_name = rev_map.get(path, path)
            if path not in known_paths and not (path.startswith("rule.") or path.startswith("facts.")):
                warnings.append(f"Unknown DSL path '{path}' — possible typo?")
            conditions.append((fact_name, "is not", "true", cond_logic))
            continue

        # ── bare path (positive boolean flag) ──────────────
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.{}]*)$', part)
        if m:
            path = m.group(1)
            fact_name = rev_map.get(path, path)
            if path not in known_paths and not (path.startswith("rule.") or path.startswith("facts.")):
                warnings.append(f"Unknown DSL path '{path}' — possible typo?")
            conditions.append((fact_name, "is", "true", cond_logic))
            continue

        # ── version_compare(path, "ver") sym 0 ─────────────
        m = re.match(r'^version_compare\(([^,]+),\s*"([^"]+)"\)\s*([><=!]+)\s*0$', part)
        if m:
            path, value, sym = m.group(1).strip(), m.group(2), m.group(3)
            operator = rev_comp.get(sym)
            if not operator:
                errors.append(f"Unknown comparison symbol '{sym}' in: `{part}`"); continue
            conditions.append((rev_map.get(path, path), operator, value, cond_logic))
            continue

        # ── path op to_array("v1", "v2") ────────────────────
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.{}]*)\s*(==|!=)\s*to_array\((.+)\)$', part)
        if m:
            path, sym, vals_raw = m.group(1).strip(), m.group(2), m.group(3)
            vals = re.findall(r'"([^"]*)"', vals_raw)
            operator = "is not" if sym == "!=" else "is"
            conditions.append((rev_map.get(path, path), operator, ", ".join(vals), cond_logic))
            continue

        # ── path op "value"  (most common) ─────────────────
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.{}]*)\s*([><=!]+)\s*"([^"]*)"$', part)
        if m:
            path, sym, value = m.group(1).strip(), m.group(2), m.group(3)
            if sym in rev_comp:
                operator = rev_comp[sym]
            elif sym == "==":
                operator = "is"
            elif sym == "!=":
                operator = "is not"
            else:
                errors.append(f"Unknown operator '{sym}' in: `{part}`"); continue
            fact_name = rev_map.get(path, path)
            if (
                path not in known_paths
                and not path.startswith("rule.")
                and not path.startswith("facts.")
                and not path.startswith("serviceAccount.")
                and not path.startswith("experiment.")
            ):
                warnings.append(f"Unknown DSL path '{path}' — possible typo?")
            conditions.append((fact_name, operator, value, cond_logic))
            continue

        # ── path op 'value'  (single-quote typo) ───────────
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_.{}]*)\s*([><=!]+)\s*'([^']*)'$", part)
        if m:
            path, sym, value = m.group(1).strip(), m.group(2), m.group(3)
            warnings.append(f"Single quotes used around '{value}' — replace with double quotes.")
            operator = "is" if sym == "==" else ("is not" if sym == "!=" else "is")
            conditions.append((rev_map.get(path, path), operator, value, cond_logic))
            continue

        # ── path op unquoted_value ──────────────────────────
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.{}]*)\s*([><=!]+)\s*([a-zA-Z0-9._]+)$', part)
        if m:
            path, sym, value = m.group(1).strip(), m.group(2), m.group(3)
            if value.lower() not in ("true", "false"):
                warnings.append(f"Unquoted string value '{value}' — DSL requires double quotes around string values.")
            operator = "is" if sym == "==" else ("is not" if sym == "!=" else "is")
            conditions.append((rev_map.get(path, path), operator, value, cond_logic))
            continue

        # ── Raw / complex expression — preserve instead of failing import ─
        # Conditions using if(), is_null(), round(), days_before_now(), etc.
        # that cannot be decomposed into visual fields are stored as raw DSL.
        _short = part[:100] + ("\u2026" if len(part) > 100 else "")
        warnings.append(f"Complex expression preserved as raw DSL (condition {idx + 1}): `{_short}`")
        conditions.append((f"__raw__:{part}", "raw", "", cond_logic))

    return conditions, global_logic, errors, warnings


def _remove_condition(idx: int) -> None:
    """Remove the condition at idx by shifting all subsequent conditions' state keys down."""
    n = st.session_state.get("num_conditions", 1)
    _SCALAR = [
        "fact_{}", "op_{}", "val_{}", "custom_fact_{}", "custom_val_{}",
        "cond_logic_{}", "val_roles_{}", "perm_count_{}", "aud_count_cond_{}", "acct_count_cond_{}"
    ]
    _SUB = ["perm_val_{}_{}", "aud_cond_{}_{}", "acct_cond_{}_{}"]
    if n <= 1:
        # Reset the single remaining condition to blank
        for tpl in _SCALAR:
            st.session_state.pop(tpl.format(0), None)
        for sub in range(20):
            for tpl in _SUB:
                st.session_state.pop(tpl.format(0, sub), None)
        return
    # Shift conditions idx+1 … n-1 down to idx … n-2
    for ci in range(idx, n - 1):
        for tpl in _SCALAR:
            src, dst = tpl.format(ci + 1), tpl.format(ci)
            if src in st.session_state:
                st.session_state[dst] = st.session_state[src]
            else:
                st.session_state.pop(dst, None)
        for sub in range(20):
            for tpl in _SUB:
                src, dst = tpl.format(ci + 1, sub), tpl.format(ci, sub)
                if src in st.session_state:
                    st.session_state[dst] = st.session_state[src]
                else:
                    st.session_state.pop(dst, None)
    # Clear the now-duplicate last slot
    last = n - 1
    for tpl in _SCALAR:
        st.session_state.pop(tpl.format(last), None)
    for sub in range(20):
        for tpl in _SUB:
            st.session_state.pop(tpl.format(last, sub), None)
    st.session_state["num_conditions"] = n - 1


def apply_parsed_conditions_to_session(parsed_conditions: List[Tuple], global_logic: str) -> None:
    """Populate condition-builder session state from parsed DSL conditions."""
    # Clear previous condition keys (up to 20)
    for ci in range(20):
        for key in [
            f"fact_{ci}", f"op_{ci}", f"val_{ci}",
            f"custom_fact_{ci}", f"custom_val_{ci}",
            f"cond_logic_{ci}", f"val_roles_{ci}",
            f"perm_count_{ci}", f"aud_count_cond_{ci}", f"acct_count_cond_{ci}",
        ]:
            st.session_state.pop(key, None)
        for sub in range(20):
            st.session_state.pop(f"perm_val_{ci}_{sub}", None)
            st.session_state.pop(f"aud_cond_{ci}_{sub}", None)
            st.session_state.pop(f"acct_cond_{ci}_{sub}", None)

    st.session_state["num_conditions"] = len(parsed_conditions)
    # Stage the logic value; applied before the radio widget renders on the next rerun
    # to avoid StreamlitAPIException (cannot write widget key after instantiation).
    st.session_state["_pending_global_logic"] = global_logic

    fact_options = (
        [k for k in FACT_DSL_MAP.keys() if k != "Permissions (toArray)"]
        + ["Permissions (toArray)", "Custom Rule", "Custom Permission", "Custom"]
    )

    for i, (fact, operator, value, cond_logic) in enumerate(parsed_conditions):
        # ── Raw / complex expressions ────────────────────────────────────────
        if fact.startswith("__raw__:"):
            st.session_state[f"fact_{i}"] = "Custom DSL Expression"
            st.session_state[f"custom_fact_{i}"] = fact[len("__raw__:"):]
            if i > 0:
                st.session_state[f"cond_logic_{i}"] = cond_logic
            continue
        # Map parsed fact name back to selectbox value
        if fact in fact_options and fact not in ("Custom Rule", "Custom Permission", "Custom"):
            fact_sel = fact
        elif fact.startswith("rule."):
            fact_sel = "Custom Rule"
            st.session_state[f"custom_fact_{i}"] = fact[len("rule."):]
        elif fact.startswith("facts.permissions."):
            fact_sel = "Custom Permission"
            st.session_state[f"custom_fact_{i}"] = fact[len("facts.permissions."):]
        else:
            fact_sel = "Custom"
            st.session_state[f"custom_fact_{i}"] = fact

        st.session_state[f"fact_{i}"] = fact_sel
        st.session_state[f"op_{i}"] = operator

        if fact == "Permissions (toArray)":
            sub_paths = [s.strip() for s in value.split(",") if s.strip()]
            st.session_state[f"perm_count_{i}"] = max(1, len(sub_paths))
            for j, sp in enumerate(sub_paths):
                st.session_state[f"perm_val_{i}_{j}"] = sp
        elif fact == "User Role":
            roles = [r.strip() for r in value.split(",") if r.strip()]
            st.session_state[f"val_roles_{i}"] = roles
        elif fact == "Audience":
            auds = [a.strip() for a in value.split(",") if a.strip()]
            st.session_state[f"aud_count_cond_{i}"] = max(1, len(auds))
            for j, a in enumerate(auds):
                st.session_state[f"aud_cond_{i}_{j}"] = a
        elif fact == "Service Account ID":
            accts = [a.strip() for a in value.split(",") if a.strip()]
            st.session_state[f"acct_count_cond_{i}"] = max(1, len(accts))
            for j, a in enumerate(accts):
                st.session_state[f"acct_cond_{i}_{j}"] = a
        else:
            _dsl = FACT_DSL_MAP.get(fact, fact)
            is_flag = (
                _dsl.startswith("rule.")
                or _dsl.startswith("facts.permissions.")
                or _dsl in TRUTHY_FACTS
            )
            if not is_flag:
                avail = list(FACT_VALUES.get(fact, ["Custom"]))
                if value in avail:
                    st.session_state[f"val_{i}"] = value
                else:
                    st.session_state[f"val_{i}"] = "Custom"
                    st.session_state[f"custom_val_{i}"] = value

        if i > 0:
            st.session_state[f"cond_logic_{i}"] = cond_logic


# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:2rem;">⚡</div>
        <div style="font-weight:700;font-size:1.1rem;color:#1e293b;">XRP DSL Builder</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:0.2rem;">Test Scenario Configuration</div>
    </div>
    <hr style="margin:0.75rem 0 1rem 0 !important;">
    """, unsafe_allow_html=True)

    # Logged-in user + sign out
    _logged_user = st.session_state.get("logged_in_user", "User")
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'background:#f0f4ff;border:1px solid #e0e7ff;border-radius:10px;'
        f'padding:0.5rem 0.75rem;margin-bottom:0.75rem;">'
        f'<span style="font-size:0.8rem;font-weight:600;color:#3730a3;">👤 {_logged_user}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("🚪 Sign Out", use_container_width=True, key="signout_btn"):
        st.session_state["authenticated"] = False
        st.session_state["logged_in_user"] = ""
        st.rerun()

    st.markdown('<div class="sidebar-card-title">👤 Customer Profile</div>', unsafe_allow_html=True)
    test_device_make_list = st.multiselect("Device Make", ["Samsung", "Apple", "Google", "Motorola", "Other"], default=["Samsung"], key="device_make_ms", help="Select one or more device makes")
    test_device_make = ", ".join(test_device_make_list) if test_device_make_list else "Samsung"

    # Auto-select OS based on Device Make
    _has_apple = "Apple" in test_device_make_list
    _has_android_make = any(m in test_device_make_list for m in ["Samsung", "Google", "Motorola", "Other"])
    if _has_apple and not _has_android_make:
        _os_auto = ["iOS"]
    elif _has_android_make and not _has_apple:
        _os_auto = ["Android"]
    elif _has_apple and _has_android_make:
        _os_auto = ["Android", "iOS"]
    else:
        _os_auto = ["Android"]
    if st.session_state.get("_last_device_make") != sorted(test_device_make_list):
        st.session_state["device_os_ms"] = _os_auto
        st.session_state["_last_device_make"] = sorted(test_device_make_list)
    test_device_os_list = st.multiselect("Device OS", ["Android", "iOS"], key="device_os_ms")
    test_device_os = ", ".join(test_device_os_list) if test_device_os_list else "Android"

    test_user_role_list = st.multiselect("User Role", ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM", "MANAGER"], default=["PRIMARY"], help="Select one or more roles")
    test_user_role = ", ".join(test_user_role_list) if test_user_role_list else "PRIMARY"
    test_account_id = st.text_input("Account ID", placeholder="Enter account ID...")
    test_has_multiple = st.selectbox("Multiple Accounts", ["true", "false"])

    st.markdown('<div style="font-size:0.85rem;color:#374151;font-weight:500;margin-bottom:0.3rem;">Audience Segments</div>', unsafe_allow_html=True)
    if "audience_count" not in st.session_state:
        st.session_state["audience_count"] = 1
    _raw_audience_list = []
    for _ai in range(st.session_state["audience_count"]):
        _aud_val = st.text_input(
            f"Audience {_ai + 1}",
            key=f"audience_{_ai}",
            placeholder="e.g. HQ_Cust_XM_Income_Above50K_Legacy",
            label_visibility="collapsed",
        )
        _raw_audience_list.append(_aud_val)
    _ac1, _ac2 = st.columns(2)
    with _ac1:
        if st.button("＋ Add", key="aud_add", use_container_width=True, help="Add audience segment"):
            st.session_state["audience_count"] += 1
            st.rerun()
    with _ac2:
        if st.session_state["audience_count"] > 1:
            if st.button("－ Remove", key="aud_rem", use_container_width=True, help="Remove last segment"):
                st.session_state["audience_count"] -= 1
                st.rerun()
    test_audience_list = [a.strip() for a in _raw_audience_list if a.strip()]
    test_audience = ", ".join(test_audience_list)

    audience_display = test_audience if test_audience else '<i style="color:#94a3b8">Not set</i>'
    st.markdown(f"""
    <div class="sidebar-card" style="background:#f0f9ff;border-color:#bae6fd;">
        <div class="sidebar-card-title" style="color:#0284c7;">📊 Active Profile</div>
        <div style="font-size:0.8rem;color:#334155;line-height:1.8;">
            <b>Device Make:</b> {test_device_make}<br>
            <b>Device OS:</b> {test_device_os}<br>
            <b>Role:</b> {test_user_role}<br>
            <b>Multi-Account:</b> {test_has_multiple}<br>
            <b>Audience:</b> {audience_display}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:1.25rem 0 0.5rem 0;border-top:1px solid #e2e8f0;margin-top:0.5rem;">
        <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Developed by</div>
        <div style="font-weight:700;font-size:0.9rem;color:#1e293b;">Sakthivel Viswanathan</div>
        <div style="font-size:0.75rem;color:#6366f1;font-weight:500;">Engineer II</div>
    </div>
    """, unsafe_allow_html=True)

test_internet_backup = "false"
test_power_backup = "false"
test_show_line_level = "false"


# ==================== HEADER ====================

st.markdown("""
<div class="header-banner">
    <div class="header-left">
        <div class="header-title">⚡ XRP DSL Builder</div>
        <p class="header-sub">Build targeting rules visually &nbsp;·&nbsp; Generate DSL expressions &nbsp;·&nbsp; Test customer profiles</p>
    </div>
    <div class="header-badge">Visual Rule Engine</div>
</div>
""", unsafe_allow_html=True)


# ==================== TABS ====================

tab1, = st.tabs(["🧩 Build Rule"])


# ==================== TAB 1: BUILD RULE ====================

with tab1:
    with st.expander("📖 How to use the condition builder", expanded=False):
        st.markdown("""
### ⚡ Quick Start
Select a **Fact → Operator → Value** for each condition. The DSL is generated live in the preview panel on the right.

---

### 🔢 Operators
| Operator | Meaning | Example DSL |
|---|---|---|
| `is` | Equals | `facts.auth.user_role == "PRIMARY"` |
| `is not` | Not equals | `facts.auth.user_role != "PRIMARY"` |
| `at least (>=)` | Greater than or equal | `facts.client.version >= "6.4"` |
| `at most (<=)` | Less than or equal | `facts.client.version <= "10.0"` |
| `above (>)` | Strictly greater | `facts.client.version > "6.4"` |
| `below (<)` | Strictly less | `facts.client.version < "10.0"` |

> **Note:** Version comparisons are version-aware — `6.10` is correctly treated as greater than `6.4`.

---

### 🏷️ Boolean Flag Facts
Facts under `rule.*` or `facts.permissions.*` are **boolean flags** — no value entry needed.

| Operator | DSL Output |
|---|---|
| `is` | `rule.is_disconnected_customer` |
| `is not` | `!rule.is_disconnected_customer` |

---

### 🧩 Custom Fact Types
| Selection | What to enter | DSL generated |
|---|---|---|
| **Custom Rule** | Rule name, e.g. `has_gw_device` | `rule.has_gw_device` |
| **Custom Permission** | Permission path, e.g. `device_prioritization.view` | `facts.permissions.device_prioritization.view` |
| **Custom** | Full fact path, e.g. `facts.custom.field` | `facts.custom.field == "value"` |
| **Permissions (toArray)** | One or more sub-paths | `toArray(facts.permissions.x, facts.permissions.y) == true` |

---

### 🔗 Logic Between Conditions
- Set **Default logic** (AND / OR) at the top — applies to all conditions
- Override per-condition using the **Join condition N → N+1 with** radio below each row
- Supports up to **20 conditions**

---

### 💡 Examples
```
(facts.xcdp.realized == "HQ_Cust_Digital_Soccer_Likely" && facts.auth.user_role == "PRIMARY")

(facts.client.version >= "6.4" && rule.has_gw_device)

(!rule.is_disconnected_customer && facts.client.device.os.name == "iOS")

(toArray(facts.permissions.device_prioritization.view) == true)
```
        """)

    col_main, col_preview = st.columns([3, 2], gap="medium")

    with col_main:
        st.markdown('<div class="section-title">📋 Conditions</div>', unsafe_allow_html=True)

        if "num_conditions" not in st.session_state:
            st.session_state["num_conditions"] = 1
        num_conditions = st.session_state["num_conditions"]

        conditions = []
        sidebar_fact_values = {
            "Client Device Make": test_device_make,
            "Client Device OS Name": test_device_os,
            "User Role": test_user_role,
            "Service Account ID": test_account_id,
            "Has Multiple Accounts": test_has_multiple,
            "Audience": test_audience_list,
        }

        # Apply staged global logic from an import (must happen before the widget renders)
        if "_pending_global_logic" in st.session_state:
            st.session_state["global_logic_radio"] = st.session_state.pop("_pending_global_logic")

        global_logic = st.radio("Default logic between conditions:", ["AND", "OR"], horizontal=True,
                         key="global_logic_radio",
                         help="Default operator joining conditions. You can override per condition below.")

        for i in range(num_conditions):
            # AND/OR selector shown BETWEEN cards
            if i > 0:
                _sp1, _logic_col, _sp2 = st.columns([3, 2, 3])
                with _logic_col:
                    cond_logic = st.radio(
                        "logic",
                        ["AND", "OR"],
                        index=0 if global_logic == "AND" else 1,
                        key=f"cond_logic_{i}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
            else:
                cond_logic = global_logic

            _hdr_lbl, _hdr_del = st.columns([11, 1])
            with _hdr_lbl:
                st.markdown(
                    f'<div style="display:flex;align-items:center;padding:0.3rem 0 0.3rem 0;">'
                    f'<span class="cond-badge">{i+1}</span>'
                    f'<span style="font-size:0.74rem;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.6px;">Condition {i+1}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with _hdr_del:
                st.markdown('<div class="rem-cond-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_cond_{i}", help=f"Remove condition {i+1}", use_container_width=True):
                    _remove_condition(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns([3, 2, 2.2])
            with c1:
                st.markdown('<span class="field-label">Fact</span>', unsafe_allow_html=True)
                fact_options = [k for k in FACT_DSL_MAP.keys() if k != "Permissions (toArray)"] + ["Permissions (toArray)", "Custom Rule", "Custom Permission", "Custom", "Custom DSL Expression"]
                fact_selection = st.selectbox("Fact", fact_options, key=f"fact_{i}", label_visibility="collapsed")
                if fact_selection == "Custom":
                    fact = st.text_input("Custom fact path", key=f"custom_fact_{i}", placeholder="facts.custom.field", label_visibility="collapsed")
                elif fact_selection == "Custom Rule":
                    rule_input = st.text_input("Rule name", key=f"custom_fact_{i}", placeholder="e.g. edp_state_features_auto_optimization", label_visibility="collapsed")
                    fact = f"rule.{rule_input.strip()}" if rule_input.strip() else "Custom Rule"
                elif fact_selection == "Custom Permission":
                    perm_input = st.text_input("Permission path", key=f"custom_fact_{i}", placeholder="e.g. device_prioritization.view", label_visibility="collapsed")
                    fact = f"facts.permissions.{perm_input.strip()}" if perm_input.strip() else "Custom Permission"
                elif fact_selection == "Custom DSL Expression":
                    _raw_dsl_input = st.text_area(
                        "Raw DSL expression",
                        key=f"custom_fact_{i}",
                        placeholder="e.g. if(!is_null(facts.x), round(y/60,0)>=1, round(z/60,0)>=1)",
                        height=72,
                        label_visibility="collapsed",
                    )
                    fact = f"__raw__:{_raw_dsl_input.strip()}" if _raw_dsl_input.strip() else "__raw__:"
                else:
                    fact = fact_selection
            with c2:
                if fact_selection == "Custom DSL Expression":
                    operator = "raw"
                    st.markdown('<span class="field-label">Operator</span>', unsafe_allow_html=True)
                    st.caption("N/A")
                else:
                    st.markdown('<span class="field-label">Operator</span>', unsafe_allow_html=True)
                    operator = st.selectbox("Operator", ["is", "is not", "at least (>=)", "at most (<=)", "above (>)", "below (<)"], key=f"op_{i}", label_visibility="collapsed")
            with c3:
                st.markdown('<span class="field-label">Value</span>', unsafe_allow_html=True)
                if fact_selection == "Custom DSL Expression":
                    value = ""
                    st.caption("N/A \u2014 value is embedded in the raw expression above")
                elif fact == "Permissions (toArray)":
                    st.markdown(
                        '<span style="font-size:0.75rem;color:#6366f1;font-weight:600;">Base: </span>'
                        '<code style="font-size:0.75rem;background:#e0e7ff;padding:0.1rem 0.4rem;border-radius:4px;">facts.permissions</code>'
                        '<span style="font-size:0.72rem;color:#64748b;"> — add each sub-path separately</span>',
                        unsafe_allow_html=True
                    )
                    perm_count_key = f"perm_count_{i}"
                    if perm_count_key not in st.session_state:
                        st.session_state[perm_count_key] = 1
                    perm_vals = []
                    for j in range(st.session_state[perm_count_key]):
                        perm_val = st.text_input(
                            f"Sub-path {j+1}",
                            key=f"perm_val_{i}_{j}",
                            placeholder=".advanced security_on the go.view all devices",
                            label_visibility="visible"
                        )
                        perm_vals.append(perm_val)
                    value = ", ".join(v.strip() for v in perm_vals if v.strip())
                elif fact == "Audience":
                    _aud_count_key = f"aud_count_cond_{i}"
                    if _aud_count_key not in st.session_state:
                        # Auto-fill from sidebar audience on first render
                        _sidebar_aud = test_audience_list if test_audience_list else []
                        st.session_state[_aud_count_key] = max(1, len(_sidebar_aud))
                        for _aj, _sv in enumerate(_sidebar_aud):
                            _aud_init_key = f"aud_cond_{i}_{_aj}"
                            if _aud_init_key not in st.session_state:
                                st.session_state[_aud_init_key] = _sv
                    _aud_cond_vals = []
                    for _aj in range(st.session_state[_aud_count_key]):
                        _av = st.text_input(
                            f"Audience {_aj + 1}",
                            key=f"aud_cond_{i}_{_aj}",
                            placeholder="e.g. HQ_Cust_Digital_Soccer_Likely",
                            label_visibility="visible",
                        )
                        _aud_cond_vals.append(_av)
                    value = ", ".join(v.strip() for v in _aud_cond_vals if v.strip())
                elif fact == "Service Account ID":
                    _acct_count_key = f"acct_count_cond_{i}"
                    if _acct_count_key not in st.session_state:
                        st.session_state[_acct_count_key] = 1
                    _acct_cond_vals = []
                    for _aj in range(st.session_state[_acct_count_key]):
                        _av = st.text_input(
                            f"Account ID {_aj + 1}",
                            key=f"acct_cond_{i}_{_aj}",
                            placeholder="Enter account ID...",
                            label_visibility="visible",
                        )
                        _acct_cond_vals.append(_av)
                    value = ", ".join(v.strip() for v in _acct_cond_vals if v.strip())
                elif fact == "User Role":
                    _role_key = f"val_roles_{i}"
                    # On first render, auto-fill from sidebar selection
                    if _role_key not in st.session_state:
                        st.session_state[_role_key] = [r for r in test_user_role_list if r in FACT_VALUES.get("User Role", [])]
                    _selected_roles = st.multiselect(
                        "Role(s)",
                        FACT_VALUES.get("User Role", []),
                        key=_role_key,
                        label_visibility="collapsed",
                    )
                    value = ", ".join(_selected_roles) if _selected_roles else ""
                else:
                    # Resolve DSL path to determine if this is a boolean flag fact
                    _dsl = FACT_DSL_MAP.get(fact, fact)
                    is_flag_fact = (
                        _dsl.startswith("rule.")
                        or _dsl.startswith("facts.permissions.")
                        or _dsl in TRUTHY_FACTS
                    )
                    if is_flag_fact:
                        value = "true"  # operator (is / is not) controls the ! prefix in DSL
                        st.markdown(
                            '<span style="font-size:0.8rem;color:#6366f1;font-weight:600;">Boolean flag</span>'
                            '<br><span style="font-size:0.75rem;color:#64748b;">Use <b>is</b> → <code>rule.X</code> &nbsp;|&nbsp; <b>is not</b> → <code>!rule.X</code></span>',
                            unsafe_allow_html=True
                        )
                    else:
                        available_values = list(FACT_VALUES.get(fact, ["Custom"]))
                        sidebar_val = sidebar_fact_values.get(fact, "")
                        if isinstance(sidebar_val, list):
                            for _sv in sidebar_val:
                                if _sv and _sv not in available_values:
                                    available_values = [_sv] + available_values
                        elif sidebar_val and sidebar_val not in available_values:
                            available_values = [sidebar_val] + available_values
                        if len(available_values) == 1 and available_values[0] == "Custom":
                            value = st.text_input("Value", key=f"val_{i}", placeholder="Enter value...", label_visibility="collapsed")
                        else:
                            options = available_values + (["Custom"] if "Custom" not in available_values else [])
                            selected = st.selectbox("Value", options, key=f"val_{i}", label_visibility="collapsed")
                            if selected == "Custom":
                                value = st.text_input("Custom value", key=f"custom_val_{i}", placeholder="Enter custom value...", label_visibility="collapsed")
                            else:
                                value = selected
            # ＋ / － buttons for multi-value facts — placed outside columns
            if fact == "Permissions (toArray)":
                _pc1, _pc2, _ = st.columns([1, 1, 6])
                with _pc1:
                    if st.button("＋", key=f"perm_add_{i}", use_container_width=True, help="Add sub-path"):
                        st.session_state[f"perm_count_{i}"] += 1
                        st.rerun()
                with _pc2:
                    if st.session_state.get(f"perm_count_{i}", 1) > 1:
                        if st.button("－", key=f"perm_rem_{i}", use_container_width=True, help="Remove last sub-path"):
                            st.session_state[f"perm_count_{i}"] -= 1
                            st.rerun()

            if fact == "Audience":
                _ac1, _ac2, _ = st.columns([1, 1, 6])
                with _ac1:
                    if st.button("＋", key=f"aud_cond_add_{i}", use_container_width=True, help="Add audience"):
                        st.session_state[f"aud_count_cond_{i}"] = st.session_state.get(f"aud_count_cond_{i}", 1) + 1
                        st.rerun()
                with _ac2:
                    if st.session_state.get(f"aud_count_cond_{i}", 1) > 1:
                        if st.button("－", key=f"aud_cond_rem_{i}", use_container_width=True, help="Remove last audience"):
                            st.session_state[f"aud_count_cond_{i}"] -= 1
                            st.rerun()

            if fact == "Service Account ID":
                _sc1, _sc2, _ = st.columns([1, 1, 6])
                with _sc1:
                    if st.button("＋", key=f"acct_cond_add_{i}", use_container_width=True, help="Add account ID"):
                        st.session_state[f"acct_count_cond_{i}"] = st.session_state.get(f"acct_count_cond_{i}", 1) + 1
                        st.rerun()
                with _sc2:
                    if st.session_state.get(f"acct_count_cond_{i}", 1) > 1:
                        if st.button("－", key=f"acct_cond_rem_{i}", use_container_width=True, help="Remove last account ID"):
                            st.session_state[f"acct_count_cond_{i}"] -= 1
                            st.rerun()

            conditions.append((fact, operator, value, cond_logic))
            st.markdown('<hr style="margin:0.6rem 0 0 0;border-top:1px solid #e0e7ff;">', unsafe_allow_html=True)

        # ── Add / Remove Condition buttons ────────────────────
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        _btn_add, _btn_rem, _ = st.columns([4, 3, 3])
        with _btn_add:
            if st.button("+ Add Condition", key="add_cond_btn", use_container_width=True):
                if st.session_state["num_conditions"] < 20:
                    st.session_state["num_conditions"] += 1
                    st.rerun()
        with _btn_rem:
            if num_conditions > 1:
                if st.button("－  Remove Last", key="rem_cond_btn", use_container_width=True):
                    st.session_state["num_conditions"] -= 1
                    st.rerun()

        logic = global_logic

    with col_preview:
        st.markdown('<div class="section-title">⚡ Live DSL Preview</div>', unsafe_allow_html=True)
        try:
            live_dsl = generate_dsl(conditions, logic)
            payload_dsl = live_dsl or "No conditions defined"
        except ValueError:
            live_dsl = ""
            payload_dsl = "Invalid conditions"
        if live_dsl:
            st.markdown(f'<div class="dsl-box">{live_dsl}</div>', unsafe_allow_html=True)
            with st.expander("📋 Copy DSL", expanded=False):
                st.code(live_dsl, language="javascript")
            st.markdown("**Condition Breakdown**")
            for i, (f, op, v, cl) in enumerate(conditions):
                if f.startswith("__raw__:"):
                    expr = f[len("__raw__:"):]
                    join_label = f" **{cl}**" if i < len(conditions) - 1 else ""
                    st.markdown(f"`{i+1}.` `{expr}`{join_label}")
                    continue
                dsl_path = FACT_DSL_MAP.get(f, f)
                if dsl_path == "__toarray__":
                    base = TO_ARRAY_FACTS.get(f, "facts.permissions")
                    full_paths = _resolve_perm_paths(v, base)
                    bool_val = "false" if op == "is not" else "true"
                    expr = f'toArray({", ".join(full_paths)}) == {bool_val}'
                elif (dsl_path.startswith("rule.") or dsl_path in TRUTHY_FACTS or dsl_path.startswith("facts.permissions.")) and v.lower() in ["true", "false"]:
                    expr = f"!{dsl_path}" if op == "is not" else dsl_path
                elif dsl_path in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
                    _vals = [_v.strip() for _v in v.split(",") if _v.strip()]
                    if len(_vals) > 1:
                        _vals_str = ", ".join(f'"{_v}"' for _v in _vals)
                        _dsl_op = "!=" if op == "is not" else "=="
                        expr = f'{dsl_path} {_dsl_op} to_array({_vals_str})'
                    else:
                        expr = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
                elif op in COMPARISON_OP_MAP and dsl_path == "facts.client.version":
                    expr = f'version_compare({dsl_path}, "{v}") {COMPARISON_OP_MAP[op]} 0'
                elif op in COMPARISON_OP_MAP:
                    expr = f'{dsl_path} {COMPARISON_OP_MAP[op]} "{v}"'
                else:
                    expr = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
                join_label = f" **{cl}**" if i < len(conditions) - 1 else ""
                st.markdown(f"`{i+1}.` `{expr}`{join_label}")
        elif payload_dsl == "Invalid conditions":
            st.markdown('<div class="dsl-box"><span class="dsl-empty">Fill in all values to see DSL preview...</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="dsl-box"><span class="dsl-empty">DSL will appear here as you build conditions...</span></div>', unsafe_allow_html=True)

        # ── PAYLOAD SECTION temporarily hidden ──────────────
        # st.markdown('<div class="section-title">📦 Payload</div>', unsafe_allow_html=True)
        # render_type_options = [...]
        # st.json(example_payload)

    # ==================== DSL VALIDATOR ====================

    st.markdown('<hr style="margin:1.2rem 0 1rem 0 !important;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 DSL Validator &amp; Import</div>', unsafe_allow_html=True)
    st.caption("Paste an existing DSL expression to validate it and auto-fill the condition builder above.")

    _val_left, _val_right = st.columns([5, 1], gap="small")
    with _val_left:
        dsl_input = st.text_area(
            "DSL Expression",
            key="dsl_validator_input",
            placeholder='(facts.auth.user_role == "PRIMARY" && facts.client.device.os.name == "iOS")',
            height=85,
            label_visibility="collapsed",
        )
    with _val_right:
        st.markdown('<div style="height:0.55rem"></div>', unsafe_allow_html=True)
        _import_clicked = st.button("⬆️ Import", key="dsl_import_btn", use_container_width=True,
                                     help="Parse the DSL and fill the condition builder",
                                     disabled=(not bool((dsl_input or "").strip())))

    if (dsl_input or "").strip():
        _parsed_conds, _parsed_logic, _parse_errors, _parse_warnings = parse_dsl_to_conditions(dsl_input.strip())

        if _parse_errors:
            for _err in _parse_errors:
                st.error(f"⛔ {_err}")
        if _parse_warnings:
            for _warn in _parse_warnings:
                st.warning(f"⚠️ {_warn}")
        if not _parse_errors and _parsed_conds:
            st.success(f"✅ Valid DSL — {len(_parsed_conds)} condition(s) found · Logic: **{_parsed_logic}**")
            with st.expander("📋 Parsed Condition Breakdown", expanded=True):
                for _pi, (_pf, _pop, _pv, _pcl) in enumerate(_parsed_conds):
                    if _pi > 0:
                        st.markdown(
                            f'<div style="text-align:center;font-size:0.7rem;font-weight:800;'
                            f'color:#4f46e5;letter-spacing:0.5px;margin:0.15rem 0;">── {_pcl} ──</div>',
                            unsafe_allow_html=True
                        )
                    _dsl_preview = FACT_DSL_MAP.get(_pf, _pf)
                    if _pf.startswith("__raw__:"):
                        _expr_preview = _pf[len("__raw__:"):]
                    elif _dsl_preview == "__toarray__":
                        _expr_preview = f'toArray(facts.permissions.{_pv}) == true'
                    elif (_dsl_preview.startswith("rule.") or _dsl_preview.startswith("facts.permissions.") or _dsl_preview in TRUTHY_FACTS) and _pv.lower() in ("true", "false"):
                        _expr_preview = f"!{_dsl_preview}" if _pop == "is not" else _dsl_preview
                    elif _pop in COMPARISON_OP_MAP and _dsl_preview == "facts.client.version":
                        _expr_preview = f'version_compare({_dsl_preview}, "{_pv}") {COMPARISON_OP_MAP[_pop]} 0'
                    elif _dsl_preview in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
                        _vals_p = [v.strip() for v in _pv.split(",") if v.strip()]
                        _dsl_op = "!=" if _pop == "is not" else "=="
                        if len(_vals_p) > 1:
                            _vals_p_str = ", ".join(f'"{v}"' for v in _vals_p)
                            _expr_preview = f'{_dsl_preview} {_dsl_op} to_array({_vals_p_str})'
                        else:
                            _expr_preview = f'{_dsl_preview} {_dsl_op} "{_pv.strip()}"'
                    else:
                        _dsl_op = "!=" if _pop == "is not" else (COMPARISON_OP_MAP.get(_pop, "=="))
                        _expr_preview = f'{_dsl_preview} {_dsl_op} "{_pv}"'
                    st.markdown(
                        f'<div style="background:#f5f7ff;border-left:3px solid #6366f1;border-radius:0 8px 8px 0;'
                        f'padding:0.35rem 0.75rem;font-family:monospace;font-size:0.82rem;color:#1e293b;margin-bottom:0.2rem;">'
                        f'<span style="color:#94a3b8;margin-right:0.5rem;">#{_pi+1}</span>{_expr_preview}</div>',
                        unsafe_allow_html=True
                    )

        if _import_clicked and not _parse_errors and _parsed_conds:
            apply_parsed_conditions_to_session(_parsed_conds, _parsed_logic)
            st.session_state.pop("dsl_validator_input", None)
            st.rerun()
        elif _import_clicked and _parse_errors:
            st.error("Cannot import — fix the errors above first.")
