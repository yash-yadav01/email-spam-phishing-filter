"""About & Limitations page."""
import streamlit as st

st.set_page_config(page_title="About & Limitations", page_icon="ℹ️", layout="wide")
st.title("ℹ️ About & Limitations")

st.markdown("""
## About This Project

**Project:** AI-Based Email Spam and Phishing Detection System Using NLP and Machine Learning  
**Author:** Yash Yadav  
**Purpose:** Internship project demonstrating three-class email classification using traditional ML and NLP.

### What This System Does
- Classifies emails as **Legitimate**, **Spam**, or **Phishing**
- Provides a **heuristic phishing risk level** (LOW / MEDIUM / HIGH) independently of the ML classification
- Lists **triggered security indicators** with a human-readable explanation
- Does NOT visit any URLs, execute any HTML, or store submitted emails

### Technology Stack
| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Text features | TF-IDF (scikit-learn) |
| Cybersecurity features | Custom heuristic extractor |
| ML models | MultinomialNB, LogisticRegression, LinearSVC (calibrated) |
| HTML parsing | BeautifulSoup4 |
| Model persistence | joblib |
| Web application | Streamlit |
| Testing | pytest |

---

## System Limitations

1. **Dataset coverage** — The model is only as good as the training data. Novel phishing techniques not present in the corpus may be missed.
2. **English only** — Preprocessing and word lists are optimised for English-language emails.
3. **Text-only analysis** — URL safety is assessed by pattern matching, not live reputation lookup. No domains are visited.
4. **Heuristic thresholds** — Risk level thresholds are `HEURISTIC_DEFAULT` values and are not scientifically validated security thresholds.
5. **Not a security product** — This is an educational and research tool. Do not rely on it as your sole defence against phishing.
6. **Class imbalance** — The Enron corpus is much larger than the phishing corpus, which may affect recall on the minority class.

---

## Security Properties

| Property | Status |
|---|---|
| URLs visited | ❌ Never |
| HTML executed | ❌ Never |
| Email content stored | ❌ Never |
| Input size limit | ✅ 100 KB per field |
| Hardcoded secrets | ❌ None |
| External API calls | ❌ None |

---

## Future Improvements

- Transformer-based NLP (BERT / RoBERTa) for improved text understanding
- Multilingual support
- Real-time email client integration
- URL reputation API integration (opt-in)
- SHAP / LIME explainability
- Attachment analysis
- Continual learning with new phishing samples

---

> **Disclaimer:** This system is an ML-based analysis aid. It does not guarantee detection of all spam or phishing emails.  
> Heuristic risk scores are initial estimates and must not be treated as calibrated probabilities.  
> Always apply independent security judgment.
""")
