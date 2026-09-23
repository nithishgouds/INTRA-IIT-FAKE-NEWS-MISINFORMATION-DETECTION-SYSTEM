"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Request Models ───────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Article or post text to analyze")
    title: Optional[str] = Field(None, description="Article title")
    url: Optional[str] = Field(None, description="Source URL")
    source: Optional[str] = Field(None, description="Source/publisher name")
    author: Optional[str] = Field(None, description="Author name")


class FeedbackRequest(BaseModel):
    prediction_id: int
    action: str = Field(..., pattern="^(confirm|dismiss|relabel)$")
    assigned_label: Optional[str] = Field(None, description="Relabeled value: FAKE|REAL|UNCERTAIN")
    note: Optional[str] = Field(None, description="Reviewer note")
    reviewer: Optional[str] = Field("human_reviewer", description="Reviewer identifier")


class TrainRequest(BaseModel):
    dataset_name: Optional[str] = Field("sample", description="Dataset to train on")
    test_size: Optional[float] = Field(0.2, description="Fraction for test set")


# ─── Response Models ──────────────────────────────────────────────────────────

class FeatureInfo(BaseModel):
    feature: str
    display_name: str
    value: float
    impact: Optional[float] = None
    impact_direction: Optional[str] = None
    description: Optional[str] = None


class TextHighlight(BaseModel):
    start: int
    end: int
    text: str
    type: str
    label: str
    color: str


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    id: int
    article_id: int
    label: str
    confidence: float
    fake_probability: float
    real_probability: float
    sentiment_score: Optional[float]
    subjectivity_score: Optional[float]
    readability_score: Optional[float]
    source_credibility_score: Optional[float]
    top_features: Optional[List[Dict[str, Any]]]
    text_highlights: Optional[List[Dict[str, Any]]]
    review_status: str
    reviewer_label: Optional[str]
    reviewer_note: Optional[str]
    reviewed_at: Optional[datetime]
    predicted_at: datetime
    model_version: str


class ArticleResponse(BaseModel):
    id: int
    title: Optional[str]
    text: str
    url: Optional[str]
    source: Optional[str]
    author: Optional[str]
    submitted_at: datetime
    dataset_label: Optional[str]
    predictions: Optional[List[PredictionResponse]] = []

    class Config:
        from_attributes = True


class AnalyzeResponse(BaseModel):
    article: Dict[str, Any]
    prediction: Dict[str, Any]
    explanation: Dict[str, Any]
    highlights: List[Dict[str, Any]]


class FeedbackResponse(BaseModel):
    success: bool
    feedback_id: int
    message: str


class DashboardItem(BaseModel):
    prediction_id: int
    article_id: int
    title: Optional[str]
    text_preview: str
    source: Optional[str]
    author: Optional[str]
    label: str
    confidence: float
    fake_probability: float
    review_status: str
    reviewer_label: Optional[str]
    predicted_at: datetime
    submitted_at: datetime


class DashboardResponse(BaseModel):
    items: List[DashboardItem]
    total: int
    page: int
    page_size: int
    stats: Dict[str, Any]


class MetricsResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    accuracy: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    auc_roc: Optional[float]
    confusion_matrix: Optional[List[List[int]]]
    total_samples: Optional[int]
    fake_samples: Optional[int]
    real_samples: Optional[int]
    false_positives_sample: Optional[List[Dict[str, Any]]]
    false_negatives_sample: Optional[List[Dict[str, Any]]]


class SourceCredibilityResponse(BaseModel):
    source_name: str
    total_articles: int
    fake_count: int
    real_count: int
    credibility_score: float
    last_updated: Optional[datetime]


class BatchJobResponse(BaseModel):
    batch_id: str
    status: str
    total_items: int
    processed_items: int
    fake_count: int
    real_count: int
    uncertain_count: int
    created_at: datetime
    completed_at: Optional[datetime]
