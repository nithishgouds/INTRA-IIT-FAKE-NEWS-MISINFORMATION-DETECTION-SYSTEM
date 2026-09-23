"""
ML Classification Model for Fake News Detection
Uses TF-IDF + Logistic Regression ensemble with handcrafted features.
Includes training, inference, and persistence.
"""
import os
import json
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple, List
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix
)
from sklearn.base import BaseEstimator, TransformerMixin

from app.core.preprocessor import clean_text
from app.core.feature_extractor import (
    extract_all_features, features_to_array, FEATURE_NAMES
)

MODEL_PATH = Path(__file__).parent.parent.parent / "models"
MODEL_FILE = MODEL_PATH / "fake_news_model.joblib"
VECTORIZER_FILE = MODEL_PATH / "tfidf_vectorizer.joblib"
METRICS_FILE = MODEL_PATH / "metrics.json"

MODEL_VERSION = "v1.0"


class HandcraftedFeatureTransformer(BaseEstimator, TransformerMixin):
    """Transformer that extracts handcrafted features from text."""
    
    def __init__(self, source_credibilities=None):
        self.source_credibilities = source_credibilities or {}
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        results = []
        for item in X:
            if isinstance(item, dict):
                text = item.get("text", "")
                source = item.get("source", "")
                cred = self.source_credibilities.get(source, 0.5)
            else:
                text = str(item)
                cred = 0.5
            feats = extract_all_features(text, source_credibility=cred)
            results.append(features_to_array(feats))
        return np.array(results)


# Global model cache
_model = None
_vectorizer = None
_is_trained = False


def _get_model_path():
    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    return MODEL_FILE


def load_model():
    """Load trained model from disk."""
    global _model, _vectorizer, _is_trained
    if MODEL_FILE.exists() and VECTORIZER_FILE.exists():
        _model = joblib.load(MODEL_FILE)
        _vectorizer = joblib.load(VECTORIZER_FILE)
        _is_trained = True
        return True
    return False


def is_trained() -> bool:
    global _is_trained
    if _is_trained:
        return True
    return load_model()


def train_model(texts: List[str], labels: List[int], sources: List[str] = None):
    """
    Train the fake news detection model.
    labels: 0 = REAL, 1 = FAKE
    """
    global _model, _vectorizer, _is_trained
    
    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    sources = sources or [""] * len(texts)
    
    # Clean texts
    cleaned = [clean_text(t, remove_stopwords=True, lemmatize=True) for t in texts]
    
    # Build source credibility map from training labels
    from collections import defaultdict
    source_stats = defaultdict(lambda: {"real": 0, "fake": 0})
    for s, l in zip(sources, labels):
        if s:
            if l == 0:
                source_stats[s]["real"] += 1
            else:
                source_stats[s]["fake"] += 1
    
    source_cred = {}
    for s, stats in source_stats.items():
        total = stats["real"] + stats["fake"]
        alpha = 2
        source_cred[s] = (stats["real"] + alpha) / (total + 2 * alpha)
    
    # TF-IDF vectorizer
    _vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        strip_accents="unicode",
        analyzer="word",
    )
    tfidf_features = _vectorizer.fit_transform(cleaned).toarray()
    
    # Handcrafted features
    items = [{"text": t, "source": s} for t, s in zip(texts, sources)]
    hc_transformer = HandcraftedFeatureTransformer(source_credibilities=source_cred)
    hc_features = hc_transformer.transform(items)
    
    # Combine features
    X = np.hstack([tfidf_features, hc_features])
    y = np.array(labels)
    
    # Scale handcrafted features part (TF-IDF is already normalized)
    scaler = StandardScaler()
    X[:, -len(FEATURE_NAMES):] = scaler.fit_transform(X[:, -len(FEATURE_NAMES):])
    
    # Train Logistic Regression with calibration
    lr = LogisticRegression(
        C=1.0, max_iter=1000, solver="lbfgs",
        class_weight="balanced", random_state=42
    )
    lr.fit(X, y)
    
    # Store metadata on model object for inference
    lr.source_cred_ = source_cred
    lr.scaler_ = scaler
    lr.n_tfidf_features_ = tfidf_features.shape[1]
    lr.feature_names_ = list(_vectorizer.get_feature_names_out()) + FEATURE_NAMES
    
    _model = lr
    _is_trained = True
    
    # Save
    joblib.dump(_model, MODEL_FILE)
    joblib.dump(_vectorizer, VECTORIZER_FILE)
    
    return _model


