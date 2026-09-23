"""
Feature Engineering module for Fake News Detection System
Extracts linguistic, sentiment, readability, and stylistic features.
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

# Sensational / clickbait words often found in fake news
SENSATIONAL_WORDS = {
    "shocking", "unbelievable", "incredible", "secret", "exposed", "breaking",
    "urgent", "exclusive", "bombshell", "scandal", "outrage", "disgusting",
    "destroy", "conspiracy", "hoax", "fraud", "lies", "truth", "wake up",
    "share", "must see", "you won't believe", "they don't want you to know",
    "mainstream media", "deep state", "fake", "crisis actor"
}

HEDGE_WORDS = {
    "allegedly", "reportedly", "claimed", "said to", "sources say",
    "some say", "rumor", "unverified", "perhaps", "maybe", "possibly"
}

STRONG_MODAL_WORDS = {
    "definitely", "certainly", "absolutely", "undoubtedly", "clearly",
    "obviously", "everyone knows", "always", "never", "all", "none"
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
        "flesch_kincaid_grade": 8.0,
        "gunning_fog": 10.0,
        "smog_index": 8.0,
        "automated_readability_index": 8.0,
        "coleman_liau_index": 10.0,
    }
    if HAS_TEXTSTAT and text:
        try:
            features["flesch_reading_ease"] = textstat.flesch_reading_ease(text)
            features["flesch_kincaid_grade"] = textstat.flesch_kincaid_grade(text)
            features["gunning_fog"] = textstat.gunning_fog(text)
            features["smog_index"] = textstat.smog_index(text)
            features["automated_readability_index"] = textstat.automated_readability_index(text)
            features["coleman_liau_index"] = textstat.coleman_liau_index(text)
        except Exception:
            pass
    return features


def extract_stylistic_features(text: str) -> Dict[str, float]:
    """Stylistic markers: punctuation, caps, exclamations, etc."""
    words = text.split()
    word_count = max(len(words), 1)
    
    sensational_count = sum(
        1 for word in SENSATIONAL_WORDS
        if word.lower() in text.lower()
    )
    hedge_count = sum(
        1 for word in HEDGE_WORDS
        if word.lower() in text.lower()
    )
    strong_modal_count = sum(
        1 for word in STRONG_MODAL_WORDS
        if word.lower() in text.lower()
    )
    
    return {
        "word_count": word_count,
        "sentence_count": get_sentence_count(text),
        "avg_word_length": get_avg_word_length(text),
        "punct_count": count_punctuation(text),
        "uppercase_word_count": count_uppercase_words(text),
        "uppercase_ratio": count_uppercase_words(text) / word_count,
        "exclamation_count": count_exclamation(text),
        "question_count": count_question_marks(text),
        "stopword_ratio": get_stopword_ratio(text),
        "unique_word_ratio": get_unique_word_ratio(text),
        "sensational_word_count": sensational_count,
        "sensational_ratio": sensational_count / word_count,
        "hedge_word_count": hedge_count,
        "strong_modal_count": strong_modal_count,
        "has_url": 1 if re.search(r"http\S+|www\S+", text) else 0,
        "numeric_count": len(re.findall(r"\b\d+\b", text)),
    }


def extract_all_features(text: str, source_credibility: float = 0.5) -> Dict[str, Any]:
    """Extract all features and return as a flat dict."""
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


def features_to_array(features: Dict[str, float]) -> np.ndarray:
    """Convert feature dict to numpy array for model input."""
    # Fixed ordered list of feature keys for model compatibility
    FEATURE_KEYS = [
        "vader_compound", "vader_pos", "vader_neg", "vader_neu",
        "textblob_polarity", "textblob_subjectivity",
        "flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog",
        "smog_index", "automated_readability_index", "coleman_liau_index",
        "word_count", "sentence_count", "avg_word_length",
        "punct_count", "uppercase_word_count", "uppercase_ratio",
        "exclamation_count", "question_count",
        "stopword_ratio", "unique_word_ratio",
        "sensational_word_count", "sensational_ratio",
        "hedge_word_count", "strong_modal_count",
        "has_url", "numeric_count", "source_credibility",
    ]
    return np.array([features.get(k, 0.0) for k in FEATURE_KEYS], dtype=np.float32)


FEATURE_NAMES = [
    "vader_compound", "vader_pos", "vader_neg", "vader_neu",
    "textblob_polarity", "textblob_subjectivity",
    "flesch_reading_ease", "flesch_kincaid_grade", "gunning_fog",
    "smog_index", "automated_readability_index", "coleman_liau_index",
    "word_count", "sentence_count", "avg_word_length",
    "punct_count", "uppercase_word_count", "uppercase_ratio",
    "exclamation_count", "question_count",
    "stopword_ratio", "unique_word_ratio",
    "sensational_word_count", "sensational_ratio",
    "hedge_word_count", "strong_modal_count",
    "has_url", "numeric_count", "source_credibility",
]
