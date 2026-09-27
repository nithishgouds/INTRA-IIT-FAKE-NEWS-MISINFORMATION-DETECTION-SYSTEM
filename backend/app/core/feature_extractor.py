"""
Feature Engineering module for Fake News Detection System
Extracts length-invariant linguistic, sentiment, readability, and stylistic density features.
"""
import re
import numpy as np
from typing import Dict, Any

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

from app.core.preprocessor import (
    get_word_count, get_sentence_count, get_avg_word_length,
    count_punctuation, count_uppercase_words, count_exclamation,
    count_question_marks, get_stopword_ratio, get_unique_word_ratio
)

# Sensational / clickbait phrases
SENSATIONAL_WORDS = {
    "shocking", "unbelievable", "bombshell", "secret exposed", "mind-blowing",
    "you won't believe", "they don't want you to know", "wake up people",
    "must share", "miracle cure", "deep state", "crisis actor",
    "bizarre secret", "conspiracy exposed", "mainstream media coverup"
}

# Speculative hedge indicators
HEDGE_WORDS = {
    "allegedly", "reportedly", "unconfirmed", "unverified", "rumored",
    "supposedly", "purportedly", "anonymous sources", "sources claim",
    "unsubstantiated", "speculated"
}


def extract_sentiment_features(text: str) -> Dict[str, float]:
    """VADER sentiment + TextBlob polarity/subjectivity."""
    features = {
        "vader_compound": 0.0,
        "vader_pos": 0.0,
        "vader_neg": 0.0,
        "vader_neu": 0.0,
        "textblob_polarity": 0.0,
        "textblob_subjectivity": 0.0,
    }
    if HAS_VADER:
        scores = _vader.polarity_scores(text)
        features["vader_compound"] = scores["compound"]
        features["vader_pos"] = scores["pos"]
        features["vader_neg"] = scores["neg"]
        features["vader_neu"] = scores["neu"]
    if HAS_TEXTBLOB:
        blob = TextBlob(text)
        features["textblob_polarity"] = blob.sentiment.polarity
        features["textblob_subjectivity"] = blob.sentiment.subjectivity
    return features


def extract_readability_features(text: str) -> Dict[str, float]:
    """Readability scores via textstat."""
    features = {
        "flesch_reading_ease": 50.0,
    }
    if HAS_TEXTSTAT and text:
        try:
            features["flesch_reading_ease"] = float(textstat.flesch_reading_ease(text))
        except Exception:
            pass
    return features


def extract_stylistic_features(text: str) -> Dict[str, float]:
    """Length-normalized stylistic and density features."""
    words = text.split()
    word_count = max(len(words), 1)
    text_lower = text.lower()
    
    sensational_count = sum(
        1 for phrase in SENSATIONAL_WORDS
        if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower)
    )
    hedge_count = sum(
        1 for phrase in HEDGE_WORDS
        if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower)
    )
    punct_count = count_punctuation(text)
    excl_count = count_exclamation(text)
    uppercase_count = count_uppercase_words(text)
    numeric_count = len(re.findall(r"\b\d+\b", text))
    sentence_count = get_sentence_count(text)

    return {
        # Raw metrics (preserved for UI display / analytics)
        "word_count": word_count,
        "sentence_count": sentence_count,
        "punct_count": punct_count,
        "exclamation_count": excl_count,
        "uppercase_word_count": uppercase_count,
        "sensational_word_count": sensational_count,
        "hedge_word_count": hedge_count,
        "numeric_count": numeric_count,

        # Length-invariant density features (used for ML prediction)
        "avg_word_length": get_avg_word_length(text),
        "punct_density": punct_count / word_count,
        "uppercase_ratio": uppercase_count / word_count,
        "exclamation_density": excl_count / word_count,
        "stopword_ratio": get_stopword_ratio(text),
        "unique_word_ratio": get_unique_word_ratio(text),
        "sensational_ratio": sensational_count / word_count,
        "hedge_ratio": hedge_count / word_count,
        "numeric_density": numeric_count / word_count,
    }


def extract_all_features(text: str, source_credibility: float = 0.5) -> Dict[str, Any]:
    """Extract all features and return as flat dict."""
    sentiment = extract_sentiment_features(text)
    readability = extract_readability_features(text)
    stylistic = extract_stylistic_features(text)
    
    features = {
        **sentiment,
        **readability,
        **stylistic,
        "source_credibility": source_credibility,
    }
    return features


# Feature names used strictly in the ML model (length-invariant features only)
FEATURE_NAMES = [
    "vader_compound",
    "vader_pos",
    "vader_neg",
    "vader_neu",
    "textblob_polarity",
    "textblob_subjectivity",
    "flesch_reading_ease",
    "avg_word_length",
    "punct_density",
    "uppercase_ratio",
    "exclamation_density",
    "stopword_ratio",
    "unique_word_ratio",
    "sensational_ratio",
    "hedge_ratio",
    "numeric_density",
]


def features_to_array(features: Dict[str, float]) -> np.ndarray:
    """Convert length-invariant feature dict to numpy array for model input."""
    return np.array([float(features.get(k, 0.0)) for k in FEATURE_NAMES], dtype=np.float32)
