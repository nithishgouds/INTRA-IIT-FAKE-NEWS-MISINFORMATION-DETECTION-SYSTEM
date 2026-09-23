"""
FastAPI Main Application Entry Point
Fake News & Misinformation Detection System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.api.routes import router
from app.core import model as ml_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Initialize database
    init_db()
    
    # Try to load pre-trained model, train if not found
    if not ml_model.load_model():
        print("No pre-trained model found. Training on sample data...")
        try:
            from app.core.data_loader import load_sample_data
            from sklearn.model_selection import train_test_split
            
            texts, labels, sources = load_sample_data()
            train_texts, test_texts, train_labels, test_labels, train_sources, test_sources = train_test_split(
                texts, labels, sources, test_size=0.2, random_state=42, stratify=labels
            )
            ml_model.train_model(train_texts, train_labels, train_sources)
            metrics = ml_model.evaluate_model(test_texts, test_labels, test_sources)
            print(f"[OK] Model trained! Accuracy: {metrics.get('accuracy', 'N/A'):.3f}, "
                  f"F1: {metrics.get('f1_score', 'N/A'):.3f}, "
                  f"AUC: {metrics.get('auc_roc', 'N/A'):.3f}")
        except Exception as e:
            print(f"[WARN] Could not train model: {e}. Using heuristic predictions.")
    else:
        print("[OK] Pre-trained model loaded successfully.")
    
    yield  # Application runs here
    
    print("[INFO] Shutting down Fake News Detection System...")


app = FastAPI(
    title="Fake News & Misinformation Detection System",
    description="""
    An ML-powered system for detecting fake news and misinformation in news articles and social media posts.
    
    ## Features
    - **Text Analysis**: Analyze individual articles with confidence scores and explanations
    - **Batch Processing**: Upload CSV files for bulk analysis
    - **Explainability**: SHAP-based feature importance and text highlighting
    - **Source Credibility**: Track and score publisher reliability
    - **Review Dashboard**: Human-in-the-loop review workflow
    - **Feedback Loop**: Reviewer feedback for continuous improvement
    
    ## Hackathon
    Intra-IIT Hackathon 2026 | Track: NLP / Trust & Safety
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "system": "Fake News & Misinformation Detection System",
        "version": "1.0.0",
        "hackathon": "Intra-IIT Hackathon 2026",
        "track": "NLP / Trust & Safety",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": ml_model.is_trained(),
        "model_version": ml_model.MODEL_VERSION,
    }
