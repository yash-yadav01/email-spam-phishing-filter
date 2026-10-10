"""Dataset Statistics page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Dataset Statistics", page_icon="📂", layout="wide")
st.title("📂 Dataset Statistics")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
META_JSON    = PROJECT_ROOT / "data" / "processed" / "dataset_metadata.json"
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"

if not META_JSON.exists():
    st.warning(
        "Dataset has not been prepared yet.\n\n"
        "Run: `python -m src.prepare_dataset`"
    )
    st.stop()

with open(META_JSON, encoding="utf-8") as f:
    meta = json.load(f)

st.markdown("## Dataset Overview")
counts = meta.get("class_counts", {})
total  = meta.get("total_records", 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records",   total)
col2.metric("Legitimate",      counts.get("legitimate", 0))
col3.metric("Spam",            counts.get("spam", 0))
col4.metric("Phishing",        counts.get("phishing", 0))

st.markdown(f"**Duplicates removed:** {meta.get('duplicates_removed', 0)}")
st.markdown(f"**Empty records removed:** {meta.get('empty_records_removed', 0)}")
st.markdown(f"**Prepared at (UTC):** {meta.get('preparation_timestamp_utc', 'N/A')}")

st.markdown("## Data Sources")
for source in meta.get("sources", []):
    with st.expander(source.get("name", "Unknown")):
        st.markdown(f"- **Records loaded:** {source.get('records_loaded', 'N/A')}")
        st.markdown(f"- **Source URL:** {source.get('source_url', 'N/A')}")
        st.markdown(f"- **License note:** {source.get('license_note', 'N/A')}")

st.markdown("## EDA Figures")
figs = [
    ("class_distribution.png",       "Class Distribution"),
    ("body_length_distribution.png",  "Body Length Distribution"),
    ("subject_length_distribution.png","Subject Length Distribution"),
    ("top_words_by_class.png",        "Top Words by Class"),
]
for fname, caption in figs:
    path = FIGURES_DIR / fname
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"{caption} — figure not yet generated. Run: `python -m src.eda`")

st.caption(
    "All statistics are computed from the actual prepared dataset. "
    "Verify dataset licenses independently before any publication or redistribution."
)
