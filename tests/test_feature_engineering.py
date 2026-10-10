"""
test_feature_engineering.py
Unit tests for src/feature_engineering.py
"""

import pytest
from src.feature_engineering import extract_security_features, FEATURE_NAMES, features_to_list


def test_returns_all_feature_keys():
    features = extract_security_features("", "")
    for name in FEATURE_NAMES:
        assert name in features, f"Missing feature: {name}"


def test_all_values_non_negative():
    features = extract_security_features("Test", "Some email body content")
    for k, v in features.items():
        assert v >= 0, f"Feature {k} is negative: {v}"


def test_url_count():
    features = extract_security_features("", "Visit https://example.com and http://test.org")
    assert features["url_count"] == 2


def test_ip_url_detected():
    features = extract_security_features("", "Login at http://192.168.1.1/admin")
    assert features["has_ip_url"] == 1


def test_no_ip_url():
    features = extract_security_features("", "Visit https://example.com")
    assert features["has_ip_url"] == 0


def test_shortened_url_detected():
    features = extract_security_features("", "Click http://bit.ly/abc123 to proceed")
    assert features["has_shortened_url"] == 1


def test_urgency_score():
    features = extract_security_features("Urgent action required", "Your account will expire immediately")
    assert features["urgency_score"] >= 1


def test_credential_score():
    features = extract_security_features("", "Please enter your password and login credentials")
    assert features["credential_score"] >= 1


def test_financial_score():
    features = extract_security_features("", "Please transfer money to our bank account")
    assert features["financial_score"] >= 1


def test_clean_email_low_scores():
    features = extract_security_features(
        "Team lunch tomorrow",
        "Hi all, we will have lunch in the cafeteria at noon."
    )
    assert features["urgency_score"] == 0
    assert features["credential_score"] == 0
    assert features["has_ip_url"] == 0


def test_exclamation_count():
    features = extract_security_features("", "Win now!!! Act fast!!!")
    assert features["exclamation_count"] >= 6


def test_html_form_detected():
    features = extract_security_features("", "<html><body><form action='x'><input></form></body></html>")
    assert features["html_form_count"] >= 1


def test_features_to_list_length():
    features = extract_security_features("", "Test body")
    lst = features_to_list(features)
    assert len(lst) == len(FEATURE_NAMES)


def test_subject_urgency():
    features = extract_security_features("URGENT: Action required now", "Normal body text")
    assert features["subject_urgency"] >= 1


def test_none_inputs():
    features = extract_security_features(None, None)
    for v in features.values():
        assert v >= 0


def test_empty_inputs():
    features = extract_security_features("", "")
    for v in features.values():
        assert v >= 0
