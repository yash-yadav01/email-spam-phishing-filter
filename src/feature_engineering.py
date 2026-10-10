"""
feature_engineering.py
=======================
Extracts cybersecurity / phishing heuristic features from raw email text.

All feature values are non-negative integers or floats.
Feature order is FIXED — do not change the ORDER without retraining.

Note: all weights/thresholds are HEURISTIC_DEFAULT values.
They are not scientifically validated security thresholds.

Security requirement
--------------------
URLs are analysed as TEXT ONLY. Never visited, fetched, or resolved.
"""

from __future__ import annotations

import re
from typing import Dict, List

# ── Word lists (HEURISTIC_DEFAULT) ────────────────────────────────────────────

_URGENCY_WORDS = frozenset({
    "urgent", "urgently", "immediately", "expires", "expiring", "expiration",
    "act now", "act immediately", "limited time", "final notice", "last chance",
    "deadline", "hurry", "warning", "alert", "important notice", "action required",
    "respond immediately", "within 24 hours", "within 48 hours", "do not delay",
    "time sensitive", "time-sensitive", "critical", "suspended", "suspension",
    "restricted", "restriction", "disabled", "terminate", "terminated",
})

_CREDENTIAL_WORDS = frozenset({
    "password", "passwd", "username", "user name", "login", "log in",
    "sign in", "signin", "credentials", "credential", "authenticate",
    "authentication", "account access", "access your account", "update your account",
    "verify your identity", "confirm your identity", "security code",
    "verification code", "one-time password", "otp", "2fa", "two-factor",
    "ssn", "social security", "date of birth", "credit card", "card number",
    "cvv", "pin number", "banking details",
})

_FINANCIAL_WORDS = frozenset({
    "bank", "banking", "transfer", "wire transfer", "payment", "invoice",
    "billing", "refund", "reimbursement", "prize", "winner", "won",
    "lottery", "claim", "award", "gift card", "gift certificate",
    "paypal", "western union", "moneygram", "bitcoin", "cryptocurrency",
    "wallet", "transaction", "funds", "money", "cash",
})

_VERIFICATION_WORDS = frozenset({
    "verify", "verification", "confirm", "confirmation", "validate",
    "validation", "update", "review", "re-confirm", "reconfirm",
    "complete your", "follow the link", "click here", "click the link",
    "click below", "click the button",
})

_SHORTENED_URL_DOMAINS = frozenset({
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly",
    "rebrand.ly", "short.io", "tiny.cc", "is.gd", "clck.ru",
    "cutt.ly", "rb.gy", "shorturl.at", "tr.im", "u.to",
})

_SUSPICIOUS_TLDS = frozenset({
    ".xyz", ".top", ".club", ".online", ".site", ".live", ".download",
    ".stream", ".loan", ".win", ".bid", ".party", ".review", ".click",
    ".link", ".gq", ".ml", ".cf", ".ga", ".tk",
})

# ── Compiled regexes ──────────────────────────────────────────────────────────

_URL_RE      = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', re.IGNORECASE)
_IP_URL_RE   = re.compile(r'https?://(?:\d{1,3}\.){3}\d{1,3}', re.IGNORECASE)
_EMAIL_RE    = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
_HTML_LINK_RE = re.compile(r'<a\s[^>]*href', re.IGNORECASE)
_HTML_FORM_RE = re.compile(r'<form[\s>]', re.IGNORECASE)
_WS_RE       = re.compile(r'\s+')

# ── Feature extraction ────────────────────────────────────────────────────────

# Fixed feature order — MUST stay stable across training and inference
FEATURE_NAMES: List[str] = [
    "url_count",
    "has_ip_url",
    "has_shortened_url",
    "suspicious_url_score",
    "html_link_count",
    "html_form_count",
    "email_count",
    "exclamation_count",
    "uppercase_ratio",
    "urgency_score",
    "credential_score",
    "financial_score",
    "verification_score",
    "subject_urgency",
]


def _count_words_in_text(text_lower: str, word_set: frozenset) -> int:
    """Count how many words/phrases from word_set appear in text_lower."""
    count = 0
    for w in word_set:
        if w in text_lower:
            count += 1
    return count


def extract_security_features(subject: object, body: object) -> Dict[str, float]:
    """
    Extract cybersecurity heuristic features from raw (un-preprocessed) email text.

    All values are non-negative. The returned dict keys match FEATURE_NAMES.
    Safe for empty / None inputs.
    """
    # Coerce to strings
    subject_str = str(subject).strip() if subject is not None else ""
    body_str    = str(body).strip()    if body    is not None else ""

    # Guard nan-strings
    if subject_str.lower() in ("nan", "none", "<na>"):
        subject_str = ""
    if body_str.lower() in ("nan", "none", "<na>"):
        body_str = ""

    # Limit to 100 KB for security
    subject_str = subject_str[:100_000]
    body_str    = body_str[:100_000]

    combined = (subject_str + " " + body_str).lower()

    # ── URLs ────────────────────────────────────────────────────────────────
    urls = _URL_RE.findall(body_str)
    url_count = len(urls)

    has_ip_url = int(bool(_IP_URL_RE.search(body_str)))

    has_shortened_url = 0
    for url in urls:
        for domain in _SHORTENED_URL_DOMAINS:
            if domain in url.lower():
                has_shortened_url = 1
                break

    suspicious_url_score = 0
    for url in urls:
        url_lower = url.lower()
        for tld in _SUSPICIOUS_TLDS:
            if tld in url_lower:
                suspicious_url_score += 1
                break
        # Also flag @ in URL (evasion technique)
        if "@" in url:
            suspicious_url_score += 1

    # ── HTML ────────────────────────────────────────────────────────────────
    html_link_count = len(_HTML_LINK_RE.findall(body_str))
    html_form_count = len(_HTML_FORM_RE.findall(body_str))

    # ── Email addresses in body ─────────────────────────────────────────────
    email_count = len(_EMAIL_RE.findall(body_str))

    # ── Punctuation / style ─────────────────────────────────────────────────
    exclamation_count = combined.count("!")
    total_chars       = max(len(combined.replace(" ", "")), 1)
    uppercase_count   = sum(1 for c in (subject_str + body_str) if c.isupper())
    uppercase_ratio   = round(uppercase_count / total_chars, 4)

    # ── Word-list scores ────────────────────────────────────────────────────
    urgency_score      = _count_words_in_text(combined, _URGENCY_WORDS)
    credential_score   = _count_words_in_text(combined, _CREDENTIAL_WORDS)
    financial_score    = _count_words_in_text(combined, _FINANCIAL_WORDS)
    verification_score = _count_words_in_text(combined, _VERIFICATION_WORDS)
    subject_urgency    = _count_words_in_text(subject_str.lower(), _URGENCY_WORDS)

    return {
        "url_count":            float(url_count),
        "has_ip_url":           float(has_ip_url),
        "has_shortened_url":    float(has_shortened_url),
        "suspicious_url_score": float(suspicious_url_score),
        "html_link_count":      float(html_link_count),
        "html_form_count":      float(html_form_count),
        "email_count":          float(email_count),
        "exclamation_count":    float(exclamation_count),
        "uppercase_ratio":      float(uppercase_ratio),
        "urgency_score":        float(urgency_score),
        "credential_score":     float(credential_score),
        "financial_score":      float(financial_score),
        "verification_score":   float(verification_score),
        "subject_urgency":      float(subject_urgency),
    }


def features_to_list(feature_dict: Dict[str, float]) -> List[float]:
    """Return features in the fixed FEATURE_NAMES order as a list."""
    return [feature_dict[name] for name in FEATURE_NAMES]
