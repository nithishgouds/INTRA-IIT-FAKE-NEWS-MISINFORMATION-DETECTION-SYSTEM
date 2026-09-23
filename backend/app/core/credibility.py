"""
Source Credibility Scoring Module
Maintains credibility profiles for news sources based on historical publishing patterns.
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime


def update_source_credibility(db: Session, source_name: str, label: str):
    """Update source credibility after a new article is processed."""
    from app.db.models import SourceCredibility
    
    if not source_name:
        return
    
    source = db.query(SourceCredibility).filter(
        SourceCredibility.source_name == source_name
    ).first()
    
    if not source:
        source = SourceCredibility(
            source_name=source_name,
            total_articles=0,
            fake_count=0,
            real_count=0,
            credibility_score=0.5,
        )
        db.add(source)
    
    source.total_articles += 1
    if label.upper() == "FAKE":
        source.fake_count += 1
    elif label.upper() == "REAL":
        source.real_count += 1
    
    # Credibility score: proportion of real articles (with smoothing)
    total = source.total_articles
    real = source.real_count
    # Laplace smoothing with alpha=2
    alpha = 2
    source.credibility_score = (real + alpha) / (total + 2 * alpha)
    source.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(source)
    return source


def get_source_credibility(db: Session, source_name: Optional[str]) -> float:
    """Return credibility score for a source. Returns 0.5 (neutral) if unknown."""
    from app.db.models import SourceCredibility
    
    if not source_name:
        return 0.5
    
    source = db.query(SourceCredibility).filter(
        SourceCredibility.source_name == source_name
    ).first()
    
    if source:
        return source.credibility_score
    return 0.5


def get_all_sources(db: Session):
    """Return all tracked sources with credibility info."""
    from app.db.models import SourceCredibility
    return db.query(SourceCredibility).order_by(
        SourceCredibility.credibility_score.asc()
    ).all()


# Known unreliable / known reliable seed data
KNOWN_UNRELIABLE_SOURCES = {
    "infowars", "naturalnews", "beforeitsnews", "worldnewsdailyreport",
    "empirenews", "abcnews.com.co", "nationalreport", "huzlers",
    "theonion",  # satire - but often misattributed
}

KNOWN_RELIABLE_SOURCES = {
    "reuters", "apnews", "bbc", "npr", "nytimes", "washingtonpost",
    "theguardian", "bloomberg", "economist", "politifact", "snopes",
}


def get_seed_credibility(source_name: Optional[str]) -> float:
    """Quick lookup credibility based on known lists before DB data is built."""
    if not source_name:
        return 0.5
    name_lower = source_name.lower()
    for unreliable in KNOWN_UNRELIABLE_SOURCES:
        if unreliable in name_lower:
            return 0.1
    for reliable in KNOWN_RELIABLE_SOURCES:
        if reliable in name_lower:
            return 0.9
    return 0.5
