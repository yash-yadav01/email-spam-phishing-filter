"""
preprocessing.py
================
Text preprocessing pipeline for email classification.

Security requirement
--------------------
URLs are NEVER visited, fetched, or resolved.
HTML is parsed as text only — never executed or rendered.
"""

from __future__ import annotations

import re
import unicodedata

# Optional: BeautifulSoup for HTML stripping
try:
    from bs4 import BeautifulSoup  # type: ignore
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────

URL_TOKEN   = "urltoken"
EMAIL_TOKEN = "emailtoken"
IP_TOKEN    = "ipaddresstoken"

# Security-relevant stop words are intentionally KEPT (not in this set).
# Only generic high-frequency words are removed.
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "that", "this",
    "these", "those", "it", "its", "i", "me", "my", "we", "our", "you",
    "your", "he", "she", "they", "them", "his", "her", "their", "what",
    "which", "who", "when", "where", "how", "all", "each", "both", "few",
    "more", "most", "other", "some", "such", "no", "not", "only", "same",
    "than", "too", "very", "so", "up", "out", "if", "about", "into",
    "through", "during", "before", "after", "above", "between", "also",
    "then", "just", "because", "as", "until", "while", "although",
    "s", "t", "re", "ll", "ve", "d", "m",
})

# Regex patterns (compiled once at import time)
_URL_RE    = re.compile(
    r'https?://[^\s<>"\']+|www\.[^\s<>"\']+',
    re.IGNORECASE
)
_EMAIL_RE  = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
_IP_URL_RE = re.compile(
    r'https?://(?:\d{1,3}\.){3}\d{1,3}[^\s]*',
    re.IGNORECASE
)
_BARE_IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
_WS_RE      = re.compile(r'\s+')
# Keep letters, digits, !, ?, and spaces; remove other punctuation
_PUNCT_RE   = re.compile(r'[^a-z0-9!?\s]')


# ── HTML stripping ────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    """Remove HTML tags and return plain text. Never executes HTML."""
    if "<" not in text:
        return text
    if _BS4_AVAILABLE:
        try:
            soup = BeautifulSoup(text, "html.parser")
            return soup.get_text(separator=" ")
        except Exception:
            pass
    # Fallback: simple tag removal
    return re.sub(r'<[^>]+>', ' ', text)


# ── Core preprocessing ────────────────────────────────────────────────────────

def preprocess_text(text: object, is_subject: bool = False) -> str:
    """
    Clean email text for NLP while preserving security-relevant signals.

    Steps
    -----
    1. Coerce to str; handle None / NaN
    2. Strip HTML
    3. Normalize encoding (replace non-ASCII)
    4. Lowercase
    5. Replace IP-based URLs with ip_token
    6. Replace all URLs with url_token
    7. Replace email addresses with email_token
    8. Replace bare IP addresses with ip_token
    9. Normalize whitespace
    10. Remove punctuation except ! and ?
    11. Tokenise and remove stop words
    12. Return clean string

    Parameters
    ----------
    text       : input text (subject or body)
    is_subject : if True, apply lighter processing (preserve more tokens)

    Returns
    -------
    Cleaned string suitable for TF-IDF vectorisation.
    """
    if text is None:
        return ""
    s = str(text).strip()
    if s.lower() in ("nan", "none", "<na>", ""):
        return ""

    # Limit size for security (100 KB max per field)
    if len(s) > 100_000:
        s = s[:100_000]

    # 1. Strip HTML
    s = _strip_html(s)

    # 2. Normalize unicode -> ASCII-compatible
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", errors="ignore").decode("ascii")

    # 3. Lowercase
    s = s.lower()

    # 4. Replace IP-based URLs first (more specific pattern)
    s = _IP_URL_RE.sub(f" {IP_TOKEN} ", s)

    # 5. Replace all remaining URLs
    s = _URL_RE.sub(f" {URL_TOKEN} ", s)

    # 6. Replace email addresses
    s = _EMAIL_RE.sub(f" {EMAIL_TOKEN} ", s)

    # 7. Replace bare IP addresses
    s = _BARE_IP_RE.sub(f" {IP_TOKEN} ", s)

    # 8. Remove punctuation except ! and ?
    s = _PUNCT_RE.sub(" ", s)

    # 9. Normalize whitespace
    s = _WS_RE.sub(" ", s).strip()

    # 10. Tokenise and remove stop words
    tokens = s.split()
    if not is_subject:
        tokens = [t for t in tokens if t not in _STOPWORDS]

    return " ".join(tokens)


def preprocess_subject_and_body(subject: object, body: object) -> str:
    """
    Combine subject and body into a single preprocessed string.
    Subject tokens are given implicit weight by repetition.

    This is the primary entry point used by the training and inference
    pipelines to ensure consistent preprocessing.
    """
    clean_subject = preprocess_text(subject, is_subject=True)
    clean_body    = preprocess_text(body,    is_subject=False)
    # Prepend subject twice to give it slightly higher TF-IDF weight
    parts = []
    if clean_subject:
        parts.append(clean_subject)
        parts.append(clean_subject)
    if clean_body:
        parts.append(clean_body)
    return " ".join(parts)
