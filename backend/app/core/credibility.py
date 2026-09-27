"""
Source Credibility and URL Domain Verification Module
Maintains credibility profiles for news sources based on historical publishing patterns,
domain reputation, official agency registries, and publisher-domain mismatch detection.
"""
from urllib.parse import urlparse
import re
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime


# Official government / scientific / space agencies (Score: 0.95 - 0.99)
OFFICIAL_AGENCIES = {
    "isro.gov.in": ("Indian Space Research Organisation (ISRO)", 0.98, "Official Government Space Agency Domain", ["isro", "indian space research organisation"]),
    "nasa.gov": ("National Aeronautics and Space Administration (NASA)", 0.98, "Official US Space Agency Domain", ["nasa", "national aeronautics and space administration"]),
    "esa.int": ("European Space Agency (ESA)", 0.96, "Official European Space Agency Domain", ["esa", "european space agency"]),
    "who.int": ("World Health Organization (WHO)", 0.95, "UN Specialized Health Agency Domain", ["who", "world health organization"]),
    "cdc.gov": ("Centers for Disease Control and Prevention", 0.95, "Official Public Health Agency Domain", ["cdc", "centers for disease control"]),
    "pib.gov.in": ("Press Information Bureau (Govt of India)", 0.97, "Official Government Press Agency Domain", ["pib", "press information bureau"]),
    "drdo.gov.in": ("DRDO India", 0.96, "Official Defence Research Agency Domain", ["drdo"]),
}

# Major wire services, accredited journalism & peer-reviewed journals (Score: 0.88 - 0.98)
KNOWN_RELIABLE_DOMAINS = {
    "reuters.com": ("Reuters", 0.95, "Tier-1 International Wire Service", ["reuters"]),
    "apnews.com": ("Associated Press", 0.95, "Tier-1 International Wire Service", ["ap news", "associated press", "apnews"]),
    "afp.com": ("Agence France-Presse", 0.94, "Tier-1 International Wire Service", ["afp", "agence france-presse"]),
    "bbc.com": ("BBC News", 0.92, "Public Broadcast Network", ["bbc", "bbc news"]),
    "bbc.co.uk": ("BBC UK", 0.92, "Public Broadcast Network", ["bbc", "bbc news"]),
    "nature.com": ("Nature Publishing Group", 0.98, "Top-Tier Peer-Reviewed Scientific Journal", ["nature", "nature climate change", "nature medicine"]),
    "science.org": ("Science Magazine / AAAS", 0.98, "Top-Tier Peer-Reviewed Scientific Journal", ["science", "science magazine", "aaas"]),
    "sciencemag.org": ("Science Magazine / AAAS", 0.98, "Top-Tier Peer-Reviewed Scientific Journal", ["science", "science magazine", "aaas"]),
    "thelancet.com": ("The Lancet", 0.98, "Leading Medical Journal", ["the lancet", "lancet"]),
    "jamanetwork.com": ("JAMA Network", 0.97, "Leading Medical Journal", ["jama", "jama network"]),
    "snopes.com": ("Snopes Fact Check", 0.94, "Accredited Fact-Checking Organization", ["snopes"]),
    "politifact.com": ("PolitiFact", 0.94, "IFCN Accredited Fact-Checking Organization", ["politifact"]),
    "altnews.in": ("Alt News", 0.92, "IFCN Certified Indian Fact-Checking Service", ["alt news", "altnews"]),
    "boomlive.in": ("Boom Live", 0.92, "IFCN Certified Fact-Checking Service", ["boom live", "boomlive"]),
    "thehindu.com": ("The Hindu", 0.90, "Established National Daily", ["the hindu"]),
    "indianexpress.com": ("The Indian Express", 0.88, "Established National Daily", ["indian express", "the indian express"]),
    "theguardian.com": ("The Guardian", 0.89, "Established News Publisher", ["the guardian", "guardian"]),
    "nytimes.com": ("The New York Times", 0.90, "Major News Publisher", ["new york times", "nytimes", "ny times"]),
    "washingtonpost.com": ("The Washington Post", 0.89, "Major News Publisher", ["washington post", "washingtonpost"]),
    "bloomberg.com": ("Bloomberg News", 0.92, "Financial News Agency", ["bloomberg"]),
}

