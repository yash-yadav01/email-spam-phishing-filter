"""
test_preprocessing.py
Unit tests for src/preprocessing.py
"""

import pytest
from src.preprocessing import preprocess_text, preprocess_subject_and_body, URL_TOKEN, EMAIL_TOKEN, IP_TOKEN


def test_empty_string():
    assert preprocess_text("") == ""


def test_none_input():
    assert preprocess_text(None) == ""


def test_nan_string():
    assert preprocess_text("nan") == ""


def test_lowercase():
    result = preprocess_text("HELLO WORLD")
    assert result == result.lower()


def test_url_replaced():
    result = preprocess_text("Visit https://example.com now")
    assert URL_TOKEN in result
    assert "example.com" not in result


def test_www_url_replaced():
    result = preprocess_text("Go to www.example.com for details")
    assert URL_TOKEN in result


def test_email_replaced():
    result = preprocess_text("Contact me at user@example.com")
    assert EMAIL_TOKEN in result
    assert "user@example.com" not in result


def test_ip_url_replaced():
    result = preprocess_text("Login at http://192.168.1.1/admin")
    assert IP_TOKEN in result


def test_html_stripped():
    result = preprocess_text("<b>Hello</b> <script>alert('x')</script> World")
    assert "<b>" not in result
    assert "<script>" not in result
    assert "hello" in result or "world" in result


def test_exclamation_kept():
    result = preprocess_text("Act now!!!")
    assert "!" in result


def test_question_mark_kept():
    result = preprocess_text("Can you verify?")
    assert "?" in result


def test_very_long_input():
    big = "hello world " * 10000
    result = preprocess_text(big)
    assert isinstance(result, str)
    assert len(result) < 200_000


def test_unicode_handled():
    result = preprocess_text("Héllo wörld café")
    assert isinstance(result, str)


def test_combine_subject_and_body():
    result = preprocess_subject_and_body("Meeting today", "Let us discuss the project")
    assert isinstance(result, str)
    assert len(result) > 0


def test_subject_only():
    result = preprocess_subject_and_body("Urgent action required", "")
    assert isinstance(result, str)


def test_body_only():
    result = preprocess_subject_and_body("", "Please verify your account immediately")
    assert isinstance(result, str)


def test_both_empty():
    result = preprocess_subject_and_body("", "")
    assert result == ""
