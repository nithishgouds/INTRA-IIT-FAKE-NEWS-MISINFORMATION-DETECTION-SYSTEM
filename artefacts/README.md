# Artefacts — TruthLens: Fake News & Misinformation Detection System

> **Intra-IIT Hackathon 2026**<br>
> **Track:** NLP / Trust & Safety | Non-Agentic AI/ML System

---

## Contents of This Folder

| File | Description |
|------|-------------|
| [`55_demo_vedio.mp4`](./55_demo_vedio.mp4) | Full end-to-end demo walkthrough video of the TruthLens application |
| [`55_report.tex`](./55_report.tex) | LaTeX source file of the final project report |
| `55_report.pdf` | Compiled PDF of the project report *(compile from `55_report.tex`)* |

---

## Demo Video

🎬 **[Watch on Google Drive](https://drive.google.com/file/d/1ea9JXSqfsS3_1it78I-8ab_D9Lihr-6U/view?usp=sharing)**

The demo video covers:
- Submitting a news article for analysis via the **Analyze** page
- Viewing the predicted verdict (`FAKE` / `REAL` / `UNCERTAIN`) with calibrated confidence scores
- Inspecting interactive **SHAP feature attribution** bars
- Reviewing **text span highlights** (sensational phrases, hedge words, excessive capitalization)
- Using the **Reviewer Dashboard** to confirm, dismiss, or relabel predictions
- Checking **Source Credibility** scores and verified domain registries
- Running **Batch CSV analysis** on multiple articles simultaneously
- Viewing **Model Metrics** (accuracy, precision, recall, F1-score, AUC-ROC, confusion matrix)

---

## Project Report (`55_report.tex` / `55_report.pdf`)

The report is a comprehensive LaTeX document describing the full TruthLens system. It covers:

### Sections

| # | Section | Description |
|---|---------|-------------|
| 1 | Executive Summary & Problem Formulation | Background, motivation, and formal problem statement |
| 2 | System Architecture & Engineering Design | FastAPI backend, React 18 frontend, SQLite schema, REST API reference |
| 3 | Feature Engineering & Preprocessing Pipeline | 29 length-invariant linguistic density features with formal mathematical definitions |
| 4 | Classification Model & Probability Calibration | TF-IDF + Logistic Regression hybrid pipeline, three-tier decision calibration ($\tau_{fake}=0.65$) |
| 5 | Explainability Layer & Evidence Presentation | SHAP `LinearExplainer`, additive feature attributions, interactive text span highlighter |
| 6 | Source Credibility Scoring & Domain Verification | Empirical Bayesian Laplace-smoothed credibility model, official domain registry, spoofing detection |
| 7 | Reviewer Dashboard & Human-in-the-Loop Workflow | Non-destructive reviewer feedback, audit trail, retraining integration |
| 8 | Experimental Evaluation & Performance Metrics | Classification metrics table, confusion matrix, false positive / false negative analysis |
| 9 | Repository Structure & Reproducibility Guide | Complete codebase hierarchy, setup & run instructions |
| 10 | Conclusion & Future Roadmap | Transformer upgrades, multilingual support, propagation graphs |

### How to Compile the PDF

**Option A — Overleaf (Recommended):**
1. Upload `55_report.tex` to [Overleaf](https://www.overleaf.com)
2. Click **Recompile**
3. Download the generated PDF

**Option B — Local (TeX Live / MiKTeX):**
```bash
pdflatex 55_report.tex
pdflatex 55_report.tex   # Run twice to resolve TOC and cross-references
```

**Required LaTeX packages:**
`amsmath`, `amssymb`, `geometry`, `booktabs`, `tabularx`, `xcolor`, `hyperref`,
`listings`, `enumitem`, `tikz` (with `arrows.meta`, `positioning`, `shapes.geometric`, `shadows`), `tcolorbox`

---

## About TruthLens

TruthLens is a full-stack, interpretable misinformation detection platform built for journalists, content moderators, fact-checkers, and researchers. It combines:

- **ML Pipeline:** TF-IDF n-gram features fused with 29 handcrafted length-invariant linguistic density metrics, classified by a class-balanced L2-regularized Logistic Regression model
- **Calibrated Predictions:** Three-tier output (`FAKE` / `REAL` / `UNCERTAIN`) with confidence scores computed as $2 \cdot |P(\text{FAKE}) - 0.5|$
- **Explainability:** SHAP `LinearExplainer` for local feature attribution; regex-based text span highlighting for sensational language, hedge words, and excessive capitalization
- **Source Credibility:** Laplace-smoothed Bayesian credibility scores; verified registry of official agencies (NASA, WHO, ISRO), tier-1 wire services (Reuters, AP, BBC), known hoax networks (InfoWars, NaturalNews), and satirical outlets (The Onion)
- **Human-in-the-Loop:** Non-destructive reviewer workflow (confirm / dismiss / relabel) with structured audit logging and retraining integration
- **Batch Processing:** CSV bulk upload with per-item predictions, aggregate statistics, and exportable results
- **Persistence:** SQLite database (5 relational tables: Articles, Predictions, Feedback, SourceCredibility, BatchJobs)

---

## Repository

📁 **[View Full Repository](https://github.com/nithishgouds/INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM)**

```
INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM/
├── artefacts/              ← You are here (demo video, report)
├── backend/                ← FastAPI Python backend
│   ├── app/
│   │   ├── core/           ← Preprocessing, feature extraction, model, explainer, credibility
│   │   ├── api/            ← REST endpoints
│   │   ├── db/             ← SQLAlchemy models & database session
│   │   └── schemas/        ← Pydantic request/response schemas
│   ├── data/               ← Sample labeled dataset (CSV)
│   └── models/             ← Serialized model artifacts (.joblib)
├── frontend/               ← React 18 + Vite SPA
│   └── src/pages/          ← Analyze, Dashboard, Batch, Sources, Metrics pages
├── start_all.bat           ← One-click launcher (Windows)
├── README.md               ← Full setup & usage guide
└── MIDTERM_REPORT.md       ← Midterm progress report
```

---

## Running the Application Locally

See the [main README](../README.md) for complete setup instructions.

**Quick start (Windows):**
```cmd
git clone https://github.com/nithishgouds/INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM.git
cd INTRA-IIT-FAKE-NEWS-MISINFORMATION-DETECTION-SYSTEM
```

**Terminal 1 — Backend:**
```cmd
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```cmd
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | TruthLens web application |
| http://localhost:8000/docs | Interactive Swagger API documentation |
| http://localhost:8000/health | Backend health & model status |
