"""
Explainability Layer using SHAP and Linguistic Feature Attribution
Generates transparent, human-interpretable explanations for model predictions.
"""
import re
import numpy as np
from typing import Dict, List, Any, Optional

try:
    import shap
    HAS_SHAP = True
except Exception:
    HAS_SHAP = False

from app.core.feature_extractor import (
    FEATURE_NAMES,
    extract_all_features,
    features_to_array,
    SENSATIONAL_WORDS,
    HEDGE_WORDS,
)
from app.core.preprocessor import clean_text


FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    "vader_compound": "Overall Sentiment (VADER)",
    "vader_pos": "Positive Sentiment",
    "vader_neg": "Negative Sentiment",
    "vader_neu": "Neutral Sentiment",
    "textblob_polarity": "Text Polarity (TextBlob)",
    "textblob_subjectivity": "Subjectivity Score",
    "flesch_reading_ease": "Readability Ease (Flesch)",
    "avg_word_length": "Average Word Length",
    "punct_density": "Punctuation Density",
    "uppercase_ratio": "Capitalization Ratio",
    "exclamation_density": "Exclamation Mark Density",
    "stopword_ratio": "Functional Stopword Ratio",
    "unique_word_ratio": "Vocabulary Diversity",
    "sensational_ratio": "Sensational Language Ratio",
    "hedge_ratio": "Unverified / Hedge Ratio",
    "numeric_density": "Numerical Data Density",
    # Preserved for display
    "word_count": "Word Count",
    "sentence_count": "Sentence Count",
    "punct_count": "Punctuation Count",
    "exclamation_count": "Exclamation Marks",
    "uppercase_word_count": "ALL CAPS Words",
    "numeric_count": "Numbers/Statistics",
    "source_credibility": "Source Credibility Score",
}

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "textblob_subjectivity": "Higher subjectivity indicates opinion/emotion rather than factual reporting.",
    "sensational_ratio": "Sensational vocabulary (e.g., 'shocking', 'bombshell') is a strong indicator of clickbait or fake news.",
    "uppercase_ratio": "Frequent capitalized words reflect urgency/sensationalism.",
    "exclamation_density": "Excessive exclamation marks suggest emotional appeal rather than objective journalism.",
    "vader_compound": "Polarized sentiment often accompanies propaganda or emotionally charged misinformation.",
    "hedge_ratio": "Unattributed hedge phrases ('sources claim', 'allegedly') without citations denote unverified claims.",
    "unique_word_ratio": "Lower vocabulary diversity can indicate repetitive or templated writing.",
    "numeric_density": "Density of specific numbers and statistics. Factual reporting frequently cites verifiable quantitative data.",
    "punct_density": "High punctuation density often correlates with dramatic or informal styling.",
    "avg_word_length": "Shorter average word length can correlate with informal or simplistic copy.",
    "flesch_reading_ease": "Readability score compared to standard journalistic writing.",
}


