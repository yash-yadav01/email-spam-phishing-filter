"""
app.py
======
AI-Based Email Spam and Phishing Detection System
Author: Yash Yadav

Streamlit application — main entry point (Email Analyzer).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

# ── Ensure project root is on sys.path so `src` package is importable ─────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Email Spam & Phishing Filter",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODELS_DIR    = PROJECT_ROOT / "models"
RESULTS_JSON  = MODELS_DIR / "training_results.json"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #f0f4f8 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}
[data-testid="stSidebar"] a {
    color: #93c5fd !important;
    text-decoration: none !important;
    font-weight: 500;
}
[data-testid="stSidebar"] a:hover {
    color: #bfdbfe !important;
}

/* ── Main content wrapper ── */
[data-testid="stMain"] > div:first-child {
    padding: 1.5rem 2rem !important;
}

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 60%, #1d4ed8 100%);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 16px rgba(30,64,175,0.18);
}
.page-header-icon {
    font-size: 2.4rem;
    line-height: 1;
    flex-shrink: 0;
}
.page-header-title {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    letter-spacing: -0.02em;
}
.page-header-subtitle {
    color: #bfdbfe;
    font-size: 0.875rem;
    margin: 0.25rem 0 0 0;
    line-height: 1.4;
}

/* ── Section card ── */
.section-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(15,23,42,0.06);
}
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.4rem;
}

/* ── Quick example buttons ── */
.stButton > button {
    width: 100%;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    box-shadow: 0 2px 8px rgba(30,64,175,0.15) !important;
}

/* ── Analyze / Clear buttons ── */
[data-testid="stButton"] button[kind="primary"] {
    background: #1e40af !important;
    border-color: #1e40af !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.55rem 2rem !important;
    border-radius: 8px !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    box-shadow: 0 4px 12px rgba(29,78,216,0.3) !important;
}

/* ── Result metric cards ── */
.result-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(15,23,42,0.06);
}
.result-card-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.5rem;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.badge-legitimate  { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.badge-spam        { background: #fff7ed; color: #9a3412; border: 1px solid #fdba74; }
.badge-phishing    { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }
.badge-low         { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.badge-medium      { background: #fff7ed; color: #9a3412; border: 1px solid #fdba74; }
.badge-high        { background: #fef2f2; color: #991b1b; border: 1px solid #fca5a5; }

/* ── Indicator list ── */
.indicator-item {
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    border-radius: 0 6px 6px 0;
    padding: 0.45rem 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.875rem;
    color: #7f1d1d;
}

/* ── Privacy note ── */
.privacy-note {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 0.65rem 1rem;
    font-size: 0.8rem;
    color: #0c4a6e;
}

/* ── Divider ── */
.styled-hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.25rem 0;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.75rem;
    padding: 1rem 0 0.25rem 0;
    border-top: 1px solid #e2e8f0;
    margin-top: 1.5rem;
}

/* ── focus rings ── */
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    outline: none !important;
}

/* ── Metric label text ── */
[data-testid="stMetricLabel"] { font-size: 0.78rem !important; }

@media (max-width: 768px) {
    [data-testid="stMain"] > div:first-child { padding: 1rem !important; }
    .page-header { padding: 1rem 1.25rem; }
    .page-header-title { font-size: 1.2rem; }
}
</style>
""", unsafe_allow_html=True)


# ── Load model artefacts once ─────────────────────────────────────────────────
@st.cache_resource
def load_model():
    """Load prediction pipeline artefacts once."""
    try:
        from src.predict import load_artefacts, predict as _predict
        load_artefacts()
        return _predict
    except FileNotFoundError as exc:
        return str(exc)


# ── Helper: label styling ─────────────────────────────────────────────────────
_LABEL_COLOR = {
    "legitimate": "#22c55e",
    "spam":       "#f97316",
    "phishing":   "#ef4444",
}
_RISK_COLOR = {
    "LOW":    "#22c55e",
    "MEDIUM": "#f97316",
    "HIGH":   "#ef4444",
}

