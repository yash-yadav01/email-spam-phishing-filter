# Presentation Outline (12–15 Slides)
# AI-Based Email Spam and Phishing Detection System Using NLP and Machine Learning
# Author: Yash Yadav

---

## Slide 1 — Title Slide
- Project title
- Author: Yash Yadav
- Internship / Academic context
- Date

## Slide 2 — Motivation & Problem Statement
- Scale of email-based cybercrime
- Phishing vs spam: why they need different handling
- Gap in binary spam filters
- Objective: three-class classifier

## Slide 3 — Proposed Solution Overview
- Architecture diagram:
  Input → Preprocessing → TF-IDF + Security Features → ML Model + Risk Engine → Output
- Three-class labels: Legitimate / Spam / Phishing
- Two independent subsystems: ML classifier + heuristic risk engine

## Slide 4 — Dataset
- Enron Spam CSV (legitimate + spam)
- Nazario Phishing Corpus (phishing)
- Label mapping table
- Class distribution bar chart (from reports/figures/class_distribution.png)
- Note: raw data excluded from repository

## Slide 5 — Text Preprocessing Pipeline
- 10-step pipeline (HTML strip → URL tokens → lowercase → stopword removal)
- Why URL token replacement (not deletion)
- Why `!` and `?` are preserved
- Security rule: URLs are NEVER visited

## Slide 6 — Feature Engineering
- TF-IDF: unigrams + bigrams, up to 10,000 features
- 14 cybersecurity heuristic features (table or list)
- Why features are extracted from raw text, not preprocessed text
- Feature scaling: MinMaxScaler for non-negative MNB compatibility

## Slide 7 — Model Training & Comparison
- Three candidate models: MNB, Logistic Regression, LinearSVC (calibrated)
- 80/20 stratified split, random_state=42
- Data leakage prevention: TF-IDF fitted only on training data
- Selection criteria: Phishing Recall → Macro F1 → Accuracy

## Slide 8 — Evaluation Results
- Table: Accuracy, Macro F1, Phishing Recall for each model
- Confusion matrix (from reports/figures/confusion_matrix.png)
- Best model selected: [TBD after training]
- All metrics from held-out test set only

## Slide 9 — Phishing Risk Engine
- Completely separate from ML classifier
- 14 indicators with HEURISTIC_DEFAULT score weights
- Thresholds: LOW (0–19), MEDIUM (20–49), HIGH (50+)
- Returns: risk_level, triggered_indicators, explanation
- Does NOT change the ML label

## Slide 10 — Streamlit Web Application
- Screenshot or demo of Email Analyzer page
- Five pages overview
- Color coding: green=legitimate, orange=spam, red=phishing
- Safety disclaimer visible in UI

## Slide 11 — Security Review
- Table of security properties (URLs never visited, no storage, etc.)
- Input size limit (100 KB)
- Heuristic disclaimer
- No hardcoded secrets or external API calls

## Slide 12 — Testing
- 47 unit tests across four test files
- Test categories: preprocessing, feature engineering, phishing detector, prediction pipeline
- All model-independent tests: PASSED
- Prediction tests: graceful skip when model not trained

## Slide 13 — Deployment
- Streamlit Community Cloud
- Steps: GitHub → New App → set app/app.py → Deploy
- Deployment status: [TBD]
- Live URL: [TBD]

## Slide 14 — Limitations & Future Scope
**Limitations:**
- English only
- Heuristic thresholds not scientifically validated
- Class imbalance may affect phishing recall

**Future scope:**
- BERT/RoBERTa NLP
- URL reputation API (opt-in)
- SHAP/LIME explainability
- Multilingual support

## Slide 15 — Conclusion & Key Learnings
- What was built and demonstrated
- Key technical decisions (TF-IDF + security features, separate risk engine)
- Skills developed: NLP, ML, feature engineering, web development, testing
- Thank You / Questions
