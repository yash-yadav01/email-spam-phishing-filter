"""
test_predict.py
Functional tests for src/predict.py

Note: these tests require trained model artefacts (models/*.joblib).
Tests that need the model skip gracefully when artefacts are missing.
"""

import pytest
from src.predict import predict, load_artefacts, _artefacts_loaded

RESULT_KEYS = {
    "ml_label", "display_label", "risk_level",
    "confidence", "confidence_available",
    "triggered_indicators", "explanation",
}
VALID_LABELS     = {"legitimate", "spam", "phishing"}
VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}


def _model_available() -> bool:
    try:
        if not _artefacts_loaded():
            load_artefacts()
        return True
    except FileNotFoundError:
        return False


requires_model = pytest.mark.skipif(
    not _model_available(),
    reason="Trained model artefacts not found — run: python -m src.train"
)


# ── Tests that do NOT require the model ───────────────────────────────────────

def test_missing_artefacts_raises_file_not_found():
    """When artefacts are absent, predict() should raise FileNotFoundError."""
    if _model_available():
        pytest.skip("Model is present — skipping missing-artefact test")
    with pytest.raises(FileNotFoundError):
        predict("subject", "body")


# ── Tests that require the model ──────────────────────────────────────────────

@requires_model
def test_result_has_required_keys():
    result = predict("Test subject", "Test body content")
    for key in RESULT_KEYS:
        assert key in result, f"Missing key: {key}"


@requires_model
def test_ml_label_is_valid():
    result = predict("Test", "Normal email content about a meeting")
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_display_label_is_uppercase():
    result = predict("Test", "Some email body")
    assert result["display_label"] == result["ml_label"].upper()


@requires_model
def test_risk_level_is_valid():
    result = predict("Test", "Some email body")
    assert result["risk_level"] in VALID_RISK_LEVELS


@requires_model
def test_confidence_available_is_bool():
    result = predict("Test", "Some email body")
    assert isinstance(result["confidence_available"], bool)


@requires_model
def test_triggered_indicators_is_list():
    result = predict("Test", "Some email body")
    assert isinstance(result["triggered_indicators"], list)


@requires_model
def test_explanation_is_string():
    result = predict("Test", "Some email body")
    assert isinstance(result["explanation"], str)
    assert len(result["explanation"]) > 0


@requires_model
def test_empty_subject_and_body():
    result = predict("", "")
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_subject_only():
    result = predict("Urgent: verify your account", "")
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_body_only():
    result = predict("", "Please click the link and enter your password now.")
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_none_inputs():
    result = predict(None, None)
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_very_long_email():
    big_body = "Normal email content. " * 5000
    result = predict("Test subject", big_body)
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_html_email():
    html_body = (
        "<html><body>"
        "<h1>Important Notice</h1>"
        "<p>Click <a href='https://example.com'>here</a></p>"
        "<form><input type='password' name='pw'></form>"
        "</body></html>"
    )
    result = predict("HTML email test", html_body)
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_ip_url_email():
    result = predict(
        "Verify account",
        "Login at http://192.168.1.1/login and enter your credentials"
    )
    assert result["ml_label"] in VALID_LABELS
    # IP URL should trigger the phishing risk engine
    assert result["risk_level"] in ("MEDIUM", "HIGH")


@requires_model
def test_special_characters():
    result = predict("Test <>&\"'", "Body with special chars: <>&\"'")
    assert result["ml_label"] in VALID_LABELS


@requires_model
def test_confidence_if_available():
    result = predict("Test", "Normal email")
    if result["confidence_available"]:
        assert result["confidence"] is not None
        assert 0.0 <= result["confidence"] <= 1.0
