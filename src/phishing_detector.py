"""
phishing_detector.py
====================
Heuristic phishing risk engine — completely separate from the ML classifier.

Risk levels: LOW (0-19), MEDIUM (20-49), HIGH (50+)
All thresholds and weights are HEURISTIC_DEFAULT values.
They are NOT scientifically validated security thresholds.

Security requirement
--------------------
URLs are analysed as TEXT ONLY. Never visited, fetched, or resolved.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from src.feature_engineering import extract_security_features

# ── HEURISTIC_DEFAULT thresholds ──────────────────────────────────────────────

# Score boundaries (HEURISTIC_DEFAULT)
_THRESHOLD_MEDIUM = 20
_THRESHOLD_HIGH   = 50

# Per-indicator score contributions (HEURISTIC_DEFAULT)
_INDICATOR_WEIGHTS = {
    "IP-based URL detected":             25,
    "Shortened URL detected":            15,
    "Suspicious URL / TLD detected":     10,
    "HTML form present":                 20,
    "Multiple external links":           10,
    "Credential-related language":       15,
    "Urgency language detected":         10,
    "Financial request language":        10,
    "Verification request language":     10,
    "Multiple exclamation marks":         5,
    "High uppercase ratio":               5,
    "Multiple email addresses in body":  10,
    "Subject contains urgency keywords": 10,
    "Multiple URLs in body":             10,
}


# ── Risk engine ───────────────────────────────────────────────────────────────

class PhishingDetector:
    """
    Evaluates an email for phishing indicators and assigns a risk level.

    Usage
    -----
        detector = PhishingDetector()
        result = detector.assess(subject="...", body="...")
        # result keys: risk_level, heuristic_score, triggered_indicators, explanation
    """

    def assess(self, subject: object, body: object) -> Dict:
        """
        Assess the phishing risk of an email.

        Parameters
        ----------
        subject : email subject (raw, un-preprocessed)
        body    : email body (raw, un-preprocessed)

        Returns
        -------
        dict with keys:
            risk_level          : "LOW" | "MEDIUM" | "HIGH"
            heuristic_score     : int (sum of triggered indicator weights)
            triggered_indicators: list of human-readable indicator strings
            explanation         : 1–3 sentence plain-language summary
        """
        features = extract_security_features(subject, body)
        triggered: List[str] = []
        score = 0

        def _add(indicator: str) -> None:
            triggered.append(indicator)
            nonlocal score
            score += _INDICATOR_WEIGHTS.get(indicator, 5)

        # Evaluate each indicator
        if features["has_ip_url"] >= 1:
            _add("IP-based URL detected")

        if features["has_shortened_url"] >= 1:
            _add("Shortened URL detected")

        if features["suspicious_url_score"] >= 1:
            _add("Suspicious URL / TLD detected")

        if features["html_form_count"] >= 1:
            _add("HTML form present")

        if features["html_link_count"] >= 5:
            _add("Multiple external links")

        if features["credential_score"] >= 1:
            _add("Credential-related language")

        if features["urgency_score"] >= 2:
            _add("Urgency language detected")

        if features["financial_score"] >= 2:
            _add("Financial request language")

        if features["verification_score"] >= 2:
            _add("Verification request language")

        if features["exclamation_count"] >= 3:
            _add("Multiple exclamation marks")

        if features["uppercase_ratio"] >= 0.15:
            _add("High uppercase ratio")

        if features["email_count"] >= 2:
            _add("Multiple email addresses in body")

        if features["subject_urgency"] >= 1:
            _add("Subject contains urgency keywords")

        if features["url_count"] >= 3:
            _add("Multiple URLs in body")

        # Determine risk level (HEURISTIC_DEFAULT thresholds)
        if score >= _THRESHOLD_HIGH:
            risk_level = "HIGH"
        elif score >= _THRESHOLD_MEDIUM:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        explanation = self._build_explanation(risk_level, triggered)

        return {
            "risk_level":           risk_level,
            "heuristic_score":      score,
            "triggered_indicators": triggered,
            "explanation":          explanation,
        }

    @staticmethod
    def _build_explanation(risk_level: str, triggered: List[str]) -> str:
        if not triggered:
            return (
                "No phishing indicators were detected in this email. "
                "Risk is assessed as LOW based on heuristic analysis. "
                "Note: absence of indicators does not guarantee safety."
            )
        n = len(triggered)
        samples = ", ".join(triggered[:3])
        suffix = f" among others ({n} total)" if n > 3 else ""
        if risk_level == "HIGH":
            return (
                f"This email triggered {n} high-risk indicators including: {samples}{suffix}. "
                "The combination of multiple phishing signals strongly suggests a phishing attempt. "
                "Exercise extreme caution and do not click any links or provide credentials."
            )
        elif risk_level == "MEDIUM":
            return (
                f"This email triggered {n} suspicious indicator(s) including: {samples}{suffix}. "
                "Some phishing signals are present. "
                "Verify the sender through an independent channel before taking any action."
            )
        else:
            return (
                f"This email triggered {n} minor indicator(s) including: {samples}{suffix}. "
                "Overall risk is LOW, but individual indicators may warrant caution. "
                "Always verify unexpected requests through trusted channels."
            )


# Module-level convenience instance
_detector = PhishingDetector()


def assess_phishing_risk(subject: object, body: object) -> Dict:
    """Module-level convenience wrapper for PhishingDetector.assess()."""
    return _detector.assess(subject=subject, body=body)