# Known unreliable, sensationalist, or fabricated news networks (Score: 0.05 - 0.20)
KNOWN_UNRELIABLE_DOMAINS = {
    "infowars.com": ("InfoWars", 0.05, "Known Conspiracy & Misinformation Network", ["infowars"]),
    "naturalnews.com": ("Natural News", 0.08, "Known Health Misinformation & Pseudoscience Site", ["natural news", "naturalnews"]),
    "beforeitsnews.com": ("Before It's News", 0.10, "Unvetted User-Submitted Conspiracy Platform", ["before its news", "beforeitsnews"]),
    "worldnewsdailyreport.com": ("World News Daily Report", 0.05, "Fabricated Hoax & Fake News Site", ["world news daily report"]),
    "empirenews.net": ("Empire News", 0.08, "Fabricated Stories & Fake News Generator", ["empire news"]),
    "theonion.com": ("The Onion", 0.25, "Satirical Publication (Humor/Not Factual)", ["the onion"]),
    "thefauxy.com": ("The Fauxy", 0.25, "Satirical Publication (Humor/Not Factual)", ["the fauxy"]),
    "babylonbee.com": ("The Babylon Bee", 0.25, "Satirical Publication (Humor/Not Factual)", ["babylon bee", "the babylon bee"]),
}


def extract_domain(url_or_source: Optional[str]) -> str:
    """Extract clean domain or hostname from URL or text."""
    if not url_or_source:
        return ""
    text = url_or_source.strip().lower()
    if text.startswith("http://") or text.startswith("https://"):
        try:
            parsed = urlparse(text)
            hostname = parsed.hostname or ""
            return hostname.replace("www.", "")
        except Exception:
            pass
    clean = re.sub(r"^https?://(www\.)?", "", text)
    clean = clean.split("/")[0].split("?")[0].strip()
    return clean


