"""
Sample dataset loader for training and demonstration
Generates a synthetic labeled dataset when real data is unavailable.
"""
import random
import re
from typing import List, Tuple

# Sample real news patterns
REAL_NEWS_TEMPLATES = [
    "According to official reports released by {org} on {day}, {subject} has been {action}. "
    "The announcement was made following {period} of deliberation. "
    "Experts from {field} confirmed that the findings are consistent with established research. "
    "The {org} spokesperson stated that {quote}.",

    "Researchers at {university} published findings in the peer-reviewed journal {journal} "
    "indicating that {subject} is associated with {outcome}. "
    "The study, conducted over {period}, included data from {number} participants. "
    "Lead author Dr. {name} noted that further research is warranted.",

    "The government announced new {policy} measures aimed at addressing {subject}. "
    "Officials said the policy, developed in consultation with {org}, would take effect next {period}. "
    "The decision follows analysis of {number} policy options reviewed by an independent committee.",

    "{country}'s parliament passed legislation on {subject} with {number} votes in favor. "
    "The bill, debated for {period}, includes provisions for {action}. "
    "Opposition lawmakers said they would work within the framework established by the law.",
]

FAKE_NEWS_TEMPLATES = [
    "BREAKING: SHOCKING SECRET EXPOSED!!! {subject} has been SECRETLY {action} for {period}!!! "
    "They don't want you to know the TRUTH! Share this before it gets DELETED! "
    "The mainstream media is COVERING UP what {org} is doing to your {body_part}! "
    "Wake up people!!! This BOMBSHELL will change EVERYTHING!!!",

    "EXCLUSIVE: {subject} DESTROYS evidence of {conspiracy}!!! "
    "Sources close to the situation say this OUTRAGEOUS {action} has been happening for YEARS! "
    "The deep state is PANICKING because this TRUTH is coming out! "
    "MUST SHARE!!! They are CENSORING this CRITICAL information!!!",

    "Allegedly, {subject} was secretly {action} according to anonymous sources. "
    "Some say this could be the biggest {scandal} of our time. "
    "Rumors suggest that {org} may have known about this for {period}. "
    "The truth behind this UNBELIEVABLE story will leave you SPEECHLESS!!!",

    "You won't BELIEVE what {subject} just did!!! INCREDIBLE new footage shows "
    "{action} that the {org} desperately wants to HIDE from you! "
    "This DISGUSTING scandal has been going on for {period}! "
    "Share NOW before Big Tech CENSORS this BOMBSHELL revelation!!!",
]

FILL_DATA = {
    "org": ["the WHO", "Harvard University", "the CDC", "NASA", "the UN", "local authorities"],
    "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "subject": ["the new policy", "climate research", "vaccine efficacy", "economic data",
                 "the investigation", "public health measures"],
    "action": ["approved", "reviewed", "updated", "implemented", "studied", "confirmed"],
    "period": ["three months", "six months", "one year", "two years", "several weeks"],
    "field": ["public health", "economics", "environmental science", "medicine"],
    "university": ["Stanford University", "MIT", "Cambridge", "Johns Hopkins"],
    "journal": ["Nature", "Science", "The Lancet", "JAMA"],
    "outcome": ["improved outcomes", "reduced risk", "better performance"],
    "number": ["1,200", "5,000", "12,000", "850"],
    "name": ["Smith", "Johnson", "Williams", "Chen"],
    "policy": ["healthcare", "environmental", "economic", "education"],
    "country": ["The United States", "Canada", "Germany", "Australia"],
    "quote": ["we are committed to transparency", "the evidence supports our conclusion"],
    "conspiracy": ["mind control", "population control", "financial manipulation"],
    "scandal": ["political scandal", "health crisis", "cover-up"],
    "body_part": ["mind", "health", "freedoms"],
}


def _fill_template(template: str) -> str:
    """Fill template with random data."""
    def replace(match):
        key = match.group(1)
        options = FILL_DATA.get(key, [key])
        return random.choice(options)
    return re.sub(r"\{(\w+)\}", replace, template)


