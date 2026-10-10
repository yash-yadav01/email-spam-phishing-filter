"""
train.py
========
Trains and compares three ML models on the combined TF-IDF +
cybersecurity feature set, then serialises the best model.

Model selection priority: Phishing Recall → Macro F1 → Accuracy

Usage
-----
    python -m src.train

Outputs (models/)
-----------------
    tfidf_vectorizer.joblib
    label_encoder.joblib
    best_model.joblib
    training_results.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

from src.preprocessing import preprocess_subject_and_body
from src.feature_engineering import extract_security_features, FEATURE_NAMES, features_to_list

# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR    = PROJECT_ROOT / "models"
DATASET_CSV   = PROCESSED_DIR / "dataset.csv"

ALLOWED_LABELS = {"legitimate", "spam", "phishing"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"subject", "body", "label"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"[ERROR] Dataset missing columns: {missing}")
    df["subject"] = df["subject"].fillna("").astype(str)
    df["body"]    = df["body"].fillna("").astype(str)
    df["label"]   = df["label"].astype(str).str.strip().str.lower()
    df = df[df["label"].isin(ALLOWED_LABELS)].copy()
    if df.empty:
        sys.exit("[ERROR] Dataset has no valid rows after label filtering.")
    return df


def build_combined_features(df: pd.DataFrame, vectorizer: TfidfVectorizer,
                             scaler: MinMaxScaler, fit: bool = False):
    """
    Return (X_combined, y_array).
    If fit=True, fit the vectorizer and scaler on this data.
    """
    texts = df.apply(
        lambda row: preprocess_subject_and_body(row["subject"], row["body"]),
        axis=1
    ).tolist()

    if fit:
        X_tfidf = vectorizer.fit_transform(texts)
    else:
        X_tfidf = vectorizer.transform(texts)

    # Security features
    sec_rows = []
    for _, row in df.iterrows():
        fd = extract_security_features(row["subject"], row["body"])
        sec_rows.append(features_to_list(fd))
    X_sec = np.array(sec_rows, dtype=float)

    if fit:
        X_sec_scaled = scaler.fit_transform(X_sec)
    else:
        X_sec_scaled = scaler.transform(X_sec)

    # Combine sparse TF-IDF with dense security features
    X_combined = hstack([X_tfidf, csr_matrix(X_sec_scaled)])
    return X_combined


def evaluate_on_test(model, X_test, y_test, label_encoder, model_name: str) -> dict:
    y_pred = model.predict(X_test)
    labels = list(label_encoder.classes_)
    phishing_idx = list(labels).index("phishing") if "phishing" in labels else None

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    p, r, f, _ = precision_recall_fscore_support(
        y_test, y_pred, labels=list(range(len(labels))), zero_division=0
    )

    phishing_recall = float(r[phishing_idx]) if phishing_idx is not None else 0.0
    phishing_prec   = float(p[phishing_idx]) if phishing_idx is not None else 0.0

    per_class = {}
    for i, lbl in enumerate(labels):
        per_class[lbl] = {
            "precision": round(float(p[i]), 4),
            "recall":    round(float(r[i]), 4),
            "f1":        round(float(f[i]), 4),
        }

    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=labels, zero_division=0)

    return {
        "model_name":       model_name,
        "accuracy":         round(acc, 4),
        "macro_f1":         round(macro_f1, 4),
        "weighted_f1":      round(weighted_f1, 4),
        "phishing_recall":  round(phishing_recall, 4),
        "phishing_precision": round(phishing_prec, 4),
        "per_class":        per_class,
        "confusion_matrix": cm,
        "class_order":      labels,
        "classification_report": report,
    }


# ── Training pipeline ─────────────────────────────────────────────────────────

def train_models() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if not DATASET_CSV.exists():
        sys.exit(
            f"[ERROR] Dataset not found at {DATASET_CSV}\n"
            "Run: python -m src.prepare_dataset"
        )

    print("Loading dataset …")
    df = load_dataset(DATASET_CSV)
    print(f"  Total records: {len(df)}")
    for lbl, cnt in df["label"].value_counts().items():
        print(f"    {lbl}: {cnt}")

    # ── Label encoding ────────────────────────────────────────────────────────
    le = LabelEncoder()
    y = le.fit_transform(df["label"].values)
    print(f"\nLabel classes: {list(le.classes_)}")

    # ── Train/test split ──────────────────────────────────────────────────────
    min_class = df["label"].value_counts().min()
    stratify = y if min_class >= 2 else None
    if stratify is None:
        print("[WARN] Stratification disabled — some class has fewer than 2 samples.")

    df_train, df_test, y_train, y_test = train_test_split(
        df, y, test_size=0.2, random_state=42, stratify=stratify
    )
    print(f"\nTrain: {len(df_train)}  Test: {len(df_test)}")

    # ── Feature pipeline ──────────────────────────────────────────────────────
    max_features = 10_000 if len(df_train) >= 5_000 else 5_000
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=max_features,
        min_df=2,
        sublinear_tf=True,
        analyzer="word",
    )
    scaler = MinMaxScaler()

    print("\nBuilding training features …")
    X_train = build_combined_features(df_train, vectorizer, scaler, fit=True)
    print("Building test features …")
    X_test  = build_combined_features(df_test,  vectorizer, scaler, fit=False)

    # ── Candidate models ──────────────────────────────────────────────────────
    candidates = {
        "MultinomialNB":        MultinomialNB(alpha=0.1),
        "LogisticRegression":   LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42, C=1.0
        ),
        "LinearSVC_calibrated": CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", random_state=42, max_iter=2000, C=1.0),
            cv=5,
        ),
    }

    results = []
    trained_models = {}

    for name, clf in candidates.items():
        print(f"\nTraining {name} …")
        try:
            clf.fit(X_train, y_train)
            result = evaluate_on_test(clf, X_test, y_test, le, name)
            results.append(result)
            trained_models[name] = clf
            print(f"  Accuracy={result['accuracy']}  "
                  f"Macro-F1={result['macro_f1']}  "
                  f"Phishing-Recall={result['phishing_recall']}")
            print(result["classification_report"])
        except Exception as exc:
            print(f"  [WARN] {name} failed: {exc}")

    if not results:
        sys.exit("[ERROR] All models failed to train.")

    # ── Model selection: Phishing Recall → Macro F1 → Accuracy ──────────────
    best_result = max(
        results,
        key=lambda r: (r["phishing_recall"], r["macro_f1"], r["accuracy"])
    )
    best_name  = best_result["model_name"]
    best_model = trained_models[best_name]

    print(f"\n{'='*50}")
    print(f"Best model: {best_name}")
    print(f"  Phishing Recall : {best_result['phishing_recall']}")
    print(f"  Macro F1        : {best_result['macro_f1']}")
    print(f"  Accuracy        : {best_result['accuracy']}")
    print("="*50)

    # ── Save artefacts ────────────────────────────────────────────────────────
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(le,         MODELS_DIR / "label_encoder.joblib")
    joblib.dump(scaler,     MODELS_DIR / "feature_scaler.joblib")
    joblib.dump(best_model, MODELS_DIR / "best_model.joblib")
    print("\nSaved model artefacts to models/")

    # Save all results and metadata
    training_output = {
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset":        str(DATASET_CSV.relative_to(PROJECT_ROOT)),
        "train_samples":  len(df_train),
        "test_samples":   len(df_test),
        "tfidf_max_features": max_features,
        "feature_names_security": FEATURE_NAMES,
        "best_model": best_name,
        "selection_criteria": "Phishing Recall > Macro F1 > Accuracy",
        "all_results": results,
        "class_counts_train": df_train["label"].value_counts().to_dict(),
        "class_counts_test":  df_test["label"].value_counts().to_dict(),
    }
    results_path = MODELS_DIR / "training_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(training_output, f, indent=2)
    print(f"Saved: {results_path}")


if __name__ == "__main__":
    train_models()