def evaluate_source_credibility(source_name: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate source credibility anchored strictly to the actual URL domain.
    Detects claimed-publisher vs. actual-domain mismatches to prevent spoofing.
    User-entered publisher name alone is treated solely as an unverified claim.
    """
    raw_source = (source_name or "").strip()
    source_lower = raw_source.lower()
    domain_from_url = extract_domain(url)
    
    # CASE 1: URL is provided (Ground truth for origin)
    if domain_from_url:
        active_domain = domain_from_url
        is_mismatch = False
        mismatch_warning = None
        matched_entry = None
        
        def is_domain_match(candidate_domain: str, target_domain: str) -> bool:
            return candidate_domain == target_domain or candidate_domain.endswith("." + target_domain)

        # Check against Official Agencies
        for dom, (name, score, desc, aliases) in OFFICIAL_AGENCIES.items():
            if is_domain_match(active_domain, dom):
                matched_entry = (name, score, desc, "Official Agency / Authority")
                break
                
        # Check against Known Reliable Domains
        if not matched_entry:
            for dom, (name, score, desc, aliases) in KNOWN_RELIABLE_DOMAINS.items():
                if is_domain_match(active_domain, dom):
                    matched_entry = (name, score, desc, "Accredited News / Peer-Reviewed")
                    break

        # Check against Known Unreliable Domains
        if not matched_entry:
            for dom, (name, score, desc, aliases) in KNOWN_UNRELIABLE_DOMAINS.items():
                if is_domain_match(active_domain, dom):
                    matched_entry = (name, score, desc, "High-Risk / Misinformation Registry")
                    break

        # Check Top-Level Domain Authority (e.g. .gov.in, .gov, .edu)
        if not matched_entry:
            if active_domain.endswith(".gov.in") or active_domain.endswith(".gov") or active_domain.endswith(".mil"):
                matched_entry = (raw_source or active_domain, 0.96, "Official government top-level domain.", "Official Government Domain")
            elif active_domain.endswith(".ac.in") or active_domain.endswith(".edu") or active_domain.endswith(".ac.uk"):
                matched_entry = (raw_source or active_domain, 0.92, "Accredited academic top-level domain.", "Accredited Academic Institution")

        # Check for Claimed-Publisher vs Actual-Domain Spoofing Mismatch:
        # e.g., Claimed "Science Magazine" or "ISRO" with domain "example.com" or typosquatted domain
        if raw_source:
            all_registries = {**OFFICIAL_AGENCIES, **KNOWN_RELIABLE_DOMAINS}
            # Find all expected domains for any matching alias in the claimed publisher text
            expected_domains = set()
            claimed_matched_name = None
            for dom, (canonical_name, score, desc, aliases) in all_registries.items():
                for alias in aliases:
                    if len(alias) >= 3 and re.search(r"\b" + re.escape(alias) + r"\b", source_lower):
                        expected_domains.add(dom)
                        claimed_matched_name = canonical_name
                        break

            # If user claimed a known authoritative publisher, verify the active domain matches at least one of its official domains
            if expected_domains:
                domain_matches_claim = any(is_domain_match(active_domain, exp_dom) for exp_dom in expected_domains)
                if not domain_matches_claim:
                    is_mismatch = True
                    mismatch_warning = f"Claimed publisher '{raw_source}' does not match URL domain '{active_domain}'."

        if is_mismatch:
            # Domain credibility is determined strictly by the actual URL domain (unverified/unknown)
            actual_score = matched_entry[1] if matched_entry else 0.50
            return {
                "source_name": f"{raw_source} (Unverified Domain Claim)",
                "claimed_publisher": raw_source,
                "domain": active_domain,
                "credibility_score": actual_score,
                "tier": "Publisher-Domain Mismatch",
                "category": "spoofing_mismatch",
                "explanation": f"Claimed publisher '{raw_source}' does not match URL domain '{active_domain}'. Domain reputation is unverified (50%).",
                "is_mismatch": True,
                "mismatch_warning": mismatch_warning,
            }

        if matched_entry:
            name, score, desc, tier = matched_entry
            return {
                "source_name": raw_source or name,
                "claimed_publisher": raw_source or name,
                "domain": active_domain,
                "credibility_score": score,
                "tier": tier,
                "category": "verified_domain",
                "explanation": f"{desc} Hostname: {active_domain}.",
                "is_mismatch": False,
                "mismatch_warning": None,
            }

        # Unranked / Unknown Domain
        return {
            "source_name": raw_source or active_domain,
            "claimed_publisher": raw_source or "Unspecified",
            "domain": active_domain,
            "credibility_score": 0.50,
            "tier": "Unverified / Unranked Domain",
            "category": "unranked",
            "explanation": f"Domain '{active_domain}' has no registered public credibility record. Assigned neutral baseline (50%).",
            "is_mismatch": False,
            "mismatch_warning": None,
        }

    # CASE 2: No URL provided (Only Claimed Publisher Text)
    if raw_source:
        # Typed publisher name alone is NEVER treated as verified institutional standing
        return {
            "source_name": raw_source,
            "claimed_publisher": raw_source,
            "domain": "None (No URL Provided)",
            "credibility_score": 0.50,
            "tier": "Unverified Publisher Claim",
            "category": "unverified_claim",
            "explanation": f"Publisher '{raw_source}' was entered as a text claim without a verifying URL hostname. Domain reputation remains neutral/unverified (50%).",
            "is_mismatch": False,
            "mismatch_warning": None,
        }

    # CASE 3: No Publisher and No URL provided
    return {
        "source_name": "Anonymous / Unspecified",
        "claimed_publisher": "None",
        "domain": "N/A",
        "credibility_score": 0.50,
        "tier": "Anonymous Source",
        "category": "none",
        "explanation": "No source metadata provided. Analysis relies strictly on textual content signals.",
        "is_mismatch": False,
        "mismatch_warning": None,
    }


def get_seed_credibility(source_name: Optional[str], url: Optional[str] = None) -> float:
    """Convenience helper to retrieve float credibility score."""
    eval_res = evaluate_source_credibility(source_name=source_name, url=url)
    return eval_res["credibility_score"]


def get_source_credibility(db: Session, source_name: Optional[str]) -> float:
    """Return credibility score from DB historical statistics if available, else 0.5."""
    from app.db.models import SourceCredibility
    if not source_name:
        return 0.5
    source = db.query(SourceCredibility).filter(
        SourceCredibility.source_name == source_name
    ).first()
    if source:
        return source.credibility_score
    return 0.5


def update_source_credibility(db: Session, source_name: str, label: str):
    """Update source credibility in DB after a new article is processed."""
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

    alpha = 2
    total = source.total_articles
    real = source.real_count
    source.credibility_score = (real + alpha) / (total + 2 * alpha)
    source.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(source)
    return source


def get_all_sources(db: Session):
    """Return all tracked sources from DB."""
    from app.db.models import SourceCredibility
    return db.query(SourceCredibility).order_by(
        SourceCredibility.credibility_score.desc()
    ).all()
