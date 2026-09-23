
# 🔍 TruthLens — Fake News & Misinformation Detection System

> **Intra-IIT Hackathon 2026** | Track: NLP / Trust & Safety | Non-Agentic AI/ML System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 📋 Overview

**TruthLens** is a full-stack AI-powered system for detecting fake news and misinformation in news articles and social media posts. It provides:

- **ML Classification** with calibrated confidence scores
- **Explainability** via feature importance (SHAP-based and heuristic)
- **Source Credibility Scoring** based on historical publishing patterns
- **Human-in-the-Loop Review Workflow** for journalists and fact-checkers
- **Batch Analysis** of CSV datasets
- **Beautiful Dark UI Dashboard** with real-time stats

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TruthLens System                         │
├────────────────────────┬────────────────────────────────────────┤
│      Frontend          │             Backend                    │
│   HTML/CSS/Vanilla JS  │         FastAPI + SQLite               │
│                        │                                        │
│  ┌─────────────────┐   │   ┌─────────────────────────────────┐  │
│  │ Analyze Page    │◄──┼──►│ POST /api/v1/analyze           │  │
│  │ Dashboard       │   │   │ GET  /api/v1/dashboard          │  │
│  │ Batch Upload    │   │   │ POST /api/v1/batch/analyze      │  │
│  │ Source Scores   │   │   │ POST /api/v1/feedback           │  │
│  │ Metrics Report  │   │   │ GET  /api/v1/metrics            │  │
│  └─────────────────┘   │   │ POST /api/v1/train              │  │
│                        │   └──────────────┬──────────────────┘  │
│                        │                  │                     │
│                        │   ┌──────────────▼──────────────────┐  │
│                        │   │          ML Pipeline            │  │
│                        │   │  Preprocessor → Features        │  │
│                        │   │  TF-IDF + LogReg (Calibrated)   │  │
│                        │   │  SHAP Explainer                 │  │
│                        │   │  Source Credibility Scorer      │  │
│                        │   └──────────────┬──────────────────┘  │
│                        │                  │                     │
│                        │   ┌──────────────▼──────────────────┐  │
│                        │   │      SQLite Database            │  │
│                        │   │  articles | predictions         │  │
│                        │   │  feedback | source_credibility  │  │
│                        │   │  batch_jobs                     │  │
│                        │   └─────────────────────────────────┘  │
└────────────────────────┴────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry + lifespan
│   │   ├── api/
│   │   │   └── routes.py            # All REST API endpoints
│   │   ├── core/
│   │   │   ├── preprocessor.py      # Text cleaning & tokenization
│   │   │   ├── feature_extractor.py # Linguistic feature engineering
│   │   │   ├── model.py             # ML model training & inference
│   │   │   ├── explainer.py         # SHAP + text highlights
│   │   │   ├── credibility.py       # Source credibility scoring
│   │   │   └── data_loader.py       # Sample dataset generation
│   │   ├── db/
│   │   │   ├── session.py           # SQLAlchemy session management
│   │   │   └── models.py            # ORM models
│   │   └── schemas/
│   │       └── schemas.py           # Pydantic request/response schemas
│   ├── models/                      # Saved model artifacts (.joblib)
│   ├── data/                        # Data files
│   └── requirements.txt
├── frontend/                        # Modern React + Vite Application
│   ├── src/
│   │   ├── api/client.js            # Axios client with Vite proxy
│   │   ├── components/              # Layout, Cards, Nav
│   │   ├── pages/                   # Analyze, Dashboard, Batch, Sources, Metrics
│   │   ├── App.jsx                  # React Router SPA root
│   │   ├── main.jsx
│   │   └── index.css                # Global modern dark design system
│   ├── package.json
│   └── vite.config.js               # Dev server & API proxy
├── run_backend.bat                  # One-click backend launcher (auto frees port 8000)
├── run_frontend.bat                 # One-click React frontend launcher
├── start_all.bat                    # Master launcher (starts both & opens browser)
└── README.md
```

---

## 🚀 Quick Start (Exact Links & Commands)

### ⚡ One-Click Launch (Recommended)
Simply double-click `start_all.bat` (or run `./start_all.bat` in terminal). It will:
1. Start the FastAPI backend on port 8000
2. Start the React frontend on port 5173
3. Automatically open your browser to **http://localhost:5173**

---

### 🖥️ Manual Startup (Two Terminals)

#### Terminal 1 — Start the Backend:
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **Backend API URL**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

#### Terminal 2 — Start the React Frontend:
```powershell
cd frontend
npm run dev
```
- **React Web Application**: [http://localhost:5173](http://localhost:5173)

---

## 🌐 API Reference

The backend exposes a full REST API at `http://localhost:8000`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Analyze a single article |
| `GET` | `/api/v1/dashboard` | Get paginated review queue |
| `GET` | `/api/v1/predictions/{id}` | Get detailed prediction |
| `POST` | `/api/v1/feedback` | Submit reviewer feedback |
| `POST` | `/api/v1/batch/analyze` | Upload CSV for batch analysis |
| `GET` | `/api/v1/batch/jobs` | List all batch jobs |
| `GET` | `/api/v1/sources` | Get source credibility profiles |
| `POST` | `/api/v1/train` | Trigger model retraining |
| `GET` | `/api/v1/metrics` | Get evaluation metrics |
| `GET` | `/api/v1/export/csv` | Export results as CSV |

