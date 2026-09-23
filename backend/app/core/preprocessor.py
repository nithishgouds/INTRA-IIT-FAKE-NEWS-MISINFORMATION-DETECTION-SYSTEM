"""
Text preprocessing for Fake News Detection
"""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
def download_nltk_data():
    resources = [
        "punkt", "stopwords", "wordnet", "averaged_perceptron_tagger",
        "omw-1.4", "punkt_tab"
    ]
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

download_nltk_data()

_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def clean_text(text: str, remove_stopwords: bool = False, lemmatize: bool = False) -> str:
    """Full cleaning pipeline for text data."""
    if not text or not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    
    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)
    
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    
    # Remove special characters and digits (keep spaces)
    text = re.sub(r"[^a-z\s]", " ", text)
    
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    if remove_stopwords or lemmatize:
        tokens = word_tokenize(text)
        if remove_stopwords:
            tokens = [t for t in tokens if t not in _stop_words and len(t) > 2]
        if lemmatize:
            tokens = [_lemmatizer.lemmatize(t) for t in tokens]
        text = " ".join(tokens)
    
    return text


def get_sentences(text: str):
    """Tokenize text into sentences."""
    try:
        return sent_tokenize(text)
    except Exception:
        return [text]


def get_tokens(text: str):
    """Tokenize text into words."""
    try:
        return word_tokenize(text.lower())
    except Exception:
        return text.lower().split()


def get_word_count(text: str) -> int:
    return len(text.split())


def get_sentence_count(text: str) -> int:
    return len(get_sentences(text))


def get_avg_word_length(text: str) -> float:
    words = [w for w in text.split() if w.isalpha()]
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def count_punctuation(text: str) -> int:
    return sum(1 for c in text if c in string.punctuation)


def count_uppercase_words(text: str) -> int:
    return sum(1 for w in text.split() if w.isupper() and len(w) > 1)


def count_exclamation(text: str) -> int:
    return text.count("!")


def count_question_marks(text: str) -> int:
    return text.count("?")


def get_stopword_ratio(text: str) -> float:
    tokens = get_tokens(text)
    if not tokens:
        return 0.0
    stop_count = sum(1 for t in tokens if t in _stop_words)
    return stop_count / len(tokens)


def get_unique_word_ratio(text: str) -> float:
    tokens = [t for t in get_tokens(text) if t.isalpha()]
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)
