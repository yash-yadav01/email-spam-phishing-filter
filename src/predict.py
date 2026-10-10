"""
predict.py
==========
Single-input prediction pipeline.

Usage (Python API)
------------------
    from src.predict import predict, load_artefacts
    load_artefacts()          # call once at startup
    result = predict(subject="...", body="...")

Security requirements
---------------------
- URLs are NEVER visited, fetched, or resolved.
- User-submitted email content is NOT stored or logged.
- All inputs are treated as untrusted text.
- Input is capped at 100 KB per field.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix

from src.preprocessing import preprocess_subject_and_body
from src.feature_engineering import extract_security_features, features_to_list
from src.phishing_detector import assess_phishing_risk

# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR   = PROJECT_ROOT / "models"

_ARTEFACT_FILES = {
    "vectorizer": "tfidf_vectorizer.joblib",
    "encoder":    "label_encoder.joblib",
    "scaler":     "feature_scaler.joblib",
    "model":      "best_model.joblib",
}

# ── Module-level artefact cache ───────────────────────────────────────────────

_artefacts: Dict[str, object] = {}


def load_artefacts() -> None:
    """Load model artefacts from disk into module cache. Call once at startup."""
    global _artefacts
    for key, filename in _ARTEFACT_FILES.items():
        path = MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Model artefact not found: {path}\n"
                "Run: python -m src.train"
            )
        _artefacts[key] = joblib.load(path)


def _artefacts_loaded() -> bool:
    return len(_artefacts) == len(_ARTEFACT_FILES)


# ── Core prediction ───────────────────────────────────────────────────────────

def predict(subject: object, body: object) -> Dict:
    """
    Classify an email and assess its phishing risk.

    Parameters
    ----------
    subject : email subject string (may be None or empty)
    body    : email body string (may be None or empty)

    Returns
    -------
    dict with keys:
        ml_label             : "legitimate" | "spam" | "phishing"
        display_label        : uppercase version
        risk_level           : "LOW" | "MEDIUM" | "HIGH"
        confidence           : float 0–1 if available, else None
        confidence_available : bool
        triggered_indicators : list[str]
        explanation          : str
    """
    # Load artefacts lazily on first call
    if not _artefacts_loaded():
        load_artefacts()

    # Coerce and cap inputs
    subject = str(subject).strip() if subject is not None else ""
    body    = str(body).strip()    if body    is not None else ""
    if subject.lower() in ("nan", "none"):
        subject = ""
    if body.lower() in ("nan", "none"):
        body = ""
    subject = subject[:100_000]
    body    = body[:100_000]

    vectorizer = _artefacts["vectorizer"]
    encoder    = _artefacts["encoder"]
    scaler     = _artefacts["scaler"]
    model      = _artefacts["model"]

    # ── Feature extraction ────────────────────────────────────────────────────
    text = preprocess_subject_and_body(subject, body)
    X_tfidf = vectorizer.transform([text])

    fd = extract_security_features(subject, body)
    X_sec = np.array([features_to_list(fd)], dtype=float)
    X_sec_scaled = scaler.transform(X_sec)

    X = hstack([X_tfidf, csr_matrix(X_sec_scaled)])

    # ── ML prediction ─────────────────────────────────────────────────────────
    y_pred = model.predict(X)[0]
    ml_label = encoder.inverse_transform([y_pred])[0]

    # ── Confidence ────────────────────────────────────────────────────────────
    confidence = None
    confidence_available = False
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(X)[0]
            confidence = float(proba[y_pred])
            confidence_available = True
        except Exception:
            pass

    # ── Phishing risk engine (separate from ML) ───────────────────────────────
    risk_result = assess_phishing_risk(subject=subject, body=body)

    return {
        "ml_label":             ml_label,
        "display_label":        ml_label.upper(),
        "risk_level":           risk_result["risk_level"],
        "confidence":           confidence,
        "confidence_available": confidence_available,
        "triggered_indicators": risk_result["triggered_indicators"],
        "explanation":          risk_result["explanation"],
    }
