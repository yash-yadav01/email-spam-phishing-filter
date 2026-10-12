"""Model Evaluation page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Model Evaluation", page_icon="📈", layout="wide")

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
.selection-banner {
    background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px;
    padding: 0.65rem 1rem; font-size: 0.875rem; color: #1e3a8a;
    margin-bottom: 1rem;
}
.per-class-label {
    font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.06em; color: #64748b; margin-bottom: 0.3rem;
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

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "models" / "training_results.json"
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">📈</div>
  <div>
    <p class="page-header-title">Model Evaluation</p>
    <p class="page-header-subtitle">Held-out test set metrics, per-class breakdown, confusion matrix, and model comparison</p>
  </div>
</div>
""", unsafe_allow_html=True)

if not RESULTS_JSON.exists():
    st.warning("Model not trained yet. Run: `python -m src.train`")
    st.stop()

with open(RESULTS_JSON, encoding="utf-8") as f:
    data = json.load(f)

best_name = data.get("best_model", "N/A")

st.markdown(f"""
<div class="selection-banner">
  <strong>Selected model:</strong> <code>{best_name}</code> &nbsp;—&nbsp;
  Selection criteria: {data.get('selection_criteria', 'N/A')}
</div>
""", unsafe_allow_html=True)

# ── Best Model Metrics ────────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Best Model — Overall Metrics</div>', unsafe_allow_html=True)
for r in data.get("all_results", []):
    if r["model_name"] == best_name:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Accuracy",        f"{r['accuracy']:.4f}")
        c2.metric("Macro F1",        f"{r['macro_f1']:.4f}")
        c3.metric("Weighted F1",     f"{r['weighted_f1']:.4f}")
        c4.metric("Phishing Recall", f"{r['phishing_recall']:.4f}")
        c5.metric("Phishing Prec.",  f"{r['phishing_precision']:.4f}")

        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-section-title" style="border-bottom:none;margin-bottom:0.5rem;">Per-Class Results</div>', unsafe_allow_html=True)
        for lbl, metrics in r.get("per_class", {}).items():
            st.markdown(f'<div class="per-class-label">{lbl}</div>', unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric(f"Precision", f"{metrics['precision']:.4f}")
            cc2.metric(f"Recall",    f"{metrics['recall']:.4f}")
            cc3.metric(f"F1",        f"{metrics['f1']:.4f}")

        st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#64748b;font-weight:600;margin-bottom:0.3rem;">Full Classification Report</div>', unsafe_allow_html=True)
        st.text(r.get("classification_report", ""))
        break
st.markdown('</div>', unsafe_allow_html=True)

# ── Confusion Matrix ──────────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Confusion Matrix</div>', unsafe_allow_html=True)
cm_path = FIGURES_DIR / "confusion_matrix.png"
if cm_path.exists():
    col_img, col_pad = st.columns([2, 1])
    with col_img:
        st.image(str(cm_path), caption=f"Confusion Matrix — {best_name}", use_container_width=True)
else:
    st.info("Confusion matrix not yet generated. Run: `python -m src.evaluate`")
st.markdown('</div>', unsafe_allow_html=True)

# ── All Models Compared ───────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">All Models Compared</div>', unsafe_allow_html=True)
rows = []
for r in data.get("all_results", []):
    rows.append({
        "Model":            r["model_name"],
        "Accuracy":         r["accuracy"],
        "Macro F1":         r["macro_f1"],
        "Weighted F1":      r["weighted_f1"],
        "Phishing Recall":  r["phishing_recall"],
        "Phishing Prec.":   r["phishing_precision"],
    })
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df.style.highlight_max(axis=0, color="#bbf7d0"), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.caption(
    "All metrics are from the held-out 20% test set. "
    "No metrics were fabricated."
)
