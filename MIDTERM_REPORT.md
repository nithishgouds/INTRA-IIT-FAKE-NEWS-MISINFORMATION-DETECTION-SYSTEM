# TruthLens: Fake News & Misinformation Detection System
## Midterm Report — Intra-IIT Hackathon 2026
**Track:** NLP / Trust & Safety | Non-Agentic AI/ML System  
**Submission Deadline:** 27th EOD

---

## 1. Problem Statement & Motivation

The proliferation of fake news and misinformation poses a significant threat to public discourse, democratic processes, and societal trust. Content moderators, journalists, and fact-checkers face an overwhelming volume of content that makes manual review infeasible at scale.

**TruthLens** addresses this challenge by providing an ML-powered system that:
- Analyzes textual content for misinformation signals
- Provides calibrated confidence scores (not binary outputs)
- Explains *why* content was flagged (not a black box)
- Supports human reviewers with a prioritized queue
- Learns from reviewer feedback over time

---

## 2. Solution Approach

### 2.1 Overall Architecture

We chose a **non-agentic, batch-processing architecture** aligned with the hackathon scope:

```
Input Text → Preprocessing → Feature Engineering → Classification → Explainability → UI
                                                         ↑
                               Source Credibility Scoring ┘
                                                    ↓
                                        Human Review Loop
                                                    ↓
                                     Feedback Storage (DB)
```

### 2.2 Technical Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | FastAPI (Python) | Async, fast, auto-docs, type-safe |
| Database | SQLite + SQLAlchemy | No-setup persistence, portable |
| ML Model | scikit-learn (LogReg + TF-IDF) | Interpretable, fast, effective baseline |
| Explainability | SHAP + custom feature weights | Industry-standard, model-agnostic |
| Frontend | Vanilla HTML/CSS/JS | No build step, zero dependencies |
| NLP | NLTK + VADER + TextBlob + textstat | Proven NLP library ecosystem |

### 2.3 Why Logistic Regression Over Transformers?

While transformer models (BERT, RoBERTa) achieve higher accuracy, we chose Logistic Regression + TF-IDF for:
1. **Interpretability**: Logistic regression coefficients directly translate to SHAP values
2. **Speed**: Sub-second inference, no GPU required
3. **SHAP compatibility**: LinearExplainer is highly efficient for linear models
4. **Hackathon scope**: The system is a complete working product, not a research prototype

The architecture is designed to be **model-agnostic** — a transformer can be swapped in by replacing `model.py`.

---

## 3. Feature Engineering

### 3.1 Sentiment Analysis
- **VADER** (Valence Aware Dictionary and sEntiment Reasoner): optimized for social media
- **TextBlob**: provides polarity (−1 to +1) and subjectivity (0=objective, 1=subjective)
- Fake news tends to have extreme sentiment and high subjectivity

### 3.2 Readability Metrics
- **Flesch Reading Ease**: Very easy/very hard reading correlates with different content types
- **Gunning Fog, SMOG, Coleman-Liau**: Grade-level estimates
- Misinformation often uses either very simple or intentionally complex language

### 3.3 Stylistic Markers (Custom Lexicons)
- **Sensational words**: "SHOCKING", "BOMBSHELL", "EXPOSED", "BREAKING", etc.
- **Hedge words**: "allegedly", "reportedly", "sources say" — unverified claims
- **Strong modal words**: "definitely", "EVERYONE KNOWS" — overconfident assertions
- **CAPS ratio**: Excessive capitalization is a strong fake news signal
- **Exclamation marks**: Emotional manipulation signal

### 3.4 Source Credibility
- Laplace-smoothed score: `(real_count + 2) / (total + 4)` 
- Seed data: 10 known reliable sources (Reuters, AP, BBC, etc.) and 10 unreliable (Infowars, etc.)
- Updated after every analyzed article
- Combined with DB history for final prediction

---

## 4. Classification Model

### 4.1 Training Pipeline
1. Load dataset (synthetic + any user-provided data)
2. Clean and lemmatize text
3. Fit TF-IDF vectorizer (20,000 features, bigrams, sublinear TF)
4. Extract 29 handcrafted linguistic features
5. Concatenate TF-IDF + handcrafted features
6. Normalize handcrafted features (StandardScaler)
7. Train Logistic Regression with class-balanced weights

### 4.2 Confidence Calibration
- Logistic regression natively outputs calibrated probabilities via sigmoid
- Decision thresholds: FAKE (≥65%), REAL (≤35%), UNCERTAIN otherwise
- The UNCERTAIN class explicitly communicates low-confidence predictions

### 4.3 Feedback Integration
- Reviewer-relabeled articles are included in subsequent retraining
- This implements a Human-in-the-Loop improvement cycle

---

## 5. Explainability Layer