def get_feature_contextual_description(feature_name: str, impact_direction: str, raw_value: float = 0.0) -> str:
    """
    Return human-interpretable description that is conceptually and mathematically
    consistent with the actual contribution direction toward Credible or Misinformation.
    """
    if impact_direction == "fake":
        descriptions = {
            "hedge_ratio": "Presence of unattributed hedge phrases ('sources claim', 'allegedly') denotes unverified claims.",
            "sensational_ratio": "Presence of sensational vocabulary (e.g., 'shocking', 'secret') indicates clickbait or unverified claims.",
            "uppercase_ratio": "Excessive capitalized words reflect urgency, shouting, or sensational framing.",
            "exclamation_density": "Excessive exclamation marks suggest dramatic emotional appeal over objective journalism.",
            "textblob_subjectivity": "Elevated subjectivity reflects opinionated or emotional wording over factual reporting.",
            "vader_compound": "Polarized emotional sentiment aligns with emotionally charged or sensational claims.",
            "textblob_polarity": "Polarized polarity score reflects opinionated or biased narrative framing.",
            "vader_neg": "Elevated negative sentiment contributes toward alarmist or fear-based framing.",
            "vader_pos": "Heightened positive sentiment reflects promotional or exaggerated assertions.",
            "vader_neu": "Neutral score distribution aligned with misinformation patterns.",
            "numeric_density": "Low density of verifiable quantitative metrics or statistics.",
            "unique_word_ratio": "Repetitive phrasing or lower vocabulary diversity.",
            "punct_density": "High punctuation density correlates with dramatic styling.",
            "avg_word_length": "Shorter average word length correlates with informal copy.",
            "stopword_ratio": "Unusual functional word distribution.",
            "flesch_reading_ease": "Informal readability score aligns with unverified claims.",
        }
        return descriptions.get(feature_name, FEATURE_DESCRIPTIONS.get(feature_name, ""))
    else:
        descriptions = {
            "hedge_ratio": "Absence or low level of speculative hedge phrases supports factual credibility.",
            "sensational_ratio": "Absence of sensational clickbait vocabulary supports objective credibility.",
            "uppercase_ratio": "Standard capitalization without excessive shouting supports professional reporting.",
            "exclamation_density": "Absence of dramatic exclamation marks indicates objective journalistic tone.",
            "textblob_subjectivity": "Low subjectivity and objective tone support factual reporting.",
            "vader_compound": "Balanced, non-alarmist sentiment supports credible reporting.",
            "textblob_polarity": "Measured, objective polarity supports credible reporting.",
            "vader_neu": "Predominantly neutral, objective tone supports journalistic credibility.",
            "vader_pos": "Constructive, measured factual tone supports credibility.",
            "vader_neg": "Absence of alarmist negative framing supports credibility.",
            "numeric_density": "Inclusion of specific quantitative data and statistics supports verifiable reporting.",
            "unique_word_ratio": "Rich, diverse vocabulary aligns with comprehensive professional reporting.",
            "punct_density": "Clean, standard punctuation supports professional formatting.",
            "avg_word_length": "Standard journalistic word length and vocabulary structure.",
            "stopword_ratio": "Standard natural language sentence structure.",
            "flesch_reading_ease": "Standard journalistic readability level.",
        }
        return descriptions.get(feature_name, FEATURE_DESCRIPTIONS.get(feature_name, ""))


def get_top_features(features: Dict[str, float], n: int = 10) -> List[Dict[str, Any]]:
    """
    Return top N most informative length-invariant features with their calculated impact and direction.
    """
    fake_weights = {
        "sensational_ratio": 2.5,
        "uppercase_ratio": 1.5,
        "textblob_subjectivity": 1.0,
        "exclamation_density": 1.2,
        "hedge_ratio": 1.2,
        "punct_density": 0.4,
        "vader_neg": 0.4,
        "numeric_density": -1.0,
        "unique_word_ratio": -0.6,
        "flesch_reading_ease": -0.2,
    }

    scored = []
    for feat_name, weight in fake_weights.items():
        value = float(features.get(feat_name, 0.0))
        impact = float(value * weight)
        dir_str = "fake" if impact > 0 else "real"
        scored.append({
            "feature": feat_name,
            "display_name": FEATURE_DISPLAY_NAMES.get(feat_name, feat_name),
            "value": round(value, 4),
            "impact": round(impact, 4),
            "shap_value": round(impact, 4),
            "impact_direction": dir_str,
            "description": get_feature_contextual_description(feat_name, dir_str, value),
        })

    scored.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return scored[:n]


