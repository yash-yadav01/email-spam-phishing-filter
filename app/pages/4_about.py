"""About & Limitations page."""
import streamlit as st

st.set_page_config(page_title="About & Limitations", page_icon="ℹ️", layout="wide")

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { background: #f0f4f8 !important; }
[data-testid="stSidebar"] { background: #0f172a !important; border-right: 1px solid #1e293b; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] a { color: #93c5fd !important; text-decoration: none !important; font-weight: 500; }
[data-testid="stSidebar"] a:hover { color: #bfdbfe !important; }
[data-testid="stMain"] > div:first-child { padding: 1.5rem 2rem !important; }
.page-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 60%, #1d4ed8 100%);
    border-radius: 12px; padding: 1.25rem 2rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 4px 16px rgba(30,64,175,0.18);
}
.page-header-icon { font-size: 2rem; line-height: 1; flex-shrink: 0; }
.page-header-title { color: #ffffff; font-size: 1.4rem; font-weight: 700; margin: 0; line-height: 1.2; }
.page-header-subtitle { color: #bfdbfe; font-size: 0.82rem; margin: 0.2rem 0 0 0; }
.info-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1.25rem 1.5rem; margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(15,23,42,0.06);
}
.card-section-title {
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #64748b; margin-bottom: 0.75rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9;
}
.security-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0; border-bottom: 1px solid #f8fafc; font-size: 0.875rem;
}
.security-row:last-child { border-bottom: none; }
.security-key { color: #334155; font-weight: 500; }
.badge-ok  { display:inline-block; background:#dcfce7; color:#166534; border:1px solid #86efac; border-radius:5px; padding:0.1rem 0.55rem; font-size:0.75rem; font-weight:700; }
.badge-no  { display:inline-block; background:#fef2f2; color:#991b1b; border:1px solid #fca5a5; border-radius:5px; padding:0.1rem 0.55rem; font-size:0.75rem; font-weight:700; }
.limit-item {
    background: #f8fafc; border-left: 3px solid #94a3b8; border-radius: 0 6px 6px 0;
    padding: 0.5rem 0.85rem; margin-bottom: 0.4rem; font-size: 0.875rem; color: #334155;
}
.future-item {
    background: #f0f9ff; border-left: 3px solid #38bdf8; border-radius: 0 6px 6px 0;
    padding: 0.5rem 0.85rem; margin-bottom: 0.4rem; font-size: 0.875rem; color: #0c4a6e;
}
.disclaimer-box {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
    padding: 0.85rem 1.1rem; font-size: 0.85rem; color: #78350f; margin-top: 0.5rem;
}
.styled-hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.25rem 0; }
@media (max-width: 768px) {
    [data-testid="stMain"] > div:first-child { padding: 1rem !important; }
    .page-header { padding: 1rem 1.25rem; }
    .page-header-title { font-size: 1.1rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">ℹ️</div>
  <div>
    <p class="page-header-title">About &amp; Limitations</p>
    <p class="page-header-subtitle">Project overview, technology stack, known limitations, and security properties</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── About ─────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="medium")

with col_left:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-section-title">About This Project</div>', unsafe_allow_html=True)
    st.markdown("""
**Project:** AI-Based Email Spam and Phishing Detection System Using NLP and Machine Learning  
**Author:** Yash Yadav  
**Purpose:** Internship project demonstrating three-class email classification using traditional ML and NLP.
""")
    st.markdown('<div class="styled-hr" style="margin:0.75rem 0;"></div>', unsafe_allow_html=True)
    st.markdown("**What this system does:**")
    items = [
        "Classifies emails as **Legitimate**, **Spam**, or **Phishing**",
        "Provides a **heuristic phishing risk level** (LOW / MEDIUM / HIGH) independently of the ML classification",
        "Lists **triggered security indicators** with a human-readable explanation",
        "Does **not** visit any URLs, execute any HTML, or store submitted emails",
    ]
    for item in items:
        st.markdown(f"— {item}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-section-title">Technology Stack</div>', unsafe_allow_html=True)
    stack = [
        ("Language", "Python 3.11+"),
        ("Text features", "TF-IDF (scikit-learn)"),
        ("Cybersecurity features", "Custom heuristic extractor"),
        ("ML models", "MultinomialNB, LogisticRegression, LinearSVC"),
        ("HTML parsing", "BeautifulSoup4"),
        ("Model persistence", "joblib"),
        ("Web application", "Streamlit"),
        ("Testing", "pytest"),
    ]
    for component, tech in stack:
        st.markdown(
            f'<div class="security-row">'
            f'<span class="security-key">{component}</span>'
            f'<span style="color:#1e40af;font-weight:600;font-size:0.82rem;">{tech}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Security Properties ───────────────────────────────────────────────────────
st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Security Properties</div>', unsafe_allow_html=True)
security_props = [
    ("URLs visited",         False),
    ("HTML executed",        False),
    ("Email content stored", False),
    ("Input size limit",     True,  "100 KB per field"),
    ("Hardcoded secrets",    False),
    ("External API calls",   False),
]
for row in security_props:
    prop, status = row[0], row[1]
    note = row[2] if len(row) > 2 else ("Yes" if status else "Never")
    badge = f'<span class="badge-ok">✓ {note}</span>' if status else f'<span class="badge-no">✗ Never</span>'
    st.markdown(
        f'<div class="security-row"><span class="security-key">{prop}</span>{badge}</div>',
        unsafe_allow_html=True,
    )
st.markdown('</div>', unsafe_allow_html=True)

# ── Limitations + Future ──────────────────────────────────────────────────────
lim_col, fut_col = st.columns(2, gap="medium")

with lim_col:
    st.markdown('<div class="info-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown('<div class="card-section-title">Known Limitations</div>', unsafe_allow_html=True)
    limitations = [
        ("Dataset coverage", "Novel phishing techniques not in training data may be missed."),
        ("English only", "Preprocessing and word lists are optimised for English."),
        ("Text-only analysis", "URL safety is assessed by pattern matching, not live reputation lookup."),
        ("Heuristic thresholds", "Risk level thresholds are HEURISTIC_DEFAULT values, not validated security thresholds."),
        ("Not a security product", "This is an educational and research tool."),
        ("Class imbalance", "The Enron corpus is much larger than the phishing corpus, which may affect recall."),
    ]
    for title, desc in limitations:
        st.markdown(f'<div class="limit-item"><strong>{title}:</strong> {desc}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with fut_col:
    st.markdown('<div class="info-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown('<div class="card-section-title">Future Improvements</div>', unsafe_allow_html=True)
    future = [
        "Transformer-based NLP (BERT / RoBERTa)",
        "Multilingual support",
        "Real-time email client integration",
        "URL reputation API integration (opt-in)",
        "SHAP / LIME explainability",
        "Attachment analysis",
        "Continual learning with new phishing samples",
    ]
    for item in future:
        st.markdown(f'<div class="future-item">→ {item}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer-box">
  ⚠️ <strong>Disclaimer:</strong> This system is an ML-based analysis aid. It does not guarantee detection of all spam or phishing emails.
  Heuristic risk scores are initial estimates and must not be treated as calibrated probabilities.
  Always apply independent security judgment.
</div>
""", unsafe_allow_html=True)
