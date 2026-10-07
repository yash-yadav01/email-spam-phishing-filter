"""
prepare_dataset.py
==================
Loads raw email datasets from data/raw/, maps columns to the standard
schema (subject, body, label), normalises labels, merges all sources,
removes duplicates, and writes the final dataset to
data/processed/dataset.csv.

Standard schema
---------------
subject : str  — Email subject line (empty string if not available)
body    : str  — Email body text (HTML stripped during preprocessing)
label   : str  — One of: legitimate | spam | phishing

Rules
-----
- Never modify any file inside data/raw/.
- All output goes to data/processed/.
- Labels must be validated; unknown labels cause a hard failure.
- All actual dataset record counts, source URLs, licenses, and access
  dates must be recorded in README.md after running this script.
- Do NOT fabricate, generate, or copy records. Use only the downloaded
  public datasets.

TODO (Phase 2): Implement loader functions for each dataset.
"""

# Implementation will be added in Phase 2.