def explain_with_shap(model: Any, vectorizer: Any, text: str, source: str = "", source_credibility: Optional[float] = None) -> Dict[str, Any]:
    """
    Generate SHAP-based feature importance for a prediction.
    Gracefully falls back to heuristic feature attribution if SHAP is unavailable.
    """
    from app.core.credibility import get_seed_credibility

    if source_credibility is not None:
        cred = source_credibility
    else:
        cred = getattr(model, "source_cred_", {}).get(source, get_seed_credibility(source)) if model else get_seed_credibility(source)

    features = extract_all_features(text, source_credibility=cred)
    fallback_features = get_top_features(features, n=10)

    if model is None or vectorizer is None or not hasattr(model, "scaler_"):
        return {
            "method": "feature_weights",
            "top_features": fallback_features,
            "shap_values": None,
        }

    try:
        cleaned = clean_text(text, remove_stopwords=True, lemmatize=True)
        tfidf_vec = vectorizer.transform([cleaned]).toarray()
        hc_vec = features_to_array(features).reshape(1, -1)
        hc_scaled = model.scaler_.transform(hc_vec)
        
        # Apply handcrafted feature weight scaling if stored on model
        hc_weight = getattr(model, "hc_weight_", 1.0)
        hc_weighted = hc_scaled * hc_weight
        X = np.hstack([tfidf_vec, hc_weighted])

        n_tfidf = getattr(model, "n_tfidf_features_", tfidf_vec.shape[1])
        hc_coefs = model.coef_[0, n_tfidf:] if hasattr(model, "coef_") else [0.0] * len(FEATURE_NAMES)
        hc_inputs = hc_weighted[0]

        shap_features = []
        for i, fname in enumerate(FEATURE_NAMES):
            coef = float(hc_coefs[i]) if i < len(hc_coefs) else 0.0
            val_scaled = float(hc_inputs[i]) if i < len(hc_inputs) else 0.0
            contrib = coef * val_scaled
            raw_val = float(features.get(fname, 0.0))
            dir_str = "fake" if contrib > 0 else "real"

            shap_features.append({
                "feature": fname,
                "display_name": FEATURE_DISPLAY_NAMES.get(fname, fname),
                "value": round(raw_val, 4),
                "impact": round(contrib, 4),
                "shap_value": round(contrib, 4),
                "impact_direction": dir_str,
                "description": get_feature_contextual_description(fname, dir_str, raw_val),
            })

        shap_features.sort(key=lambda x: abs(x["impact"]), reverse=True)

        return {
            "method": "shap",
            "top_features": shap_features[:10],
            "shap_values": [round(f["impact"], 5) for f in shap_features[:10]],
        }
    except Exception as exc:
        return {
            "method": "feature_weights",
            "top_features": fallback_features,
            "shap_values": None,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "method": "feature_weights",
            "top_features": fallback_features,
            "shap_values": None,
            "error": str(exc),
        }


def highlight_suspicious_text(text: str, features: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    """
    Identify non-overlapping suspicious text segments for highlighting in UI.
    """
    highlights: List[Dict[str, Any]] = []
    text_lower = text.lower()

    # 1. Sensational keywords
    for word in SENSATIONAL_WORDS:
        for match in re.finditer(r"\b" + re.escape(word) + r"\b", text_lower):
            highlights.append({
                "start": match.start(),
                "end": match.end(),
                "text": text[match.start():match.end()],
                "type": "sensational",
                "label": "Sensational Language",
                "color": "#ef4444",
            })

    # 2. Hedge words / Unverified claims
    for word in HEDGE_WORDS:
        for match in re.finditer(r"\b" + re.escape(word) + r"\b", text_lower):
            highlights.append({
                "start": match.start(),
                "end": match.end(),
                "text": text[match.start():match.end()],
                "type": "hedge",
                "label": "Unverified Claim",
                "color": "#f59e0b",
            })

    # 3. Excessive Capitalization (3+ uppercase letters in non-standard acronym words)
    STANDARD_ACRONYMS = {
        "ISRO", "NASA", "WHO", "CDC", "GSLV", "PSLV", "IIT", "USA", "UK",
        "AI", "ML", "COVID", "UN", "EU", "PM", "DRDO", "NOAA", "ESA",
        "MIT", "BBC", "CNN", "AFP", "GMT", "UTC", "EST", "IST", "UAV", "GDP", "NDTV"
    }
    for match in re.finditer(r"\b[A-Z]{3,}\b", text):
        word = match.group()
        if word not in STANDARD_ACRONYMS:
            highlights.append({
                "start": match.start(),
                "end": match.end(),
                "text": word,
                "type": "caps",
                "label": "Excessive Capitalization",
                "color": "#8b5cf6",
            })

    # Sort by starting index
    highlights.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

    # Deduplicate / merge overlapping spans
    filtered: List[Dict[str, Any]] = []
    last_end = -1
    for hl in highlights:
        if hl["start"] >= last_end:
            filtered.append(hl)
            last_end = hl["end"]

    return filtered[:25]
