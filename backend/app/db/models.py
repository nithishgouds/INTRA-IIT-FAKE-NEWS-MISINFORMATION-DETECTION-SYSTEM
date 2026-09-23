"""
Database models for Fake News Detection System
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=True)
    text = Column(Text, nullable=False)
    url = Column(String(1000), nullable=True)
    source = Column(String(200), nullable=True)
    author = Column(String(200), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    dataset_label = Column(String(50), nullable=True)   # Ground truth if from dataset
    batch_id = Column(String(100), nullable=True)       # For batch submissions

    predictions = relationship("Prediction", back_populates="article", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    label = Column(String(50), nullable=False)           # FAKE / REAL / UNCERTAIN
    confidence = Column(Float, nullable=False)
    fake_probability = Column(Float, nullable=False)
    real_probability = Column(Float, nullable=False)

    # Feature scores
    sentiment_score = Column(Float, nullable=True)
    subjectivity_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    source_credibility_score = Column(Float, nullable=True)
    linguistic_features = Column(JSON, nullable=True)

    # SHAP explanation
    shap_values = Column(JSON, nullable=True)
    top_features = Column(JSON, nullable=True)           # [{feature, value, impact}]

    predicted_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), default="v1.0")

    # Review status
    review_status = Column(String(50), default="pending")  # pending/confirmed/dismissed/relabeled
    reviewer_label = Column(String(50), nullable=True)
    reviewer_note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)

    article = relationship("Article", back_populates="predictions")
    feedback = relationship("Feedback", back_populates="prediction", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    action = Column(String(50), nullable=False)          # confirm / dismiss / relabel
    original_label = Column(String(50), nullable=False)
    assigned_label = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    reviewer = Column(String(100), default="human_reviewer")
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", back_populates="feedback")


class SourceCredibility(Base):
    __tablename__ = "source_credibility"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(200), unique=True, index=True, nullable=False)
    total_articles = Column(Integer, default=0)
    fake_count = Column(Integer, default=0)
    real_count = Column(Integer, default=0)
    credibility_score = Column(Float, default=0.5)       # 0=unreliable, 1=highly credible
    last_updated = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), unique=True, index=True)
    filename = Column(String(500), nullable=True)
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    fake_count = Column(Integer, default=0)
    real_count = Column(Integer, default=0)
    uncertain_count = Column(Integer, default=0)
    status = Column(String(50), default="processing")    # processing/completed/failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
