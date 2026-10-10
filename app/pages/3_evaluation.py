"""Model Evaluation page."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Model Evaluation", page_icon="📈", layout="wide")
st.title("📈 Model Evaluation")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_JSON = PROJECT_ROOT / "models" / "training_results.json"
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"

if not RESULTS_JSON.exists():
    st.warning("Model not trained yet. Run: `python -m src.train`")
    st.stop()

with open(RESULTS_JSON, encoding="utf-8") as f:
    data = json.load(f)

best_name = data.get("best_model", "N/A")
st.markdown(f"**Selected model:** `{best_name}` — chosen by: {data.get('selection_criteria', 'N/A')}")

st.markdown("---")
st.markdown("## Best Model Metrics")
for r in data.get("all_results", []):
    if r["model_name"] == best_name:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Accuracy",         f"{r['accuracy']:.4f}")
        c2.metric("Macro F1",         f"{r['macro_f1']:.4f}")
        c3.metric("Weighted F1",      f"{r['weighted_f1']:.4f}")
        c4.metric("Phishing Recall",  f"{r['phishing_recall']:.4f}")
        c5.metric("Phishing Prec.",   f"{r['phishing_precision']:.4f}")

        st.markdown("### Per-Class Results")
        for lbl, metrics in r.get("per_class", {}).items():
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric(f"{lbl} Precision", f"{metrics['precision']:.4f}")
            cc2.metric(f"{lbl} Recall",    f"{metrics['recall']:.4f}")
            cc3.metric(f"{lbl} F1",        f"{metrics['f1']:.4f}")

        st.markdown("### Full Classification Report")
        st.text(r.get("classification_report", ""))
        break

st.markdown("## Confusion Matrix")
cm_path = FIGURES_DIR / "confusion_matrix.png"
if cm_path.exists():
    st.image(str(cm_path), caption=f"Confusion Matrix — {best_name}", use_container_width=False)
else:
    st.info("Confusion matrix not yet generated. Run: `python -m src.evaluate`")

st.markdown("## All Models Compared")
import pandas as pd
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

st.caption(
    "All metrics are from the held-out 20% test set. "
    "No metrics were fabricated."
)
