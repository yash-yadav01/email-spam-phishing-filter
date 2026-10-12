"""Model Information page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Model Information", page_icon="📊", layout="wide")

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
.feature-item {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
    padding: 0.35rem 0.7rem; margin-bottom: 0.35rem; font-size: 0.82rem;
    color: #334155; font-family: monospace;
}
.best-badge {
    display: inline-block; background: #dbeafe; color: #1e40af;
    border: 1px solid #93c5fd; border-radius: 5px;
    font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.55rem;
    margin-left: 0.5rem; vertical-align: middle; text-transform: uppercase;
    letter-spacing: 0.05em;
}
.styled-hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.25rem 0; }
[data-testid="stMetricLabel"] { font-size: 0.78rem !important; }
@media (max-width: 768px) {
    [data-testid="stMain"] > div:first-child { padding: 1rem !important; }
    .page-header { padding: 1rem 1.25rem; }
    .page-header-title { font-size: 1.1rem; }
}
</style>
""", unsafe_allow_html=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "models" / "training_results.json"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">📊</div>
  <div>
    <p class="page-header-title">Model Information</p>
    <p class="page-header-subtitle">Architecture overview, training configuration, and per-model comparison</p>
  </div>
</div>
""", unsafe_allow_html=True)

if not RESULTS_JSON.exists():
    st.warning(
        "Model has not been trained yet.\n\n"
        "Run: `python -m src.train`"
    )
    st.stop()

with open(RESULTS_JSON, encoding="utf-8") as f:
    data = json.load(f)

# ── System Architecture ───────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">System Architecture</div>', unsafe_allow_html=True)
st.code(
    "User Input (Subject + Body)\n"
    "        ↓\n"
    "  Text Preprocessing (HTML strip, URL/email tokens)\n"
    "        ↓\n"
    "  TF-IDF Vectorizer (unigrams+bigrams)  +  Security Feature Extractor\n"
    "        ↓\n"
    "  Trained ML Model (best of: MNB / LR / LinearSVC-Calibrated)\n"
    "        ↓\n"
    "  Phishing Risk Engine (heuristic — separate from ML)\n"
    "        ↓\n"
    "  Result: label + risk_level + confidence + indicators + explanation",
    language="text",
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Training Configuration ────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Training Configuration</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("TF-IDF Max Features", data.get("tfidf_max_features", "N/A"))
col2.metric("Train Samples",       data.get("train_samples", "N/A"))
col3.metric("Test Samples",        data.get("test_samples", "N/A"))
col4.metric("Best Model",          data.get("best_model", "N/A"))
st.markdown('</div>', unsafe_allow_html=True)

# ── Model Comparison ──────────────────────────────────────────────────────────
st.markdown('<div class="card-section-title" style="padding:0.25rem 0 0.5rem 0;border-bottom:none;">Model Comparison</div>', unsafe_allow_html=True)
best_model = data.get("best_model", "")
for r in data.get("all_results", []):
    is_best = r["model_name"] == best_model
    label = r["model_name"]
    badge = '<span class="best-badge">✓ Selected</span>' if is_best else ""
    with st.expander(f"{'🏆 ' if is_best else '📈 '}{label}", expanded=is_best):
        if is_best:
            st.markdown(f'<span style="font-size:0.78rem;color:#1e40af;font-weight:600;">Best model — selected by highest phishing recall then macro F1</span>{badge}', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy",          f"{r['accuracy']:.4f}")
        c2.metric("Macro F1",          f"{r['macro_f1']:.4f}")
        c3.metric("Phishing Recall",   f"{r['phishing_recall']:.4f}")
        c4.metric("Phishing Precision",f"{r['phishing_precision']:.4f}")
        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#64748b;font-weight:600;margin-bottom:0.3rem;">Classification Report</div>', unsafe_allow_html=True)
        st.text(r.get("classification_report", ""))

# ── Security Features ─────────────────────────────────────────────────────────
st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Security Features Used</div>', unsafe_allow_html=True)
features = data.get("feature_names_security", [])
cols = st.columns(2)
for i, name in enumerate(features):
    cols[i % 2].markdown(f'<div class="feature-item">{i+1}. {name}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption(
    "Model selection priority: Phishing Recall → Macro F1 → Accuracy. "
    "Heuristic risk thresholds are HEURISTIC_DEFAULT values, not validated security thresholds."
)
