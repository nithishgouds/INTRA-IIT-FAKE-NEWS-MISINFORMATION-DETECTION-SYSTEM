"""
Main analysis API endpoints
"""
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Article, Prediction, Feedback, BatchJob
from app.core import model as ml_model
from app.core.explainer import explain_with_shap, highlight_suspicious_text, get_top_features
from app.core.credibility import (
    get_source_credibility, update_source_credibility, get_seed_credibility, get_all_sources
)
from app.schemas.schemas import (
    AnalyzeRequest, AnalyzeResponse, FeedbackRequest, FeedbackResponse,
    DashboardResponse, DashboardItem, MetricsResponse, SourceCredibilityResponse,
    BatchJobResponse
)

router = APIRouter()


@router.post("/analyze", response_model=dict)
async def analyze_article(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze a single article/post for misinformation."""
    
    # Get source credibility
    db_cred = get_source_credibility(db, request.source)
    seed_cred = get_seed_credibility(request.source)
    # Combine: if db has enough history use that, otherwise use seed
    source_cred = (db_cred + seed_cred) / 2
    
    # Store article
    article = Article(
        title=request.title,
        text=request.text,
        url=str(request.url) if request.url else None,
        source=request.source,
        author=request.author,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # Run ML prediction
    result = ml_model.predict(request.text, source=request.source or "")
    features = result["features"]
    
    # Generate explanation
    _model = ml_model._model
    _vectorizer = ml_model._vectorizer
    
    if _model and _vectorizer:
        explanation = explain_with_shap(_model, _vectorizer, request.text, request.source or "")
    else:
        top_feats = get_top_features(features)
        explanation = {
            "method": "feature_weights",
            "top_features": top_feats,
            "shap_values": None,
        }
    
    # Text highlights
    highlights = highlight_suspicious_text(request.text, features)
    
    # Store prediction
    prediction = Prediction(
        article_id=article.id,
        label=result["label"],
        confidence=result["confidence"],
        fake_probability=result["fake_probability"],
        real_probability=result["real_probability"],
        sentiment_score=features.get("vader_compound"),
        subjectivity_score=features.get("textblob_subjectivity"),
        readability_score=features.get("flesch_reading_ease"),
        source_credibility_score=source_cred,
        linguistic_features={k: round(float(v), 4) for k, v in features.items()},
        top_features=explanation.get("top_features", []),
        model_version=result["model_version"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    # Update source credibility with this prediction
    if request.source:
        update_source_credibility(db, request.source, result["label"])
    
    return {
        "article": {
            "id": article.id,
            "title": article.title,
            "text": article.text,
            "source": article.source,
            "author": article.author,
            "url": article.url,
            "submitted_at": article.submitted_at.isoformat(),
        },
        "prediction": {
            "id": prediction.id,
            "label": prediction.label,
            "confidence": prediction.confidence,
            "fake_probability": prediction.fake_probability,
            "real_probability": prediction.real_probability,
            "sentiment_score": prediction.sentiment_score,
            "subjectivity_score": prediction.subjectivity_score,
            "readability_score": prediction.readability_score,
            "source_credibility_score": prediction.source_credibility_score,
            "review_status": prediction.review_status,
            "predicted_at": prediction.predicted_at.isoformat(),
            "model_version": prediction.model_version,
        },
        "explanation": explanation,
        "highlights": highlights,
        "linguistic_features": features,
    }


@router.get("/dashboard")
async def get_dashboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    label: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("predicted_at"),
    sort_order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db)
):
    """Get paginated dashboard with flagged content for review."""
    query = db.query(Prediction, Article).join(Article, Prediction.article_id == Article.id)
    
    if label:
        query = query.filter(Prediction.label == label.upper())
    if review_status:
        query = query.filter(Prediction.review_status == review_status)
    if source:
        query = query.filter(Article.source.ilike(f"%{source}%"))
    
    total = query.count()
    
    if sort_by == "confidence":
        order_col = Prediction.confidence
    elif sort_by == "fake_probability":
        order_col = Prediction.fake_probability
    else:
        order_col = Prediction.predicted_at
    
    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    items_raw = query.offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for pred, art in items_raw:
        items.append({
            "prediction_id": pred.id,
            "article_id": art.id,
            "title": art.title,
            "text_preview": art.text[:200] + "..." if len(art.text) > 200 else art.text,
            "source": art.source,
            "author": art.author,
            "label": pred.label,
            "confidence": pred.confidence,
            "fake_probability": pred.fake_probability,
            "review_status": pred.review_status,
            "reviewer_label": pred.reviewer_label,
            "predicted_at": pred.predicted_at.isoformat(),
            "submitted_at": art.submitted_at.isoformat(),
        })
    
    # Aggregate stats
    all_preds = db.query(Prediction).all()
    stats = {
        "total_analyzed": len(all_preds),
        "fake_count": sum(1 for p in all_preds if p.label == "FAKE"),
        "real_count": sum(1 for p in all_preds if p.label == "REAL"),
        "uncertain_count": sum(1 for p in all_preds if p.label == "UNCERTAIN"),
        "pending_review": sum(1 for p in all_preds if p.review_status == "pending"),
        "confirmed": sum(1 for p in all_preds if p.review_status == "confirmed"),
        "dismissed": sum(1 for p in all_preds if p.review_status == "dismissed"),
        "relabeled": sum(1 for p in all_preds if p.review_status == "relabeled"),
    }
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "stats": stats,
    }


@router.get("/predictions/{prediction_id}")
async def get_prediction_detail(prediction_id: int, db: Session = Depends(get_db)):
    """Get detailed view of a single prediction."""
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    article = db.query(Article).filter(Article.id == pred.article_id).first()
    feedbacks = db.query(Feedback).filter(Feedback.prediction_id == prediction_id).all()
    
    return {
        "prediction": {
            "id": pred.id,
            "label": pred.label,
            "confidence": pred.confidence,
            "fake_probability": pred.fake_probability,
            "real_probability": pred.real_probability,
            "sentiment_score": pred.sentiment_score,
            "subjectivity_score": pred.subjectivity_score,
            "readability_score": pred.readability_score,
            "source_credibility_score": pred.source_credibility_score,
            "top_features": pred.top_features,
            "linguistic_features": pred.linguistic_features,
            "review_status": pred.review_status,
            "reviewer_label": pred.reviewer_label,
            "reviewer_note": pred.reviewer_note,
            "reviewed_at": pred.reviewed_at.isoformat() if pred.reviewed_at else None,
            "predicted_at": pred.predicted_at.isoformat(),
            "model_version": pred.model_version,
        },
        "article": {
            "id": article.id,
            "title": article.title,
            "text": article.text,
            "source": article.source,
            "author": article.author,
            "url": article.url,
            "dataset_label": article.dataset_label,
        },
        "feedback_history": [
            {
                "id": f.id,
                "action": f.action,
                "original_label": f.original_label,
                "assigned_label": f.assigned_label,
                "note": f.note,
                "reviewer": f.reviewer,
                "created_at": f.created_at.isoformat(),
            }
            for f in feedbacks
        ],
    }


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit human reviewer feedback on a prediction."""
    pred = db.query(Prediction).filter(Prediction.id == request.prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Store feedback (never overwrites original prediction)
    feedback = Feedback(
        prediction_id=pred.id,
        action=request.action,
        original_label=pred.label,
        assigned_label=request.assigned_label if request.action == "relabel" else None,
        note=request.note,
        reviewer=request.reviewer or "human_reviewer",
    )
    db.add(feedback)
    
    # Update review status on prediction
    pred.review_status = {
        "confirm": "confirmed",
        "dismiss": "dismissed",
        "relabel": "relabeled",
    }.get(request.action, "pending")
    
    if request.action == "relabel" and request.assigned_label:
        pred.reviewer_label = request.assigned_label
    
    pred.reviewer_note = request.note
    pred.reviewed_at = datetime.utcnow()
    pred.reviewed_by = request.reviewer
    
    db.commit()
    db.refresh(feedback)
    
    return {
        "success": True,
        "feedback_id": feedback.id,
        "message": f"Feedback recorded: {request.action} on prediction {request.prediction_id}",
    }


@router.post("/batch/analyze")
async def batch_analyze(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze a CSV file containing multiple articles."""
    import io
    import pandas as pd
    
    batch_id = str(uuid.uuid4())[:8]
    
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
    
    # Detect column names flexibly
    text_col = next((c for c in df.columns if c.lower() in ["text", "content", "body", "article"]), None)
    if not text_col:
        raise HTTPException(status_code=400, detail="CSV must have a 'text' or 'content' column")
    
    title_col = next((c for c in df.columns if c.lower() in ["title", "headline"]), None)
    source_col = next((c for c in df.columns if c.lower() in ["source", "publisher", "domain"]), None)
    author_col = next((c for c in df.columns if c.lower() in ["author", "writer"]), None)
    label_col = next((c for c in df.columns if c.lower() in ["label", "class", "type", "fake"]), None)
    
    # Create batch job record
    batch_job = BatchJob(
        batch_id=batch_id,
        filename=file.filename,
        total_items=len(df),
        status="processing",
    )
    db.add(batch_job)
    db.commit()
    
    results = []
    fake_count = real_count = uncertain_count = 0
    
    for idx, row in df.iterrows():
        text = str(row[text_col])
        if not text or text == "nan":
            continue
        
        source = str(row[source_col]) if source_col and source_col in row else None
        author = str(row[author_col]) if author_col and author_col in row else None
        title = str(row[title_col]) if title_col and title_col in row else None
        dataset_label = str(row[label_col]) if label_col and label_col in row else None
        
        # Store article
        article = Article(
            title=title,
            text=text,
            source=source,
            author=author,
            dataset_label=dataset_label,
            batch_id=batch_id,
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        
        # Predict
        result = ml_model.predict(text, source=source or "")
        features = result["features"]
        top_feats = get_top_features(features, n=5)
        
        prediction = Prediction(
            article_id=article.id,
            label=result["label"],
            confidence=result["confidence"],
            fake_probability=result["fake_probability"],
            real_probability=result["real_probability"],
            sentiment_score=features.get("vader_compound"),
            subjectivity_score=features.get("textblob_subjectivity"),
            readability_score=features.get("flesch_reading_ease"),
            source_credibility_score=get_seed_credibility(source),
            linguistic_features={k: round(float(v), 4) for k, v in features.items()},
            top_features=top_feats,
            model_version=result["model_version"],
        )
        db.add(prediction)
        db.commit()
        
        if result["label"] == "FAKE":
            fake_count += 1
        elif result["label"] == "REAL":
            real_count += 1
        else:
            uncertain_count += 1
        
        results.append({
            "row": idx,
            "prediction_id": prediction.id,
            "label": result["label"],
            "confidence": result["confidence"],
        })
    
    # Update batch job
    batch_job.processed_items = len(results)
    batch_job.fake_count = fake_count
    batch_job.real_count = real_count
    batch_job.uncertain_count = uncertain_count
    batch_job.status = "completed"
    batch_job.completed_at = datetime.utcnow()
    db.commit()
    
    return {
        "batch_id": batch_id,
        "total_processed": len(results),
        "fake_count": fake_count,
        "real_count": real_count,
        "uncertain_count": uncertain_count,
        "status": "completed",
        "results": results[:50],  # Return first 50
    }


@router.get("/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Get all tracked source credibility profiles."""
    sources = get_all_sources(db)
    return [
        {
            "source_name": s.source_name,
            "total_articles": s.total_articles,
            "fake_count": s.fake_count,
            "real_count": s.real_count,
            "credibility_score": round(s.credibility_score, 4),
            "last_updated": s.last_updated.isoformat() if s.last_updated else None,
        }
        for s in sources
    ]


@router.post("/train")
async def trigger_training(db: Session = Depends(get_db)):
    """Train/retrain model on stored data + sample dataset."""
    from app.core.data_loader import load_sample_data
    
    texts, labels, sources = load_sample_data()
    
    if len(texts) < 10:
        raise HTTPException(status_code=400, detail="Not enough training data")
    
    # Also include feedback-corrected labels from DB
    feedbacks = db.query(Feedback).filter(Feedback.action == "relabel").all()
    for fb in feedbacks:
        pred = db.query(Prediction).filter(Prediction.id == fb.prediction_id).first()
        if pred:
            art = db.query(Article).filter(Article.id == pred.article_id).first()
            if art:
                texts.append(art.text)
                labels.append(1 if fb.assigned_label == "FAKE" else 0)
                sources.append(art.source or "")
    
    ml_model.train_model(texts, labels, sources)
    
    # Evaluate
    from sklearn.model_selection import train_test_split
    _, test_texts, _, test_labels, _, test_sources = train_test_split(
        texts, labels, sources, test_size=0.2, random_state=42, stratify=labels
    )
    metrics = ml_model.evaluate_model(test_texts, test_labels, test_sources)
    
    return {
        "success": True,
        "message": "Model trained successfully",
        "training_samples": len(texts),
        "metrics": metrics,
    }


@router.get("/metrics")
async def get_metrics():
    """Return last evaluation metrics."""
    metrics = ml_model.get_saved_metrics()
    return metrics or {"message": "No metrics available. Train the model first."}


@router.get("/batch/jobs")
async def get_batch_jobs(db: Session = Depends(get_db)):
    """List all batch jobs."""
    jobs = db.query(BatchJob).order_by(BatchJob.created_at.desc()).limit(20).all()
    return [
        {
            "batch_id": j.batch_id,
            "filename": j.filename,
            "total_items": j.total_items,
            "processed_items": j.processed_items,
            "fake_count": j.fake_count,
            "real_count": j.real_count,
            "uncertain_count": j.uncertain_count,
            "status": j.status,
            "created_at": j.created_at.isoformat(),
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.get("/export/csv")
async def export_csv(
    batch_id: Optional[str] = None,
    label: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export analysis results as CSV."""
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    query = db.query(Prediction, Article).join(Article, Prediction.article_id == Article.id)
    if batch_id:
        query = query.filter(Article.batch_id == batch_id)
    if label:
        query = query.filter(Prediction.label == label.upper())
    
    results = query.limit(1000).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "prediction_id", "article_id", "title", "source", "author",
        "label", "confidence", "fake_probability", "real_probability",
        "review_status", "reviewer_label", "predicted_at", "text_preview"
    ])
    
    for pred, art in results:
        writer.writerow([
            pred.id, art.id, art.title or "", art.source or "", art.author or "",
            pred.label, pred.confidence, pred.fake_probability, pred.real_probability,
            pred.review_status, pred.reviewer_label or "",
            pred.predicted_at.isoformat(),
            art.text[:200].replace("\n", " ")
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.read().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=analysis_results.csv"}
    )
