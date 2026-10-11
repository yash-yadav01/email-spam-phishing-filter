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


def _colored_badge(text: str, color: str) -> str:
    return (
        f'<span style="background:{color};color:white;padding:4px 12px;'
        f'border-radius:6px;font-weight:bold;">{text}</span>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🛡️ Email Filter")
st.sidebar.markdown(
    "**AI-Based Email Spam and Phishing Detection**\n\n"
    "Enter an email below to classify it and receive a phishing risk assessment."
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Navigation**")
st.sidebar.page_link("app.py",                   label="🔍 Email Analyzer")
st.sidebar.page_link("pages/1_model_info.py",    label="📊 Model Information")
st.sidebar.page_link("pages/2_dataset_stats.py", label="📂 Dataset Statistics")
st.sidebar.page_link("pages/3_evaluation.py",    label="📈 Model Evaluation")
st.sidebar.page_link("pages/4_about.py",         label="ℹ️ About & Limitations")

# ── Main page ─────────────────────────────────────────────────────────────────
st.title("🛡️ Email Spam & Phishing Detector")
st.markdown(
    "Classify an email as **Legitimate**, **Spam**, or **Phishing**, "
    "and receive a heuristic phishing risk assessment with triggered indicators."
)
st.markdown("---")

# ── Input form ────────────────────────────────────────────────────────────────

# Apply any staged values from quick-example / clear buttons BEFORE widgets render
for _key in ("subject", "body"):
    _stage = f"_{_key}_stage"
    if _stage in st.session_state:
        st.session_state[_key] = st.session_state.pop(_stage)

col1, col2 = st.columns([3, 1])

with col1:
    subject_input = st.text_input(
        "📧 Email Subject",
        placeholder="e.g. Your account has been suspended",
        key="subject",
    )

with col1:
    body_input = st.text_area(
        "📄 Email Body",
        height=220,
        placeholder="Paste the email body here …",
        key="body",
    )

with col2:
    st.markdown("### Quick Examples")
    if st.button("📬 Legitimate"):
        st.session_state["_subject_stage"] = "Meeting rescheduled to 3pm"
        st.session_state["_body_stage"] = (
            "Hi team,\n\nThe weekly sync has been moved to 3:00 PM on Thursday. "
            "Please update your calendars accordingly.\n\nBest,\nAlice"
        )
        st.rerun()
    if st.button("📧 Spam"):
        st.session_state["_subject_stage"] = "WIN $1,000,000 — Claim NOW!!!"
        st.session_state["_body_stage"] = (
            "Congratulations! You have been selected as the winner of our lottery! "
            "Click here to claim your prize money of one million dollars!!!! "
            "Limited time offer — act now before it expires!!!"
        )
        st.rerun()
    if st.button("🎣 Phishing"):
        st.session_state["_subject_stage"] = "Urgent: Verify your account immediately"
        st.session_state["_body_stage"] = (
            "Dear Customer,\n\nWe have detected suspicious activity on your account. "
            "Your account will be suspended within 24 hours unless you verify your credentials.\n\n"
            "Click here to login: http://192.168.1.1/verify-account\n\n"
            "Enter your username, password, and credit card details to confirm your identity.\n\n"
            "This is urgent. Act immediately to avoid account termination."
        )
        st.rerun()

st.markdown("---")

# ── Analysis ──────────────────────────────────────────────────────────────────
analyze_col, clear_col, _ = st.columns([2, 1, 4])
analyze = analyze_col.button("🔍 Analyze Email", type="primary")
if clear_col.button("🗑️ Clear"):
    st.session_state["_subject_stage"] = ""
    st.session_state["_body_stage"]    = ""
    st.rerun()

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
            with st.spinner("Analyzing …"):
                try:
                    result = predict_fn(subject=subject_input, body=body_input)
                except Exception as exc:
                    st.error(f"Prediction error: {exc}")
                    result = None

            if result:
                st.markdown("## 📋 Analysis Results")
                r1, r2, r3 = st.columns(3)

                lbl = result["ml_label"]
                lbl_color = _LABEL_COLOR.get(lbl, "#94a3b8")
                r1.markdown("**Classification**")
                r1.markdown(
                    _colored_badge(result["display_label"], lbl_color),
                    unsafe_allow_html=True,
                )

                risk = result["risk_level"]
                risk_color = _RISK_COLOR.get(risk, "#94a3b8")
                r2.markdown("**Phishing Risk**")
                r2.markdown(
                    _colored_badge(risk, risk_color),
                    unsafe_allow_html=True,
                )

                r3.markdown("**Confidence**")
                if result["confidence_available"] and result["confidence"] is not None:
                    r3.progress(result["confidence"])
                    r3.caption(f"{result['confidence']:.1%}")
                else:
                    r3.caption("N/A for this model")

                st.markdown("---")

                # Explanation
                st.markdown("### 💬 Explanation")
                st.info(result["explanation"])

                # Triggered indicators
                indicators = result["triggered_indicators"]
                if indicators:
                    st.markdown("### 🚨 Triggered Indicators")
                    for ind in indicators:
                        st.markdown(f"- {ind}")
                else:
                    st.success("✅ No phishing indicators triggered.")

                # Disclaimer
                st.markdown("---")
                st.caption(
                    "⚠️ **Disclaimer:** This tool is an AI-based analysis aid. "
                    "It does not guarantee detection of all spam or phishing emails. "
                    "Do not rely solely on this tool for security decisions. "
                    "Submitted email content is not stored."
                )

# Footer if no analysis
if not analyze:
    st.markdown("---")
    st.caption(
        "🛡️ Email Spam & Phishing Filter — "
        "AI-Based detection using NLP + ML + Heuristic Risk Engine. "
        "No URLs are visited. No email content is stored."
    )
