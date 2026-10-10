"""
test_phishing_detector.py
Unit tests for src/phishing_detector.py
"""

import pytest
from src.phishing_detector import PhishingDetector, assess_phishing_risk

DETECTOR = PhishingDetector()
VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
RESULT_KEYS = {"risk_level", "heuristic_score", "triggered_indicators", "explanation"}


def test_result_has_required_keys():
    result = DETECTOR.assess("", "")
    for key in RESULT_KEYS:
        assert key in result


def test_risk_level_is_valid():
    result = DETECTOR.assess("Subject", "Some body")
    assert result["risk_level"] in VALID_RISK_LEVELS


def test_explanation_is_string():
    result = DETECTOR.assess("Subject", "Body")
    assert isinstance(result["explanation"], str)
    assert len(result["explanation"]) > 0


def test_triggered_indicators_is_list():
    result = DETECTOR.assess("Subject", "Body")
    assert isinstance(result["triggered_indicators"], list)


def test_empty_email_low_risk():
    result = DETECTOR.assess("", "")
    assert result["risk_level"] == "LOW"
    assert result["triggered_indicators"] == []


def test_clean_email_low_risk():
    result = DETECTOR.assess(
        "Team lunch tomorrow",
        "Hi all, we are meeting for lunch tomorrow at noon."
    )
    assert result["risk_level"] == "LOW"


def test_ip_url_raises_risk():
    result = DETECTOR.assess(
        "Account verification",
        "Click here to login: http://192.168.1.1/verify"
    )
    assert result["risk_level"] in ("MEDIUM", "HIGH")
    assert "IP-based URL detected" in result["triggered_indicators"]


def test_multiple_indicators_high_risk():
    result = DETECTOR.assess(
        "URGENT: Verify your account immediately",
        "Dear Customer, your account will be suspended within 24 hours. "
        "Login at http://192.168.1.1/login using your password and credit card. "
        "Click verify now: http://bit.ly/xyz. "
        "<form action='steal'><input name='password'></form>"
        "ACT NOW!!!"
    )
    assert result["risk_level"] == "HIGH"
    assert len(result["triggered_indicators"]) > 3


def test_no_indicators_empty_list():
    result = DETECTOR.assess("Hello", "See you at the meeting tomorrow.")
    assert result["triggered_indicators"] == []


def test_ml_label_not_modified():
    """The phishing detector should not return an ml_label field."""
    result = DETECTOR.assess("subject", "body")
    assert "ml_label" not in result


def test_heuristic_score_non_negative():
    result = DETECTOR.assess("", "")
    assert result["heuristic_score"] >= 0


def test_convenience_function():
    result = assess_phishing_risk("Subject", "Body")
    assert "risk_level" in result


def test_none_inputs():
    result = DETECTOR.assess(None, None)
    assert result["risk_level"] in VALID_RISK_LEVELS


def test_shortened_url_triggers_indicator():
    result = DETECTOR.assess("", "Click here http://bit.ly/abc to confirm")
    assert "Shortened URL detected" in result["triggered_indicators"]
