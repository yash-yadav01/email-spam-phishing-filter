"""
feature_engineering.py
=======================
Extracts two types of features for email classification:

A. TF-IDF text features
-----------------------
- Input: preprocessed email text (subject + body concatenated)
- Unigrams and bigrams, max 10,000 features
- Fitted ONLY on training data; transform applied to test/inference
- Serialised to models/tfidf_vectorizer.joblib

B. Cybersecurity / phishing heuristic features
-----------------------------------------------
All features computed from RAW (un-preprocessed) text to preserve signal.

Feature list:
  url_count          — number of URLs detected
  domain_count       — unique domains across all URLs
  has_ip_url         — 1 if any URL uses a bare IP address (phishing evasion)
  has_shortened_url  — 1 if bit.ly / tinyurl / t.co / etc. detected
  suspicious_url_score — count of URLs with suspicious TLDs or path patterns
  exclamation_count  — number of ! characters (urgency/spam signal)
  uppercase_ratio    — ratio of uppercase to total characters
  urgency_score      — count of urgency words (urgent, expires, act now …)
  credential_score   — count of credential words (password, login, …)
  financial_score    — count of financial words (bank, transfer, …)
  verification_score — count of verification language (verify, confirm …)
  html_link_count    — number of <a href> links in raw HTML
  html_form_count    — number of <form> elements
  email_count        — number of email addresses in body
  subject_urgency    — urgency score applied to subject only

Note: weights and thresholds used here are HEURISTIC_DEFAULT values.
They are not scientifically validated security thresholds.

TODO (Phase 6): Implement extract_tfidf_features() and
                extract_security_features() functions.
"""

# Implementation will be added in Phase 6.
