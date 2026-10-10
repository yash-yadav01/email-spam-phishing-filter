"""
evaluate.py
===========
Loads trained model artefacts and the held-out test results,
prints a full evaluation report, and saves confusion matrix figure.

Usage
-----
    python -m src.evaluate

All metrics come from the held-out test set recorded during training.
No metrics are fabricated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
MODELS_DIR    = PROJECT_ROOT / "models"
FIGURES_DIR   = PROJECT_ROOT / "reports" / "figures"
RESULTS_JSON  = MODELS_DIR / "training_results.json"


def save_confusion_matrix(cm: list, class_order: list, model_name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    cm_arr = np.array(cm)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm_arr, interpolation="nearest", cmap=plt.cm.Blues)
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(class_order)))
    ax.set_yticks(range(len(class_order)))
    ax.set_xticklabels(class_order, rotation=45, ha="right")
    ax.set_yticklabels(class_order)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(f"Confusion Matrix — {model_name}")
    thresh = cm_arr.max() / 2.0
    for i in range(cm_arr.shape[0]):
        for j in range(cm_arr.shape[1]):
            ax.text(j, i, str(cm_arr[i, j]),
                    ha="center", va="center",
                    color="white" if cm_arr[i, j] > thresh else "black")
    plt.tight_layout()
    out_path = FIGURES_DIR / "confusion_matrix.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved confusion matrix: {out_path}")


def evaluate_model() -> None:
    if not RESULTS_JSON.exists():
        sys.exit(
            f"[ERROR] {RESULTS_JSON} not found.\n"
            "Run: python -m src.train"
        )

    with open(RESULTS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "="*60)
    print("MODEL EVALUATION REPORT")
    print("="*60)
    print(f"Trained at      : {data.get('trained_at_utc', 'N/A')}")
    print(f"Dataset         : {data.get('dataset', 'N/A')}")
    print(f"Train samples   : {data.get('train_samples', 'N/A')}")
    print(f"Test samples    : {data.get('test_samples', 'N/A')}")
    print(f"Best model      : {data.get('best_model', 'N/A')}")
    print(f"Selection       : {data.get('selection_criteria', 'N/A')}")
    print()

    for result in data.get("all_results", []):
        name = result["model_name"]
        print(f"── {name} ──")
        print(f"  Accuracy         : {result['accuracy']}")
        print(f"  Macro F1         : {result['macro_f1']}")
        print(f"  Weighted F1      : {result['weighted_f1']}")
        print(f"  Phishing Recall  : {result['phishing_recall']}")
        print(f"  Phishing Precision: {result['phishing_precision']}")
        print()
        print(result.get("classification_report", ""))

    # Save confusion matrix for best model
    best_name = data.get("best_model")
    for result in data.get("all_results", []):
        if result["model_name"] == best_name:
            save_confusion_matrix(
                result["confusion_matrix"],
                result["class_order"],
                best_name,
            )
            break


if __name__ == "__main__":
    evaluate_model()