**Interactive API Docs:** `http://localhost:8000/docs`

---

## 🧠 ML Pipeline

### 1. Text Preprocessing
- Lowercase normalization
- URL, email, and HTML tag removal
- Stopword removal + lemmatization (NLTK WordNetLemmatizer)

### 2. Feature Engineering
**Sentiment Features** (VADER + TextBlob):
- Compound, positive, negative, neutral sentiment
- Text polarity and subjectivity scores

**Readability Features** (textstat):
- Flesch Reading Ease, Kincaid Grade Level
- Gunning Fog, SMOG, Coleman-Liau indexes

**Stylistic Features**:
- Word count, sentence count, avg word length
- CAPS ratio, exclamation/question marks
- Sensational word ratio (custom lexicon)
- Hedge word count, strong modal assertions
- Unique word (vocabulary diversity) ratio
- Stopword ratio, URL presence

**Source Credibility**:
- Laplace-smoothed credibility score from publishing history
- Seed data for known reliable/unreliable sources

### 3. Classification Model
- **TF-IDF Vectorizer** (20,000 features, unigrams + bigrams, sublinear TF)
- **Logistic Regression** (L2 regularization, class-balanced, calibrated probabilities)
- **Combined features**: TF-IDF + 29 handcrafted linguistic features
- **Confidence thresholds**: `FAKE (≥65%)`, `REAL (≤35%)`, `UNCERTAIN` otherwise

### 4. Explainability Layer
- **SHAP LinearExplainer** for feature attribution on trained model
- **Feature-weight heuristics** as fallback when SHAP unavailable
- **Text span highlighting**: identifies sensational words, hedge language, CAPS
- Top-N feature display with impact direction (→ Fake / → Real)

### 5. Source Credibility Scoring
- Tracks every source analyzed in SQLite
- Laplace smoothing: `score = (real + 2) / (total + 4)`
- Seed credibility for 20+ known reliable/unreliable sources
- Updates after every prediction

---

## 📊 Evaluation Metrics

After training, the system reports:
- **Accuracy**, **Precision**, **Recall**, **F1 Score**, **AUC-ROC**
- **Confusion Matrix** (TP, TN, FP, FN breakdown)
- **Failure Case Analysis** (sample false positives and false negatives)

Metrics are accessible via the **Metrics** page in the UI or `/api/v1/metrics`.

---

## 🖥️ UI Features

### 📝 Content Analysis Page
- Text input with character/word count
- "Try Sample" buttons (real news / fake news)
- Verdict display: **FAKE / REAL / UNCERTAIN** with confidence gauge
- Probability bars (real vs fake)
- **Text highlighting**: color-coded suspicious spans
- Feature importance chart (top 10 factors)
- Linguistic profile grid (8 key metrics)
- **Human-in-the-Loop feedback**: Confirm / Dismiss / Relabel