_BADGE_CLASS = {
    "legitimate": "badge-legitimate",
    "spam":       "badge-spam",
    "phishing":   "badge-phishing",
    "LOW":        "badge-low",
    "MEDIUM":     "badge-medium",
    "HIGH":       "badge-high",
}


def _badge(text: str, key: str) -> str:
    cls = _BADGE_CLASS.get(key.upper() if key.upper() in _BADGE_CLASS else key.lower(), "badge-spam")
    return f'<span class="badge {cls}">{text}</span>'


def _colored_badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color};color:white;padding:4px 12px;'
        f'border-radius:6px;font-weight:bold;">{text}</span>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:0.5rem 0 0.75rem 0;">
  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
    <span style="font-size:1.6rem;">🛡️</span>
    <span style="font-size:1.05rem;font-weight:700;color:#f8fafc;letter-spacing:-0.01em;">Email Filter</span>
  </div>
  <div style="font-size:0.78rem;color:#94a3b8;line-height:1.5;">
    AI-Based Spam &amp; Phishing Detection<br>
    <span style="color:#64748b;">by Yash Yadav</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<hr style="border-color:#334155;margin:0.5rem 0;">', unsafe_allow_html=True)
st.sidebar.markdown('<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;color:#64748b;text-transform:uppercase;margin-bottom:0.5rem;">Navigation</div>', unsafe_allow_html=True)
st.sidebar.page_link("app.py",                   label="🔍 Email Analyzer")
st.sidebar.page_link("pages/1_model_info.py",    label="📊 Model Information")
st.sidebar.page_link("pages/2_dataset_stats.py", label="📂 Dataset Statistics")
st.sidebar.page_link("pages/3_evaluation.py",    label="📈 Model Evaluation")
st.sidebar.page_link("pages/4_about.py",         label="ℹ️ About & Limitations")
st.sidebar.markdown('<hr style="border-color:#334155;margin:0.75rem 0 0.5rem 0;">', unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="font-size:0.72rem;color:#64748b;line-height:1.6;">
  <div style="margin-bottom:0.3rem;">🔒 <strong style="color:#94a3b8;">No URLs visited</strong></div>
  <div style="margin-bottom:0.3rem;">📵 <strong style="color:#94a3b8;">No content stored</strong></div>
  <div>🖥️ <strong style="color:#94a3b8;">Local inference only</strong></div>
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">🛡️</div>
  <div>
    <p class="page-header-title">Email Security Analyzer</p>
    <p class="page-header-subtitle">
      Classify emails as Legitimate, Spam, or Phishing using NLP + Machine Learning + Heuristic Risk Engine
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────────

# Apply any staged values from quick-example / clear buttons BEFORE widgets render
for _key in ("subject", "body"):
    _stage = f"_{_key}_stage"
    if _stage in st.session_state:
        st.session_state[_key] = st.session_state.pop(_stage)

col1, col2 = st.columns([3, 1], gap="medium")

with col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Email Input</div>', unsafe_allow_html=True)
    subject_input = st.text_input(
        "Subject",
        placeholder="e.g. Your account has been suspended",
        key="subject",
        label_visibility="visible",
    )
    body_input = st.text_area(
        "Email Body",
        height=200,
        placeholder="Paste the full email body here…",
        key="body",
        label_visibility="visible",
    )
    st.markdown('<div class="privacy-note">🔒 Email content is analyzed locally by this application\'s pipeline. No content is transmitted or stored.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Quick Examples</div>', unsafe_allow_html=True)
    if st.button("📬 Legitimate", use_container_width=True):
        st.session_state["_subject_stage"] = "Meeting rescheduled to 3pm"
        st.session_state["_body_stage"] = (
            "Hi team,\n\nThe weekly sync has been moved to 3:00 PM on Thursday. "
            "Please update your calendars accordingly.\n\nBest,\nAlice"
        )
        st.rerun()
    if st.button("📧 Spam", use_container_width=True):
        st.session_state["_subject_stage"] = "WIN $1,000,000 — Claim NOW!!!"
        st.session_state["_body_stage"] = (
            "Congratulations! You have been selected as the winner of our lottery! "
            "Click here to claim your prize money of one million dollars!!!! "
            "Limited time offer — act now before it expires!!!"
        )
        st.rerun()
    if st.button("🎣 Phishing", use_container_width=True):
        st.session_state["_subject_stage"] = "Urgent: Verify your account immediately"
        st.session_state["_body_stage"] = (
            "Dear Customer,\n\nWe have detected suspicious activity on your account. "
            "Your account will be suspended within 24 hours unless you verify your credentials.\n\n"
            "Click here to login: http://192.168.1.1/verify-account\n\n"
            "Enter your username, password, and credit card details to confirm your identity.\n\n"
            "This is urgent. Act immediately to avoid account termination."
        )
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Action buttons ─────────────────────────────────────────────────────────────
st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
analyze_col, clear_col, _ = st.columns([2, 1, 4])
analyze = analyze_col.button("🔍 Analyze Email", type="primary", use_container_width=True)
if clear_col.button("🗑️ Clear", use_container_width=True):
    st.session_state["_subject_stage"] = ""
    st.session_state["_body_stage"]    = ""
    st.rerun()

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze:
    if not subject_input.strip() and not body_input.strip():
        st.warning("⚠️ Please enter an email subject or body before analyzing.")
    else:
        predict_fn = load_model()

        if isinstance(predict_fn, str):
            st.error(
                f"**Model not loaded:** {predict_fn}\n\n"
                "To use the analyzer, first train the model:\n\n"
                "```\npython -m src.prepare_dataset\npython -m src.train\n```"
            )
        else:
            with st.spinner("Analyzing email…"):
                try:
                    result = predict_fn(subject=subject_input, body=body_input)
                except Exception as exc:
                    st.error(f"Prediction error: {exc}")
                    result = None

            if result:
                st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
                st.markdown("""
<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748b;margin-bottom:0.75rem;">
  Analysis Results
</div>
""", unsafe_allow_html=True)

                r1, r2, r3 = st.columns(3, gap="medium")

                lbl = result["ml_label"]
                lbl_badge = _badge(result["display_label"], lbl)
                with r1:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-label">Classification</div>', unsafe_allow_html=True)
                    st.markdown(lbl_badge, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                risk = result["risk_level"]
                risk_badge = _badge(f"{risk} Risk", risk)
                with r2:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-label">Phishing Risk Level</div>', unsafe_allow_html=True)
                    st.markdown(risk_badge, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with r3:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="result-card-label">Confidence</div>', unsafe_allow_html=True)
                    if result["confidence_available"] and result["confidence"] is not None:
                        st.progress(result["confidence"])
                        st.caption(f"{result['confidence']:.1%}")
                    else:
                        st.caption("N/A for this model")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)

                # Explanation
                st.markdown("**💬 Explanation**")
                st.info(result["explanation"])

                # Triggered indicators
                indicators = result["triggered_indicators"]
                if indicators:
                    st.markdown("**🚨 Triggered Security Indicators**")
                    for ind in indicators:
                        st.markdown(f'<div class="indicator-item">⚠ {ind}</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ No phishing indicators triggered.")

                # Disclaimer
                st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
                st.caption(
                    "⚠️ **Disclaimer:** This tool is an AI-based analysis aid. "
                    "It does not guarantee detection of all spam or phishing emails. "
                    "Do not rely solely on this tool for security decisions. "
                    "Submitted email content is not stored."
                )

# ── Footer ────────────────────────────────────────────────────────────────────
if not analyze:
    st.markdown("""
<div class="app-footer">
  🛡️ Email Spam &amp; Phishing Filter &mdash; AI-Based detection using NLP + ML + Heuristic Risk Engine &nbsp;|&nbsp;
  No URLs visited &nbsp;|&nbsp; No email content stored
</div>
""", unsafe_allow_html=True)
