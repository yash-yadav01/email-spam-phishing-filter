"""
preprocessing.py
================
Text preprocessing pipeline for email classification.

Design principle
----------------
The pipeline cleans email text for NLP purposes WITHOUT destroying
cybersecurity signals. URLs, email addresses, and IP addresses are
extracted and counted BEFORE being replaced with placeholder tokens.

Pipeline steps (in order)
--------------------------
1.  HTML parsing      — extract plain text; count links and forms
2.  Encoding norm     — decode to UTF-8; replace non-ASCII with space
3.  Lowercase         — convert entire text to lowercase
4.  URL extraction    — count, record domains; replace with url_token
5.  Email extraction  — count; replace with email_token
6.  IP detection      — flag bare IP addresses
7.  Whitespace norm   — collapse whitespace to single space
8.  Punctuation       — keep ! and ?; remove other punctuation
9.  Tokenisation      — split on whitespace
10. Stop-word removal — custom list preserving security-relevant terms
11. Return cleaned string for TF-IDF

Security requirement
--------------------
URLs are NEVER visited, fetched, or resolved.
HTML is parsed as text only — never executed or rendered.

TODO (Phase 3): Implement preprocess_text() and helper functions.
"""

# Implementation will be added in Phase 3.
