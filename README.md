# TruthLens: Fake News and Misinformation Detection System

TruthLens is a full-stack machine-learning application for analysing news articles and social-media-style posts. It predicts whether submitted text is `FAKE`, `REAL`, or `UNCERTAIN`, displays confidence and probabilities, explains the prediction, evaluates the source, and stores results for later review.

This project was created for the **Intra-IIT Hackathon 2026**, under the **NLP / Trust and Safety** track. It is a decision-support tool, not a replacement for professional fact-checking.

## What The Application Does

The application has two parts:

- **React + Vite frontend:** the web interface at `http://localhost:5173`.
- **FastAPI backend:** the machine-learning API at `http://localhost:8000`.

The main workflow is:

1. A user enters an article title, article text, URL, source, and author.
2. The backend combines the title and text and runs the saved ML model.
3. The system returns a label, confidence, fake/real probabilities, linguistic features, text highlights, source credibility, and important factors.
4. The article and prediction are saved in a local SQLite database.
5. A reviewer can confirm, dismiss, or relabel the prediction.

The interface includes:

- **Analyze:** analyse one article or post and inspect the explanation.
- **Dashboard:** browse previous predictions and review statuses.
- **Batch:** upload a CSV and analyse many records.
- **Sources:** inspect source history and credibility scores.
- **Metrics:** view model evaluation metrics and failure examples.

## Technology Used

- Python 3.10 or 3.11 recommended
- FastAPI and Uvicorn
- React 18 and Vite
- scikit-learn TF-IDF and logistic regression model
- SHAP-based explainability with a fallback feature explanation
- NLTK, VADER, TextBlob, and textstat for language features
- SQLAlchemy with SQLite for local persistence

## Repository Contents

```text
INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM/
├── backend/
│   ├── app/
│   │   ├── main.py                  FastAPI application and startup logic
│   │   ├── api/routes.py             REST API endpoints
│   │   ├── core/
│   │   │   ├── preprocessor.py      Text cleaning and preprocessing
│   │   │   ├── feature_extractor.py Linguistic and sentiment features
│   │   │   ├── model.py             Model loading, training, and prediction
│   │   │   ├── explainer.py         Explanations and suspicious text highlights
│   │   │   ├── credibility.py       Source credibility evaluation
│   │   │   └── data_loader.py       Sample dataset loading
│   │   ├── db/
│   │   │   ├── database.py          SQLite connection and initialization
│   │   │   └── models.py            Database tables
│   │   └── schemas/schemas.py        API request and response schemas
│   ├── data/sample_dataset.csv       Included sample training data
│   ├── models/
│   │   ├── fake_news_model.joblib    Saved classifier
│   │   ├── tfidf_vectorizer.joblib   Saved text vectorizer
│   │   └── metrics.json              Saved evaluation metrics
│   └── requirements.txt              Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/client.js             Frontend API client
│   │   ├── components/               Shared layout and card components
│   │   └── pages/                    Analyze, dashboard, batch, source, metrics pages
│   ├── package.json                  JavaScript dependencies and scripts
│   └── vite.config.js                Port and backend proxy configuration
├── run_backend.bat                   Windows backend launcher
├── run_frontend.bat                  Windows frontend launcher
├── start_all.bat                     Windows launcher for both services
├── start.bat                         Windows backend setup and launcher
└── README.md                         This guide
```

`frontend/node_modules/`, Python virtual environments, caches, and the generated database are intentionally not stored in Git. They are created locally during setup or first use.

## Requirements

Before cloning or running the project, install:

1. **Git:** https://git-scm.com/downloads
2. **Python 3.10 or 3.11:** https://www.python.org/downloads/
3. **Node.js 18 or newer:** https://nodejs.org/

During Python installation on Windows, enable **Add Python to PATH**. After installation, verify the tools in PowerShell:

```powershell
git --version
python --version
node --version
npm --version
```

## Evaluator Setup After Cloning

These are the complete steps for a fresh Windows computer.

### 1. Clone the repository

Open PowerShell and run:

```powershell
git clone https://github.com/nithishgouds/INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM.git
cd INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM
```

### 2. Create and activate the Python environment

Run these commands from the project root:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

If PowerShell blocks environment activation, run this once in the same PowerShell window and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
backend\.venv\Scripts\Activate.ps1
```

### 3. Install frontend dependencies

Open a second PowerShell window, move to the project root, and run:

```powershell
cd path\to\INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM
cd frontend
npm install
```

This creates the local `frontend/node_modules` folder. It is required to run the frontend but is not committed to Git.

### 4. Start the application

The simplest option is to return to the project root and double-click `start_all.bat`, or run:

```powershell
cd path\to\INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM
.\start_all.bat
```

If PowerShell does not accept that command, use:

```powershell
cmd /c start_all.bat
```

The launcher opens two command windows, starts both services, and opens the browser at:

**http://localhost:5173**

Keep both command windows open while using the application.

## Manual Startup

Manual startup is useful if the evaluator wants to see backend and frontend logs separately.

### Terminal 1: backend

```powershell
cd path\to\INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM
backend\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Terminal 2: frontend

```powershell
cd path\to\INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM\frontend
npm run dev
```

Then open **http://localhost:5173** in a browser.

The important URLs are:

| URL | Purpose |
|---|---|
| http://localhost:5173 | Main TruthLens web application |
| http://localhost:8000 | Backend root/status information |
| http://localhost:8000/docs | Interactive Swagger API documentation |
| http://localhost:8000/health | Backend health and model status |

## First Evaluation Walkthrough

After the page opens:

1. Open **Analyze**.
2. Enter an article with at least 10 characters in the text field, or use one of the sample buttons.
3. Optionally add a title, source such as `reuters.com`, URL, and author.
4. Submit the article.
5. Inspect the verdict, confidence, fake/real probability bars, source evaluation, highlighted text, and explanation factors.
6. Open **Dashboard** to see the saved prediction.
7. Use the review controls to confirm, dismiss, or relabel the prediction.
8. Open **Sources** to see source history.
9. Open **Metrics** to see the saved model metrics.
10. Open **Batch** to upload a CSV and test multiple articles.

The included sample model is loaded automatically from `backend/models`. If those files are unavailable, the backend attempts to train on `backend/data/sample_dataset.csv` during startup.

## Batch CSV Format

The batch upload accepts a CSV with a `text` column. The following columns are supported:

```csv
title,text,source,author,url
Example title,"Example article text with at least ten characters.",example.com,Example Author,https://example.com/article
```

`text` is the important required column. `title`, `source`, `author`, and `url` are optional. The included file `backend/data/sample_dataset.csv` shows the sample dataset format; its `label` column is useful for training/evaluation data but is not needed for a new prediction upload.

## API Quick Reference

All application endpoints are under `/api/v1`:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/analyze` | Analyse one article or post |
| `GET` | `/dashboard` | List saved predictions and summary statistics |
| `GET` | `/predictions/{id}` | View one prediction in detail |
| `POST` | `/feedback` | Confirm, dismiss, or relabel a prediction |
| `POST` | `/batch/analyze` | Upload a CSV for batch analysis |
| `GET` | `/batch/jobs` | List batch jobs |
| `GET` | `/sources` | List source credibility records |
| `GET` | `/metrics` | Return model metrics |
| `POST` | `/train` | Retrain the model using the supported training flow |
| `GET` | `/export/csv` | Export stored results as CSV |

Example request for one article:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:8000/api/v1/analyze `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"title":"Example article","text":"This is an example article containing enough text for analysis.","source":"example.com"}'
```

The complete request and response schemas are available at `http://localhost:8000/docs`.

## How The Prediction Works

The system combines several signals:

1. **Preprocessing:** normalises text and removes or handles URLs, email addresses, HTML, stopwords, and word forms.
2. **TF-IDF text features:** represents important unigrams and bigrams from the text.
3. **Linguistic features:** includes sentiment, readability, word counts, punctuation, capitalisation, sensational language, hedging, and vocabulary diversity.
4. **Classifier:** uses the saved scikit-learn model to estimate fake and real probabilities.
5. **Decision label:** returns `FAKE`, `REAL`, or `UNCERTAIN` based on the configured confidence thresholds.
6. **Explainability:** uses SHAP when available and falls back to feature-weight explanations when necessary.
7. **Source evaluation:** estimates source credibility using source history and known seed patterns.

The output is a model estimate. A `FAKE` result does not prove that an article is false, and a `REAL` result does not prove that it is true.

## Data And Local Files

- `backend/models/*.joblib` and `backend/models/metrics.json` are committed runtime artifacts, so a fresh clone can use the same saved model.
- `backend/data/sample_dataset.csv` is included sample data.
- `backend/fakenews.db` is created automatically when the backend starts. It stores articles, predictions, feedback, source history, and batch jobs.
- The database is local and is intentionally ignored by Git. Delete `backend/fakenews.db` to reset local application history.
- `frontend/node_modules` is generated by `npm install` and is intentionally ignored by Git.

## Troubleshooting

### `python` is not recognized

Install Python and enable **Add Python to PATH**, then reopen PowerShell. On some systems, use `py` instead of `python`.

### `npm` is not recognized

Install Node.js, reopen PowerShell, and verify with `node --version` and `npm --version`.

### Port 8000 or 5173 is already in use

Stop the process using that port, then restart the relevant service. `run_backend.bat` attempts to free port 8000 automatically. The frontend is configured for port 5173.

### The frontend says it cannot reach the API

Check that the backend terminal is still running and that `http://localhost:8000/health` opens successfully. The Vite development server proxies `/api` and `/health` requests to port 8000.

### The browser opens but the page is blank

Stop the frontend with `Ctrl+C`, run `npm install` inside `frontend`, and start it again with `npm run dev`. Check the frontend terminal for build errors.

### Model loading or SHAP errors appear

Confirm that the three files in `backend/models` exist and that the virtual environment was installed from `backend/requirements.txt`. The backend has a fallback path and can train from the included sample data when a saved model cannot be loaded.

### How to stop the application

Press `Ctrl+C` in each running terminal. If `start_all.bat` opened separate windows, close those windows after stopping the servers.

## Responsible Use

- Treat every prediction as a probabilistic signal, not a verified fact.
- Use human review before publishing, removing, or escalating content.
- Source credibility is based on observed history and seed data; it is not an absolute ranking of a publisher.
- Do not use the system as the sole decision-maker for high-impact or safety-critical situations.

## Team And Context

**Intra-IIT Hackathon 2026**
Track: **NLP / Trust and Safety**
