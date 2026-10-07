"""
phishing_detector.py
====================
Heuristic phishing risk engine.

Purpose
-------
Evaluates cybersecurity features of an email and produces:
  - risk_level          : "LOW" | "MEDIUM" | "HIGH"
  - triggered_indicators: list of human-readable strings
  - explanation         : 1–3 sentence plain-language summary

IMPORTANT
---------
This component is COMPLETELY SEPARATE from the ML classifier.
It does NOT change, override, or influence the ML classification label.
The ML label and the risk level are always computed independently and
displayed separately in the UI.

Heuristic weights and thresholds
---------------------------------
All weights and thresholds in this module are HEURISTIC_DEFAULT values.
They are NOT scientifically validated security thresholds.
They are initial values and must be documented as such in:
  - source code comments (HEURISTIC_DEFAULT)
  - README.md
  - the internship report

Default thresholds:
  Score  0–19  → LOW
  Score 20–49  → MEDIUM
  Score 50+    → HIGH

Security requirement
--------------------
URLs found in emails are analysed as TEXT ONLY.
They are NEVER visited, fetched, resolved, or executed.

TODO (Phase 9): Implement PhishingDetector class.
"""

# Implementation will be added in Phase 9.
