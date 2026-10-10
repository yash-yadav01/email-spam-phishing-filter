"""Model Information page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Model Information", page_icon="📊", layout="wide")
st.title("📊 Model Information")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "models" / "training_results.json"

if not RESULTS_JSON.exists():
    st.warning(
        "Model has not been trained yet.\n\n"
        "Run: `python -m src.train`"
    )
    st.stop()

with open(RESULTS_JSON, encoding="utf-8") as f:
    data = json.load(f)

st.markdown("## System Architecture")
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

st.markdown("## Training Configuration")
col1, col2 = st.columns(2)
col1.metric("TF-IDF Max Features", data.get("tfidf_max_features", "N/A"))
col1.metric("Train Samples", data.get("train_samples", "N/A"))
col2.metric("Test Samples", data.get("test_samples", "N/A"))
col2.metric("Best Model Selected", data.get("best_model", "N/A"))

st.markdown("## Model Comparison")
for r in data.get("all_results", []):
    with st.expander(f"📈 {r['model_name']}", expanded=(r['model_name'] == data.get('best_model'))):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{r['accuracy']:.4f}")
        c2.metric("Macro F1", f"{r['macro_f1']:.4f}")
        c3.metric("Phishing Recall", f"{r['phishing_recall']:.4f}")
        c4.metric("Phishing Precision", f"{r['phishing_precision']:.4f}")
        st.text(r.get("classification_report", ""))

st.markdown("## Security Features Used")
features = data.get("feature_names_security", [])
for i, name in enumerate(features, 1):
    st.markdown(f"{i}. `{name}`")

st.caption(
    "Model selection priority: Phishing Recall → Macro F1 → Accuracy. "
    "Heuristic risk thresholds are HEURISTIC_DEFAULT values, not validated security thresholds."
)