### 5.1 SHAP Values
- **LinearExplainer** for logistic regression (efficient O(n) computation)
- Explains contribution of each feature to the FAKE probability
- Both TF-IDF features and handcrafted features are explained

### 5.2 Text Span Highlighting
- Post-hoc analysis identifies suspicious text spans:
  - Red: Sensational language ("SHOCKING", "BOMBSHELL")
  - Amber: Unverified claims ("allegedly", "reportedly")
  - Purple: Excessive capitalization (3+ char CAPS words)
- Shown interactively in the UI overlay

### 5.3 Feature Importance Display
- Top 10 features with impact bars
- Color-coded: red = suggests FAKE, green = suggests REAL
- Human-readable names and descriptions for each feature

---

## 6. Source Credibility Scoring

Each source is tracked with:
- Total articles analyzed
- Count of FAKE predictions, REAL predictions
- Laplace-smoothed credibility score

**Formula:** `credibility = (real_count + α) / (total + 2α)` where `α = 2`

Credibility is incorporated as an additional feature in prediction, and displayed separately in the UI to avoid conflating it with the content-based prediction.

**Important caveat:** Source credibility scores are explicitly flagged as dataset-derived estimates, not definitive trust ratings.

---

## 7. Product & User Experience

### 7.1 Target Users
- **Journalists**: Quick pre-publish fact-check on source material
- **Content Moderators**: Efficiently triage large volumes of content
- **Researchers**: Batch analysis of news datasets
- **Fact-checkers**: Prioritized review queue with explanations

### 7.2 User Journey
```
1. Open TruthLens frontend (index.html)
2. Paste article text OR click "Try Sample"
3. Optionally add source, author, URL
4. Click "Analyze Content"
5. See verdict (FAKE/REAL/UNCERTAIN) with confidence
6. Review probability bars, text highlights, feature importance
7. Provide feedback (Confirm/Dismiss/Relabel)
8. Move to Dashboard to manage queue
9. Optionally run batch analysis on full dataset
10. View Model Metrics for evaluation report
```

### 7.3 Design Decisions
- **Dark glassmorphism UI**: Premium feel, reduces eye strain for reviewers
- **No build step**: Frontend is pure HTML/CSS/JS for maximum portability
- **Uncertainty class**: Explicitly models low-confidence cases rather than forcing binary output
- **Non-destructive feedback**: Reviewer labels never overwrite original predictions

---

## 8. Evaluation Plan

### 8.1 Metrics
- Accuracy, Precision, Recall, F1 Score (macro + binary)
- AUC-ROC (threshold-independent)
- Confusion matrix (FP/FN analysis)

### 8.2 Failure Analysis
The system automatically samples failure cases:
- **False Positives**: Real news incorrectly flagged (journalist impact)
- **False Negatives**: Fake news missed (safety risk)

### 8.3 Current Baseline (Synthetic Dataset)
On the generated training dataset (600 samples, 80/20 split):
- Expected Accuracy: ~88-93%
- Expected F1: ~0.87-0.92
- Expected AUC-ROC: ~0.93-0.97

*Note: Synthetic data creates an optimistic estimate. Real-world performance on LIAR/ISOT will be lower and more representative.*

---

## 9. Steps Completed

| Step | Status |
|------|--------|
| Problem analysis & architecture design | ✅ Complete |
| Text preprocessing pipeline | ✅ Complete |
| Feature engineering (29 features) | ✅ Complete |
| Source credibility scoring | ✅ Complete |
| ML model (TF-IDF + LogReg + calibration) | ✅ Complete |
| SHAP explainability layer | ✅ Complete |
| Text span highlighting | ✅ Complete |
| FastAPI REST backend | ✅ Complete |
| SQLite database (5 tables) | ✅ Complete |
| Human-in-the-loop review workflow | ✅ Complete |
| Frontend (analysis, dashboard, batch, sources, metrics) | ✅ Complete |
| Batch CSV analysis | ✅ Complete |
| CSV export | ✅ Complete |
| Evaluation metrics reporting | ✅ Complete |
| README & documentation | ✅ Complete |
| Sample dataset | ✅ Complete |

---

## 10. Known Limitations

1. **Training data**: Synthetic dataset is less representative than LIAR/ISOT
2. **Language**: English only (multilingual support out of scope)
3. **Real-time**: No live social media crawling (batch-only, per scope)
4. **Context**: No cross-article comparison (optional extension)
5. **Model**: Logistic regression may miss subtle semantic patterns that BERT would catch

---

## 11. Future Work

1. Replace TF-IDF with DistilBERT embeddings for semantic understanding
2. Integrate real propagation signals (share counts, reply graphs)
3. Add user accounts and collaborative reviewer roles
4. Browser extension for in-situ analysis
5. Multilingual support (Spanish, Hindi priority)
6. Side-by-side article comparison for detecting contradictory claims
