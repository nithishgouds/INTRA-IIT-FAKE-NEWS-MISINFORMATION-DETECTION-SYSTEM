"""
Explainability Layer using SHAP for Fake News Detection
Generates feature importance explanations for each prediction.
"""
import numpy as np
from typing import Dict, List, Any

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

try:
    from lime.lime_text import LimeTextExplainer
    HAS_LIME = True
except ImportError:
    HAS_LIME = False

from app.core.feature_extractor import FEATURE_NAMES, extract_all_features, features_to_array
from app.core.preprocessor import clean_text


FEATURE_DISPLAY_NAMES = {
    "vader_compound": "Overall Sentiment (VADER)",
    "vader_pos": "Positive Sentiment",
    "vader_neg": "Negative Sentiment",
    "vader_neu": "Neutral Sentiment",
    "textblob_polarity": "Text Polarity (TextBlob)",
    "textblob_subjectivity": "Subjectivity Score",
    "flesch_reading_ease": "Readability (Flesch)",
    "flesch_kincaid_grade": "Grade Level",
    "gunning_fog": "Gunning Fog Index",
    "smog_index": "SMOG Readability",
    "automated_readability_index": "Auto Readability Index",
    "coleman_liau_index": "Coleman-Liau Index",
    "word_count": "Word Count",
    "sentence_count": "Sentence Count",
    "avg_word_length": "Average Word Length",
    "punct_count": "Punctuation Count",
    "uppercase_word_count": "ALL CAPS Words",
    "uppercase_ratio": "CAPS Ratio",
    "exclamation_count": "Exclamation Marks",
    "question_count": "Question Marks",
    "stopword_ratio": "Stopword Ratio",
    "unique_word_ratio": "Vocabulary Diversity",
    "sensational_word_count": "Sensational Words",
    "sensational_ratio": "Sensational Language Ratio",
    "hedge_word_count": "Hedge Words (uncertainty)",
    "strong_modal_count": "Strong Assertions",
    "has_url": "Contains URLs",
    "numeric_count": "Numbers/Statistics",
    "source_credibility": "Source Credibility Score",
}

FEATURE_DESCRIPTIONS = {
    "textblob_subjectivity": "Higher subjectivity suggests opinion-based writing, common in misinformation",
    "sensational_ratio": "Sensational language (shocking, bombshell, etc.) is a red flag for fake news",
    "uppercase_ratio": "Excessive capitalization is a stylistic marker of misinformation",
    "exclamation_count": "High exclamation marks suggest emotional manipulation",
    "vader_compound": "Extreme sentiment (very positive or very negative) correlates with fake news",
    "source_credibility": "Historical credibility of the publishing source",
    "unique_word_ratio": "Low vocabulary diversity may indicate template-based misinformation",
    "hedge_word_count": "Use of hedging language without sources suggests unverified claims",
    "strong_modal_count": "Overconfident assertions without evidence are a fake news pattern",
}


def get_top_features(features: Dict[str, float], n: int = 10) -> List[Dict[str, Any]]:
    """
    Return top N most informative features with their values and impact direction.
    Uses rule-based scoring when SHAP is unavailable.
    """
    # Fake news indicator weights (positive = suggests fake, negative = suggests real)
    FAKE_WEIGHTS = {
        "textblob_subjectivity": 0.8,
        "sensational_ratio": 1.5,
        "uppercase_ratio": 1.2,
        "exclamation_count": 0.6,
        "strong_modal_count": 0.5,
        "hedge_word_count": 0.4,
        "vader_neg": 0.4,
        "source_credibility": -1.5,   # Higher credibility = less fake
        "unique_word_ratio": -0.5,    # Higher diversity = less fake
        "flesch_reading_ease": -0.2,  # Easier reading = slightly more fake
        "sensational_word_count": 1.0,
        "has_url": -0.3,
    }
    
    scored = []
    for feat_name, weight in FAKE_WEIGHTS.items():
        value = features.get(feat_name, 0.0)
        impact = float(value * weight)
        scored.append({
            "feature": feat_name,
            "display_name": FEATURE_DISPLAY_NAMES.get(feat_name, feat_name),
            "value": round(float(value), 4),
            "impact": round(impact, 4),
            "impact_direction": "fake" if impact > 0 else "real",
            "description": FEATURE_DESCRIPTIONS.get(feat_name, ""),
        })
    
    # Sort by absolute impact
    scored.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return scored[:n]


