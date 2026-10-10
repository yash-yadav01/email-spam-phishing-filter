# Viva Questions and Answers
# AI-Based Email Spam and Phishing Detection System
# Author: Yash Yadav

---

## Python / General Programming

**Q1. Why did you use Python for this project?**  
Python has the most mature ML ecosystem (scikit-learn, pandas, NumPy) and fast development tools for prototyping NLP pipelines. It also integrates well with Streamlit for rapid web application development.

**Q2. What is a virtual environment and why did you use one?**  
A virtual environment isolates project dependencies from the system Python, ensuring reproducibility. Each project has its own package versions so different projects do not conflict.

---

## NLP / Text Processing

**Q3. What is TF-IDF and why did you use it instead of simple word counts?**  
TF-IDF (Term Frequency-Inverse Document Frequency) weighs terms by how frequent they are in a document relative to how common they are across all documents. This reduces the influence of very common words while highlighting distinctive terms. `sublinear_tf=True` further reduces the effect of very high frequencies.

**Q4. What is an n-gram? Why did you use bigrams?**  
An n-gram is a contiguous sequence of n words. Bigrams capture two-word phrases such as "click here" or "verify account" which are meaningful phishing signals but would be lost with unigrams only.

**Q5. Why did you keep `!` and `?` in preprocessing but remove other punctuation?**  
Exclamation marks and question marks are meaningful spam/phishing signals (urgency, credential requests). Other punctuation like commas and brackets has no discriminative value for this task.

**Q6. Why did you replace URLs with a token instead of removing them?**  
Simply removing URLs would lose the information that URLs are present at all. Replacing them with `urltoken` tells the TF-IDF vectorizer that URLs appeared without leaking the actual URL content into the vocabulary.

**Q7. What is stop-word removal and which words did you keep that NLP libraries usually remove?**  
Stop-word removal eliminates very common words that carry little information. This project preserves security-relevant terms like "urgent", "verify", "password", "login" that a generic stop list would wrongly remove.

---

## Machine Learning

**Q8. What is Multinomial Naive Bayes and why is it a good baseline for text classification?**  
MNB models the probability of each class given word frequencies using Bayes' theorem with a naive independence assumption. It is computationally very fast, works well with sparse TF-IDF features, and performs surprisingly well on text classification as a baseline.

**Q9. What is Logistic Regression in a multi-class setting?**  
For three or more classes, Logistic Regression uses the softmax function (one-vs-rest or multinomial). It learns a weight for each feature per class, and predicts the class with the highest probability. With `class_weight='balanced'` it compensates for class imbalance.

**Q10. What is a Support Vector Machine? Why did you use LinearSVC instead of SVC with RBF kernel?**  
SVM finds a hyperplane that maximises the margin between classes. LinearSVC uses a linear kernel, which is very efficient for high-dimensional sparse text features. An RBF kernel would be much slower and is not well-suited to TF-IDF vectors.

**Q11. Why did you wrap LinearSVC in CalibratedClassifierCV?**  
LinearSVC does not natively output probabilities. `CalibratedClassifierCV` applies Platt scaling via cross-validation to convert decision scores to calibrated probability estimates, which the UI uses for the confidence display.

**Q12. What is class imbalance and how did you address it?**  
Class imbalance means one class has far fewer examples than others. We used `class_weight='balanced'` in Logistic Regression and LinearSVC, which automatically increases the penalty for misclassifying minority class samples. Stratified train/test split also ensures each split preserves the class ratio.

---

## Evaluation

**Q13. What is a confusion matrix?**  
A confusion matrix is a square table where rows represent true classes and columns represent predicted classes. Each cell shows how many samples of a true class were predicted as each class. The diagonal represents correct predictions; off-diagonal cells are errors.

**Q14. What is the difference between precision and recall?**  
- **Precision:** of all emails predicted as class X, what fraction actually is class X. (Measures false positives.)
- **Recall:** of all emails that are actually class X, what fraction did the model correctly identify. (Measures false negatives.)

**Q15. Why did you prioritise Phishing Recall over Accuracy?**  
A missed phishing email (false negative) is far more dangerous than incorrectly flagging a legitimate email (false positive). Prioritising phishing recall minimises the risk of undetected phishing attacks.

**Q16. What is macro F1?**  
Macro F1 is the unweighted average of the F1 score for each class. It treats all classes equally regardless of how many samples each has, making it appropriate when minority class performance matters.

**Q17. What is data leakage and how did you prevent it?**  
Data leakage occurs when information from the test set influences training (e.g., fitting a scaler or vectorizer on all data before splitting). This project fits the TF-IDF vectorizer and MinMaxScaler **only** on training data and uses `transform()` (not `fit_transform()`) for test data and inference.

---

## Feature Engineering

**Q18. What cybersecurity features did you extract?**  
14 features: url_count, has_ip_url, has_shortened_url, suspicious_url_score, html_link_count, html_form_count, email_count, exclamation_count, uppercase_ratio, urgency_score, credential_score, financial_score, verification_score, subject_urgency.

**Q19. Why are IP-based URLs suspicious?**  
Phishing sites often use bare IP addresses (e.g., http://192.168.1.1) to evade domain-based blacklists and to host short-lived malicious servers.

**Q20. Why are URL shorteners a phishing signal?**  
URL shorteners (bit.ly, tinyurl.com, etc.) are used by attackers to hide the real destination URL and bypass link filters.

---

## Phishing Risk Engine

**Q21. Why is the phishing risk engine separate from the ML classifier?**  
The ML model and the heuristic engine capture different signal types. Keeping them separate means each can be interpreted, updated, and tested independently. The ML label is never silently overridden by the heuristic score — both are shown to the user.

**Q22. Are the heuristic thresholds scientifically validated?**  
No. The weights and thresholds are `HEURISTIC_DEFAULT` values — initial reasonable estimates. They are documented as such in the code, README, and this report. Validation would require expert-labelled data and formal calibration.

---

## Security

**Q23. Why does your application never visit URLs found in emails?**  
Following URLs would expose the analysis server to drive-by downloads, SSRF attacks, and remote code execution. Text-only analysis is the safe and correct approach.

**Q24. Why do you cap input at 100 KB?**  
To prevent denial-of-service attacks via extremely large inputs and to bound memory and processing time per request.

**Q25. How would you handle a request to log email content for debugging?**  
User-submitted email content is treated as sensitive and must not be stored or logged. Debugging should use synthetic test fixtures, not real user data.

---

## Deployment

**Q26. How did you deploy the application?**  
Target platform: Streamlit Community Cloud. Steps: push code (including trained model artefacts) to GitHub, connect the repository on streamlit.io/cloud, set the entry point to `app/app.py`, and deploy.  
**Actual deployment status:** _To be filled after deployment._

**Q27. What would happen if the model files are missing at runtime?**  
The `load_artefacts()` function raises `FileNotFoundError` with a clear message. The Streamlit app catches this and displays an error box with instructions to train the model, instead of crashing silently.

---

## Testing

**Q28. What is pytest and what did you test?**  
pytest is the standard Python testing framework. Tests cover: text preprocessing (17 tests), cybersecurity feature extraction (15 tests), phishing risk engine (14 tests), and the end-to-end prediction pipeline (17 tests, 16 skip until trained).

**Q29. How do your tests handle the case where the model is not yet trained?**  
Model-dependent tests use `pytest.mark.skipif` with a check for artefact availability. This ensures tests run as far as possible and skip gracefully rather than failing with misleading errors.
