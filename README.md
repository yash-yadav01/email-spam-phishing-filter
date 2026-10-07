# AI-Based Email Spam and Phishing Detection System Using NLP and Machine Learning

**Short name:** Email Spam & Phishing Filter
**Author:** Yash Yadav
**Status:** 🚧 In Development

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Objectives](#objectives)
3. [Features](#features)
4. [Architecture](#architecture)
5. [Technology Stack](#technology-stack)
6. [Dataset](#dataset)
7. [Data Preprocessing](#data-preprocessing)
8. [Feature Engineering](#feature-engineering)
9. [ML Models](#ml-models)
10. [Evaluation Methodology](#evaluation-methodology)
11. [Screenshots](#screenshots)
12. [Installation](#installation)
13. [Running Locally](#running-locally)
14. [Deployment](#deployment)
15. [Project Limitations](#project-limitations)
16. [Future Scope](#future-scope)
17. [License](#license)

---

## Problem Statement

> _This section will be completed after dataset collection and model evaluation._

Email remains the most common attack vector for cybercrime. Phishing emails — which impersonate trusted entities to steal credentials or financial information — are often misclassified by simple binary spam filters. This project builds a three-class classifier (Legitimate / Spam / Phishing) that incorporates both NLP-based text features and cybersecurity-oriented heuristic features to improve phishing detection accuracy.

---

## Objectives

1. Collect, merge, and clean publicly available labeled email datasets (legitimate, spam, phishing).
2. Build a reproducible NLP preprocessing pipeline that preserves phishing-relevant signals.
3. Extract TF-IDF text features combined with cybersecurity-specific heuristic features.
4. Train, compare, and select the best model from Naive Bayes, Logistic Regression, and Linear SVM.
5. Build a phishing risk engine that produces a risk level and human-readable explanation.
6. Deliver a professional multi-page Streamlit web interface.
7. Write a unit and functional test suite.
8. Document fully and deploy to Streamlit Community Cloud.

---

## Features

- ✅ Three-class classification: Legitimate / Spam / Phishing
- ✅ TF-IDF text features (unigrams + bigrams)
- ✅ Cybersecurity heuristic features (URL analysis, urgency language, credential keywords, etc.)
- ✅ Phishing risk engine: LOW / MEDIUM / HIGH with indicator list and explanation
- ✅ Model confidence where technically supported
- ✅ Multi-page Streamlit interface
- ✅ Model evaluation: accuracy, precision, recall, F1, confusion matrix
- ✅ No URLs are visited or executed — analysis is text-only

---

## Architecture

> _Architecture diagram will be added after implementation._

```
User Input (Subject + Body)
        ↓
  Text Preprocessing
        ↓
  TF-IDF Vectorizer  +  Security Feature Extractor
        ↓
  Trained ML Model (best of: MNB / LR / LinearSVC)
        ↓
  Phishing Risk Engine (heuristic — separate from ML)
        ↓
  Result: label + risk_level + confidence + indicators + explanation
```

---

## Technology Stack

| Category | Library / Tool | Version |
|----------|---------------|---------|
| Language | Python | 3.11+ |
| Data processing | pandas, NumPy | See requirements.txt |
| Machine Learning | scikit-learn | See requirements.txt |
| NLP | NLTK, scikit-learn TF-IDF | See requirements.txt |
| HTML parsing | BeautifulSoup4 | See requirements.txt |
| Visualization | Matplotlib, Seaborn | See requirements.txt |
| Model persistence | joblib | See requirements.txt |
| Web application | Streamlit | See requirements.txt |
| Testing | pytest | See requirements.txt |
| Version control | Git / GitHub | — |
| Deployment | Streamlit Community Cloud | — |

---

## Dataset

> _This section will be completed after datasets are downloaded and verified._

The following public datasets are candidates for use in this project. Actual records used, verified licenses, and download dates will be recorded here after dataset preparation.

| Dataset | Source | Classes | License | Records Used | Accessed |
|---------|--------|---------|---------|-------------|---------|
| SpamAssassin Public Corpus | spamassassin.apache.org | spam / ham | _To be verified_ | _TBD_ | _TBD_ |
| Enron Email Dataset | _Mirror URL TBD_ | ham | _To be verified_ | _TBD_ | _TBD_ |
| Nazario Phishing Corpus | monkey.org/~jose/phishing | phishing | _To be verified_ | _TBD_ | _TBD_ |
| CSDMC2010 Spam Corpus | csmining.org | spam / ham | _To be verified_ | _TBD_ | _TBD_ |

> ⚠️ PhishTank and OpenPhish are URL-only databases. They are **not** email datasets and are not used for the core email classifier.

---

## Data Preprocessing

> _This section will be completed after preprocessing module is implemented._

Key steps:
1. HTML parsing (extract plain text; count links, forms)
2. Encoding normalization
3. Lowercase conversion
4. URL extraction + token replacement (URL not visited)
5. Email address extraction + token replacement
6. IP address detection
7. Whitespace normalization
8. Punctuation handling (preserve ! and ?)
9. Tokenization
10. Stop-word removal (custom list preserving security-relevant terms)

---

## Feature Engineering

> _This section will be completed after feature engineering module is implemented._

Two feature types:
- **TF-IDF**: unigrams + bigrams, max 10,000 features, fitted on training data only
- **Cybersecurity features**: URL count, IP URLs, shortened URLs, urgency score, credential score, etc.

---

## ML Models

> _This section will be completed after model training and evaluation._

Three models are trained and compared:
1. Multinomial Naive Bayes
2. Logistic Regression (class_weight='balanced')
3. Linear SVM (class_weight='balanced')

**Selection priority:** Phishing Recall → Macro F1 → Overall Accuracy

Final model is selected after evaluation on the held-out test set. No target accuracy is pre-assumed.

---

## Evaluation Methodology

> _Actual metrics will be added after evaluation._

- 80/20 stratified train/test split, random_state=42
- Metrics: Accuracy, Precision, Recall, F1 (macro & weighted), per-class metrics
- Special focus: Phishing Recall and Phishing Precision
- Confusion matrix saved to `reports/figures/`

---

## Screenshots

> _Screenshots will be added after UI is implemented._

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/email-spam-phishing-filter.git
cd email-spam-phishing-filter

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

---

## Running Locally

> _Dataset download and model training instructions will be added in Phase 2 and Phase 7._

```bash
# After datasets are prepared and model is trained:
streamlit run app/app.py
```

---

## Deployment

> _Deployment URL and instructions will be added after Phase 15._

Deployment target: Streamlit Community Cloud

---

## Project Limitations

- Dataset quality and coverage affect model performance.
- Model is trained on English-language emails only.
- Novel phishing techniques not present in the training corpus may be missed.
- URL-based analysis is text-only; no URL reputation or domain age lookup is performed.
- Risk thresholds are heuristic initial values, not scientifically validated security thresholds.
- The system is a detection aid and does not guarantee 100% accuracy.

---

## Future Scope

- Transformer-based NLP (BERT/RoBERTa) for improved text understanding
- Multilingual phishing detection
- Real-time email client integration
- URL reputation API integration
- Attachment analysis
- Continual learning with new phishing samples
- Explainable AI (LIME/SHAP) for model explanations
- Browser or email plugin

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

> **Disclaimer:** This system is an ML-based analysis aid. It does not guarantee detection of all spam or phishing emails. Do not rely solely on this tool for security decisions.
