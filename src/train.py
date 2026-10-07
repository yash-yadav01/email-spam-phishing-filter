"""
train.py
========
Trains and compares three candidate ML models on the combined
TF-IDF + cybersecurity feature set, then serialises the best model.

Candidate models
----------------
1. Multinomial Naive Bayes  (MultinomialNB)
2. Logistic Regression      (LogisticRegression, class_weight='balanced')
3. Linear SVM               (LinearSVC,          class_weight='balanced')

Data splitting
--------------
- 80% train / 20% test, stratified by label, random_state=42
- TF-IDF vectoriser is fitted ONLY on training data

Model selection priority
------------------------
1. Phishing Recall  (highest priority)
2. Macro F1
3. Overall Accuracy

No target accuracy is assumed. The winner is determined from actual
held-out test set results documented in evaluate.py.

Serialised artefacts (models/)
-------------------------------
- tfidf_vectorizer.joblib
- label_encoder.joblib
- best_model.joblib          (winner after evaluation)

TODO (Phase 7): Implement train_models() and save_artefacts() functions.
"""

# Implementation will be added in Phase 7.
