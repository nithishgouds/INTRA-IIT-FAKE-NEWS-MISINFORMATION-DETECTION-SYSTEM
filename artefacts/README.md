# Artefacts — TruthLens: Fake News & Misinformation Detection System

**Intra-IIT Hackathon 2026 | Track: NLP / Trust & Safety**

| File | Description |
|------|-------------|
| `55_demo_vedio.mp4` | Full demo walkthrough video — covers the Analyze page, Dashboard, Batch upload, Sources credibility view, and Metrics panel |
| `55_report.tex` | LaTeX source for the project report (compile with `pdflatex 55_report.tex` to generate PDF) |
| `55_report.pdf` | Compiled PDF version of the project report *(add after compiling the .tex)* |

## Team

| Name | Roll Number |
|------|-------------|
| G Santhosh Reddy | CS23B022 |
| S Sri Nithish Goud | CS23B052 |

## Demo Video

[Watch on Google Drive](https://drive.google.com/file/d/1ea9JXSqfsS3_1it78I-8ab_D9Lihr-6U/view?usp=sharing)

## Report

The project report (`55_report.tex` / `55_report.pdf`) covers:
- Problem formulation & motivation
- System architecture (FastAPI backend + React 18 frontend)
- Feature engineering pipeline (29 length-invariant linguistic densities)
- Classification model (TF-IDF + Calibrated Logistic Regression)
- Explainability layer (SHAP + text span highlighting)
- Source credibility scoring (Laplace-smoothed Bayesian model)
- Human-in-the-Loop reviewer workflow
- Evaluation metrics (Accuracy, Precision, Recall, F1, AUC-ROC)
- Repository structure & local setup instructions

## How to Compile the Report

```bash
pdflatex 55_report.tex
pdflatex 55_report.tex   # Run twice to resolve cross-references and TOC
```

Requires a standard LaTeX distribution (TeX Live / MiKTeX) with packages:
`amsmath`, `booktabs`, `tabularx`, `xcolor`, `hyperref`, `listings`, `enumitem`, `tikz`, `tcolorbox`