### 📋 Review Dashboard
- Live stats: total, fake, real, pending review
- Sortable/filterable table (by label, status, source, date, risk score)
- Color-coded prediction badges
- Quick "View →" modal with full detail + feedback history
- CSV export button

### 📤 Batch Analysis
- Drag-and-drop CSV upload
- Animated progress bar
- Batch results summary (pie-chart-style breakdown)
- Batch job history with status tracking

### 🛡️ Source Credibility
- Credibility profiles for all analyzed sources
- Visual credibility bars (color-coded: green/yellow/red)
- Article count, fake/real breakdown

### 📈 Model Metrics
- Accuracy, F1, Precision, Recall, AUC displayed as big-number cards
- Confusion matrix visualization
- False positive/negative failure case examples

---

## 📦 Datasets

The system is compatible with these public datasets (not included due to size):

| Dataset | Description | Download |
|---------|-------------|----------|
| **LIAR** | Politifact labeled statements | [LIAR Dataset](https://paperswithcode.com/dataset/liar) |
| **FakeNewsNet** | PolitiFact + GossipCop | [FakeNewsNet](https://github.com/KaiDMML/FakeNewsNet) |
| **ISOT** | News article dataset | [ISOT Dataset](https://onlineacademiccommunity.uvic.ca/isot/) |

**Using a real dataset:**
```python
# In backend/app/core/data_loader.py, replace load_sample_data() 
# to load from your CSV:
import pandas as pd

def load_sample_data():
    df = pd.read_csv("data/your_dataset.csv")
    texts = df['text'].tolist()
    labels = df['label'].map({'fake': 1, 'real': 0, 'FAKE': 1, 'REAL': 0}).tolist()
    sources = df.get('source', pd.Series([''] * len(df))).tolist()
    return texts, labels, sources
```

---

## 💬 Human-in-the-Loop Workflow

```
Article Submitted
       │
       ▼
  ML Prediction
  (FAKE/REAL/UNCERTAIN + Confidence)
       │
       ▼
  Reviewer Dashboard
  (Prioritized queue by risk score)
       │
       ├─► Confirm: ML prediction was correct
       ├─► Dismiss: Flag is incorrect (not fake news)
       └─► Relabel: Assign correct label + optional note
              │
              ▼
       Feedback stored in DB
       (Never overwrites original prediction)
              │
              ▼
       Available for model retraining
       (POST /api/v1/train includes feedback)
```

---

## ⚠️ Responsible Use

- Model predictions are **probabilistic estimates**, not definitive proof
- Source credibility scores reflect **dataset patterns**, not absolute trustworthiness
- Avoid using this system as the sole arbiter of content truthfulness
- Always have human reviewers make final decisions
- The system clearly distinguishes **model predictions** from **verified facts**

---

## 🔮 Optional Extensions (Implemented as Stretch Goals)

- [x] Batch CSV analysis with drag-and-drop
- [x] CSV export of analysis results
- [x] Source history visualization
- [x] Reviewer feedback logging for retraining
- [x] Text span highlighting for suspicious language
- [ ] Browser extension (out of scope for this submission)
- [ ] Side-by-side article comparison
- [ ] Multilingual support

---

## 🏆 Judging Criteria Coverage

| Criterion | Coverage |
|-----------|----------|
| **Solution Idea & Innovation (15%)** | TF-IDF + LogReg + SHAP + source credibility scoring + human-in-the-loop |
| **Code Structure & Architecture (30%)** | Clean layered FastAPI + modular ML pipeline + SQLite persistence |
| **Demo Explanation (20%)** | Full UI with explanation panel, feature importance, text highlighting |
| **Output Accuracy (15%)** | Calibrated probabilities + evaluated metrics (accuracy, F1, AUC-ROC) |
| **Product Usability (20%)** | Premium dark UI, reviewer dashboard, batch analysis, feedback workflow |

---

## 👥 Team

**Intra-IIT Hackathon 2026** | Track: NLP / Trust & Safety

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.