def explain_with_shap(model, vectorizer, text: str, source: str = "") -> Dict[str, Any]:
    """
    Generate SHAP explanation for a prediction.
    Falls back to feature-based explanation if SHAP fails.
    """
    from app.core.feature_extractor import extract_all_features
    from app.core.credibility import get_seed_credibility
    
    cred = getattr(model, "source_cred_", {}).get(source, get_seed_credibility(source))
    features = extract_all_features(text, source_credibility=cred)
    top_features = get_top_features(features)
    
    if not HAS_SHAP or not hasattr(model, "source_cred_"):
        return {
            "method": "feature_weights",
            "top_features": top_features,
            "shap_values": None,
        }
    
    try:
        cleaned = clean_text(text, remove_stopwords=True, lemmatize=True)
        tfidf_vec = vectorizer.transform([cleaned]).toarray()
        
        from app.core.feature_extractor import features_to_array
        hc_vec = features_to_array(features).reshape(1, -1)
        hc_scaled = model.scaler_.transform(hc_vec)
        X = np.hstack([tfidf_vec, hc_scaled])
        
        # Use linear SHAP explainer for logistic regression
        explainer = shap.LinearExplainer(model, X, feature_perturbation="correlation_dependent")
        shap_vals = explainer.shap_values(X)[0]  # For FAKE class
        
        feature_names = model.feature_names_
        # Get top SHAP features (from handcrafted features section)
        n_tfidf = model.n_tfidf_features_
        hc_shap = shap_vals[n_tfidf:]
        
        shap_features = []
        for i, fname in enumerate(FEATURE_NAMES):
            sv = float(hc_shap[i]) if i < len(hc_shap) else 0.0
            shap_features.append({
                "feature": fname,
                "display_name": FEATURE_DISPLAY_NAMES.get(fname, fname),
                "value": round(features.get(fname, 0.0), 4),
                "shap_value": round(sv, 4),
                "impact_direction": "fake" if sv > 0 else "real",
                "description": FEATURE_DESCRIPTIONS.get(fname, ""),
            })
        
        shap_features.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "method": "shap",
            "top_features": shap_features[:10],
            "shap_values": [round(float(v), 5) for v in hc_shap[:20]],
        }
    except Exception as e:
        return {
            "method": "feature_weights",
            "top_features": top_features,
            "shap_values": None,
            "error": str(e),
        }


def highlight_suspicious_text(text: str, features: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Identify suspicious text segments (sensational words, CAPS, excessive punctuation).
    Returns list of highlighted spans for the UI.
    """
    import re
    from app.core.feature_extractor import SENSATIONAL_WORDS, HEDGE_WORDS, STRONG_MODAL_WORDS
    
    highlights = []
    text_lower = text.lower()
    
    # Sensational words
    for word in SENSATIONAL_WORDS:
        for match in re.finditer(re.escape(word), text_lower):
            highlights.append({
                "start": match.start(),
                "end": match.end(),
                "text": text[match.start():match.end()],
                "type": "sensational",
                "label": "Sensational Language",
                "color": "#ef4444",
            })
    
    # Hedge words
    for word in HEDGE_WORDS:
        for match in re.finditer(re.escape(word), text_lower):
            highlights.append({
                "start": match.start(),
                "end": match.end(),
                "text": text[match.start():match.end()],
                "type": "hedge",
                "label": "Unverified Claim",
                "color": "#f59e0b",
            })
    
    # ALL CAPS words
    for match in re.finditer(r"\b[A-Z]{3,}\b", text):
        highlights.append({
            "start": match.start(),
            "end": match.end(),
            "text": match.group(),
            "type": "caps",
            "label": "Excessive Capitalization",
            "color": "#8b5cf6",
        })
    
    # Sort by position and deduplicate
    highlights.sort(key=lambda x: x["start"])
    return highlights[:20]  # Limit to 20 highlights