def _prepare_features(text: str, source: str = ""):
    """Prepare combined feature vector for a single text."""
    cleaned = clean_text(text, remove_stopwords=True, lemmatize=True)
    tfidf_vec = _vectorizer.transform([cleaned]).toarray()
    
    cred = _model.source_cred_.get(source, 0.5)
    feats = extract_all_features(text, source_credibility=cred)
    hc_vec = features_to_array(feats).reshape(1, -1)
    
    hc_scaled = _model.scaler_.transform(hc_vec)
    X = np.hstack([tfidf_vec, hc_scaled])
    return X, feats


def predict(text: str, source: str = "") -> Dict[str, Any]:
    """
    Run inference on a single article.
    Returns label, confidence, probabilities, and features.
    """
    if not is_trained():
        # Return a mock prediction if model not trained
        return _mock_predict(text, source)
    
    X, feats = _prepare_features(text, source)
    proba = _model.predict_proba(X)[0]
    fake_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
    real_prob = float(proba[0]) if len(proba) > 1 else 1.0 - float(proba[0])
    
    # Determine label
    if fake_prob >= 0.65:
        label = "FAKE"
    elif fake_prob <= 0.35:
        label = "REAL"
    else:
        label = "UNCERTAIN"
    
    confidence = max(fake_prob, real_prob)
    
    return {
        "label": label,
        "confidence": round(confidence, 4),
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4),
        "features": feats,
        "model_version": MODEL_VERSION,
    }


def _mock_predict(text: str, source: str = "") -> Dict[str, Any]:
    """Heuristic-based prediction when model is not trained."""
    from app.core.feature_extractor import extract_all_features
    from app.core.credibility import get_seed_credibility
    
    cred = get_seed_credibility(source)
    feats = extract_all_features(text, source_credibility=cred)
    
    # Simple heuristic scoring
    score = 0.5
    score -= feats.get("textblob_subjectivity", 0) * 0.15
    score -= feats.get("sensational_ratio", 0) * 2.0
    score += feats.get("source_credibility", 0.5) * 0.2
    score -= abs(feats.get("vader_compound", 0)) * 0.1
    score -= feats.get("uppercase_ratio", 0) * 0.5
    score = max(0.05, min(0.95, score))
    
    real_prob = score
    fake_prob = 1.0 - score
    
    if fake_prob >= 0.65:
        label = "FAKE"
    elif fake_prob <= 0.35:
        label = "REAL"
    else:
        label = "UNCERTAIN"
    
    return {
        "label": label,
        "confidence": round(max(fake_prob, real_prob), 4),
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4),
        "features": feats,
        "model_version": "heuristic-v1",
    }


def evaluate_model(texts: List[str], labels: List[int], sources: List[str] = None) -> Dict[str, Any]:
    """Evaluate model on a test set and return metrics."""
    sources = sources or [""] * len(texts)
    predictions = []
    fake_probs = []
    
    for text, source in zip(texts, sources):
        result = predict(text, source)
        label_int = 1 if result["label"] == "FAKE" else 0
        predictions.append(label_int)
        fake_probs.append(result["fake_probability"])
    
    y_true = np.array(labels)
    y_pred = np.array(predictions)
    y_prob = np.array(fake_probs)
    
    metrics = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "auc_roc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, target_names=["REAL", "FAKE"], output_dict=True
        ),
        "total_samples": len(labels),
        "fake_samples": int(sum(labels)),
        "real_samples": int(len(labels) - sum(labels)),
    }
    
    # Failure case analysis
    false_positives = [
        {"text": texts[i][:200], "true": "REAL", "predicted": "FAKE", "confidence": round(fake_probs[i], 3)}
        for i in range(len(labels)) if labels[i] == 0 and predictions[i] == 1
    ][:5]
    
    false_negatives = [
        {"text": texts[i][:200], "true": "FAKE", "predicted": "REAL", "confidence": round(fake_probs[i], 3)}
        for i in range(len(labels)) if labels[i] == 1 and predictions[i] == 0
    ][:5]
    
    metrics["false_positives_sample"] = false_positives
    metrics["false_negatives_sample"] = false_negatives
    
    # Save metrics
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics


def get_saved_metrics() -> Dict[str, Any]:
    """Return last saved evaluation metrics."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {}
