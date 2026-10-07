"""
predict.py
==========
Single-input prediction pipeline for the Streamlit application.

Accepts a raw email subject and body, applies the full preprocessing
and feature extraction pipeline, and returns a structured result.

Result schema
-------------
{
    "ml_label"             : str,   # "legitimate" | "spam" | "phishing"
    "display_label"        : str,   # uppercase version for UI
    "risk_level"           : str,   # "LOW" | "MEDIUM" | "HIGH"
    "confidence"           : float, # probability [0.0–1.0] if available
    "confidence_available" : bool,  # True only if model supports predict_proba
    "triggered_indicators" : list,  # human-readable indicator strings
    "explanation"          : str,   # 1–3 sentence plain-language summary
}

Rules
-----
- Models are loaded ONCE at startup (not per request).
- None / empty inputs are converted to empty strings before processing.
- URLs are NEVER visited, fetched, or resolved.
- User-submitted email content is NOT stored or logged.
- Confidence is displayed only when the model natively supports
  predict_proba OR when CalibratedClassifierCV is used.

TODO (Phase 10): Implement predict() and load_artefacts() functions.
"""

# Implementation will be added in Phase 10.