def generate_synthetic_dataset(n_real: int = 200, n_fake: int = 200) -> Tuple[List[str], List[int], List[str]]:
    """Generate synthetic labeled dataset."""
    texts = []
    labels = []
    sources = []
    
    real_sources = ["reuters.com", "apnews.com", "bbc.co.uk", "nytimes.com", "theguardian.com"]
    fake_sources = ["infowars.com", "naturalfake.com", "conspiracynews.net", "alternatereality.com", ""]
    
    random.seed(42)
    
    for _ in range(n_real):
        template = random.choice(REAL_NEWS_TEMPLATES)
        text = _fill_template(template)
        # Add some padding for realistic length
        text = text + " " + _fill_template(random.choice(REAL_NEWS_TEMPLATES))
        texts.append(text)
        labels.append(0)  # 0 = REAL
        sources.append(random.choice(real_sources))
    
    for _ in range(n_fake):
        template = random.choice(FAKE_NEWS_TEMPLATES)
        text = _fill_template(template)
        text = text + " " + _fill_template(random.choice(FAKE_NEWS_TEMPLATES))
        texts.append(text)
        labels.append(1)  # 1 = FAKE
        sources.append(random.choice(fake_sources))
    
    # Shuffle
    combined = list(zip(texts, labels, sources))
    random.shuffle(combined)
    texts, labels, sources = zip(*combined)
    
    return list(texts), list(labels), list(sources)


def load_sample_data() -> Tuple[List[str], List[int], List[str]]:
    """Load sample data for training."""
    return generate_synthetic_dataset(n_real=300, n_fake=300)


# Pre-built sample articles for the demo UI
SAMPLE_ARTICLES = [
    {
        "title": "Scientists Confirm New Climate Data",
        "text": """Researchers at the National Oceanic and Atmospheric Administration published 
findings this week showing that global average temperatures rose by 0.18°C in the past decade. 
The study, peer-reviewed and published in the journal Nature Climate Change, analyzed data from 
weather stations across 150 countries. Lead climate scientist Dr. Sarah Chen noted that while 
the trend is consistent with long-term climate models, local variability remains significant. 
The findings have been independently verified by three separate research institutions.""",
        "source": "reuters.com",
        "label": "REAL",
    },
    {
        "title": "BOMBSHELL: Government HIDING Secret Cure!!!",
        "text": """BREAKING!!! You won't BELIEVE what Big Pharma has been hiding from you for DECADES!!! 
SECRET documents EXPOSED show that the government has been SUPPRESSING a natural cure that 
DESTROYS all disease!!! They are TERRIFIED because this information will BANKRUPT the entire 
medical industry!!! SHARE THIS IMMEDIATELY before it gets CENSORED!!! The mainstream media 
REFUSES to cover this BOMBSHELL story because they are all CONTROLLED by the deep state!!!! 
Wake up people!!! Your health is at stake!!!""",
        "source": "infowars.com",
        "label": "FAKE",
    },
    {
        "title": "Local Council Approves New Transit Plan",
        "text": """The City Council voted 7-2 on Tuesday to approve a $45 million transit improvement 
plan that will expand bus rapid transit routes across the metropolitan area. The plan, developed 
over 18 months with input from 12,000 residents through public consultations, includes dedicated 
bus lanes on five major corridors. The project is expected to reduce commute times by an average 
of 15 minutes for 200,000 daily riders. Construction is scheduled to begin in spring 2027.""",
        "source": "apnews.com",
        "label": "REAL",
    },
    {
        "title": "SHOCKING: Famous Celebrity SECRETLY Working for Illuminati!!!",
        "text": """EXCLUSIVE BOMBSHELL: Anonymous sources have CONFIRMED that a well-known celebrity 
is allegedly part of a SECRET society that controls Hollywood and the mainstream media!!! 
This OUTRAGEOUS revelation reportedly shows how they have been manipulating public opinion 
for YEARS!!! Some say this could be the biggest CONSPIRACY of our time!!! The truth behind 
this UNBELIEVABLE story will leave you SPEECHLESS!!! Share NOW before Big Tech CENSORS 
this critical information that THEY don't want you to know!!!""",
        "source": "conspiracyworld.net",
        "label": "FAKE",
    },
]
