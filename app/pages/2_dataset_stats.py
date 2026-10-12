"""Dataset Statistics page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Dataset Statistics", page_icon="📂", layout="wide")

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
.meta-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.4rem 0; border-bottom: 1px solid #f1f5f9; font-size: 0.875rem;
}
.meta-row:last-child { border-bottom: none; }
.meta-key { color: #64748b; font-weight: 500; }
.meta-val { color: #0f172a; font-weight: 600; }
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
META_JSON    = PROJECT_ROOT / "data" / "processed" / "dataset_metadata.json"
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">📂</div>
  <div>
    <p class="page-header-title">Dataset Statistics</p>
    <p class="page-header-subtitle">Actual class counts, data sources, and exploratory analysis figures</p>
  </div>
</div>
""", unsafe_allow_html=True)

if not META_JSON.exists():
    st.warning(
        "Dataset has not been prepared yet.\n\n"
        "Run: `python -m src.prepare_dataset`"
    )
    st.stop()

with open(META_JSON, encoding="utf-8") as f:
    meta = json.load(f)

counts = meta.get("class_counts", {})
total  = meta.get("total_records", 0)

# ── Overview metrics ──────────────────────────────────────────────────────────
st.markdown('<div class="info-card">', unsafe_allow_html=True)
st.markdown('<div class="card-section-title">Dataset Overview</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records",   total)
col2.metric("Legitimate",      counts.get("legitimate", 0))
col3.metric("Spam",            counts.get("spam", 0))
col4.metric("Phishing",        counts.get("phishing", 0))
st.markdown('<div class="styled-hr" style="margin:0.75rem 0;"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="meta-row"><span class="meta-key">Duplicates removed</span><span class="meta-val">{meta.get('duplicates_removed', 0)}</span></div>
<div class="meta-row"><span class="meta-key">Empty records removed</span><span class="meta-val">{meta.get('empty_records_removed', 0)}</span></div>
<div class="meta-row"><span class="meta-key">Prepared at (UTC)</span><span class="meta-val">{meta.get('preparation_timestamp_utc', 'N/A')}</span></div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Data Sources ──────────────────────────────────────────────────────────────
st.markdown('<div class="card-section-title" style="padding:0.25rem 0 0.5rem 0;border-bottom:none;">Data Sources</div>', unsafe_allow_html=True)
for source in meta.get("sources", []):
    with st.expander(source.get("name", "Unknown")):
        st.markdown(f"- **Records loaded:** {source.get('records_loaded', 'N/A')}")
        st.markdown(f"- **Source URL:** {source.get('source_url', 'N/A')}")
        st.markdown(f"- **License note:** {source.get('license_note', 'N/A')}")

# ── EDA Figures ───────────────────────────────────────────────────────────────
st.markdown('<div class="styled-hr"></div>', unsafe_allow_html=True)
st.markdown('<div class="card-section-title" style="padding:0.25rem 0 0.5rem 0;border-bottom:none;">EDA Figures</div>', unsafe_allow_html=True)
figs = [
    ("class_distribution.png",        "Class Distribution"),
    ("body_length_distribution.png",   "Body Length Distribution"),
    ("subject_length_distribution.png","Subject Length Distribution"),
    ("top_words_by_class.png",         "Top Words by Class"),
]
fig_cols = st.columns(2)
for idx, (fname, caption) in enumerate(figs):
    path = FIGURES_DIR / fname
    with fig_cols[idx % 2]:
        if path.exists():
            st.markdown(f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:0.75rem;margin-bottom:1rem;">', unsafe_allow_html=True)
            st.image(str(path), caption=caption, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"{caption} — figure not yet generated. Run: `python -m src.eda`")

st.caption(
    "All statistics are computed from the actual prepared dataset. "
    "Verify dataset licenses independently before any publication or redistribution."
)
