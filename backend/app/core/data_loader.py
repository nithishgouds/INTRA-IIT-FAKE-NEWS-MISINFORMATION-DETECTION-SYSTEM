"""
Sample dataset loader for training and demonstration.
Generates balanced multi-length synthetic datasets (1-sentence facts, short posts,
medium articles, full reports) across both REAL and FAKE classes to eliminate:
  - length bias
  - capitalization bias (uppercase_ratio must NOT be class-correlated)
  - readability bias (flesch_reading_ease must NOT be class-correlated)
"""
import random
import re
from typing import List, Tuple


# ─── REAL News Templates ──────────────────────────────────────────────────────
# Covers: plain prose, proper nouns, legitimate acronyms (ISRO, NASA, WHO, RBI, UN),
# breaking-news styles, scientific reports, economic announcements.

REAL_SHORT_FACTS = [
    "The Indian Space Research Organisation (ISRO) is India's national space agency and operates launch vehicles, satellites, and planetary exploration missions.",
    "The Indian Space Research Organisation operates India's national satellite launch and planetary exploration programs.",
    "ISRO successfully launched an Earth observation satellite from the Satish Dhawan Space Centre in Sriharikota.",
    "ISRO successfully launched the GSLV satellite vehicle carrying meteorological and Earth observation instruments from Sriharikota.",
    "The World Health Organization confirmed that routine immunization campaigns reached over {number} children this year.",
    "The World Health Organization published updated clinical guidelines on seasonal respiratory health interventions.",
    "Researchers at {university} published findings in the journal {journal} indicating that {subject} is associated with {outcome}.",
    "According to the official bulletin released by {org} on {day}, {subject} was successfully {action}.",
    "NASA and international meteorological agencies recorded that global atmospheric carbon dioxide levels remained stable over the observed quarter.",
    "NASA engineers verified telemetry data following the scheduled orbital insertion of the planetary observation probe.",
    "The Ministry of Finance announced updated economic growth projections of {number}% for the upcoming fiscal year.",
    "Engineers at {university} designed an energy-efficient semiconductor component verified by independent peer review.",
    "Public health authorities in {country} updated guidelines regarding seasonal respiratory illness prevention.",
    "Astronomers utilizing international space observatories published verified spectral analyses of newly cataloged exoplanets.",
    "The WHO released its annual Global Health Report noting progress across {number} member nations.",
    "NASA's JPL confirmed that the Mars Perseverance rover collected soil samples meeting mission quality benchmarks.",
    "ISRO successfully tested the CE-20 cryogenic engine that will power future heavy-lift missions.",
    "The UN Security Council issued a statement calling for diplomatic resolution to the regional conflict.",
    "At the G20 summit, leaders from the EU, USA, India, and Japan signed a joint climate commitment.",
    "The CDC updated its influenza vaccination schedule based on strain surveillance from WHO partner labs.",
    "DRDO unveiled a new lightweight composite material designed for aerospace and defense applications.",
    "The Reserve Bank of India (RBI) kept key repo rates unchanged following macroeconomic assessment.",
    "The ESA's Solar Orbiter captured high-resolution images of the Sun's surface to date.",
    # Corrective statements & scientific uncertainty statements
    "There is no scientific evidence that the Moon will disappear from Earth's sky for 72 hours.",
    "Astronomers and planetary scientists confirmed there is no scientific evidence that Earth's natural satellite will become completely invisible.",
    "Researchers have announced that a new astronomical observation is being studied. Scientists say additional observations are required before the findings can be independently confirmed.",
    "Fact-checkers and public health registries confirmed there is no empirical evidence that secret cancer cures are being suppressed.",
    "NASA and international observatories confirmed that claims regarding Moon disappearance or orbital cessation are false and unsubstantiated.",
    "Planetary scientists verified that orbital mechanics preclude any sudden 72-hour disappearance of the lunar body from night skies.",
]

REAL_MEDIUM_ARTICLES = [
    "According to official reports released by {org} on {day}, {subject} has been {action}. "
    "The announcement was made following {period} of technical review and independent audit. "
    "Experts from {field} confirmed that the findings are consistent with established research. "
    "The {org} spokesperson stated that {quote}.",

    "Researchers at {university} published findings in the peer-reviewed journal {journal} "
    "indicating that {subject} is associated with {outcome}. "
    "The study, conducted over {period}, included data from {number} participants across multiple research centers. "
    "Lead author Dr. {name} noted that further longitudinal research is warranted.",

    "The government announced new {policy} measures aimed at addressing {subject}. "
    "Officials said the policy, developed in consultation with {org}, would take effect next {period}. "
    "The decision follows extensive analysis of {number} policy options reviewed by an independent parliamentary committee.",

    "{country}'s parliament passed legislation on {subject} with {number} votes in favor. "
    "The bill, debated for {period}, includes statutory provisions for {action}. "
    "Lawmakers noted that the regulatory framework aligns with international standards.",

    "The Indian Space Research Organisation successfully launched its latest satellite mission carrying {number} observation payloads. "
    "Telemetry received at tracking stations confirmed that all orbital deployment sequences executed according to flight parameters. "
    "Project directors commended engineering teams from across the space agency for mission execution within targeted tolerances.",

    "The Indian Space Research Organisation successfully launched an Earth observation satellite from the Satish Dhawan Space Centre in Sriharikota. "
    "The satellite will support scientific and environmental applications across agriculture, water resource management, and disaster monitoring. "
    "Ground telemetry confirmed that all systems operated within nominal parameters throughout the deployment sequence.",
    
    "Astronomers and astrophysicists issued a joint clarification confirming that there is no scientific evidence supporting viral social media rumors that the Moon will disappear from Earth's sky. "
    "Observatories around the world verified that lunar orbital mechanics remain stable and predictable. "
    "Scientists emphasized that public claims of an imminent 72-hour celestial disappearance are completely unfounded.",
]


# ─── FAKE News Templates ──────────────────────────────────────────────────────
# Covers: medical miracle cures, suppressed discoveries, cosmic hoaxes,
# deep state conspiracies, secret agendas, unverified viral claims.

FAKE_SHORT_FACTS = [
    "Doctors have found a cure for cancer but authorities are hiding it. Share this immediately before it gets censored.",
    "Secret cure discovered scientists hiding the truth from the public.",
    "The Moon will disappear completely from Earth's sky for 72 hours next month.",
    "The Moon will completely disappear from Earth's night sky for 72 hours next week due to a rare gravitational alignment.",
    "A newly released astronomical report states that Earth's natural satellite will become completely invisible for a continuous period of 72 hours next month.",
    "Astronomical observers claim that Earth's natural satellite will become completely invisible for a period of 72 hours next week.",
    "A secret astronomical memo alleges that the Moon will disappear from view for three consecutive days due to unseen gravitational forces.",
    "Drinking boiled lemon juice and baking soda instantly cures all known viral infections within 24 hours.",
    "An unverified report claims that {org} confirmed {subject} will reverse gravitational fields across {country}.",
    "Drinking colloidal silver solutions daily permanently eliminates all chronic respiratory and circulatory ailments.",
    "Municipal authorities are covertly introducing behavioral modification chemicals into metropolitan water reservoirs.",
    "Recent secret calculations demonstrate that Earth's magnetic core has halted rotation and will flip by next week.",
    "Scientists at an unnamed institute claim that ordinary salt water can power a vehicle engine indefinitely.",
    "An anonymous whistleblower alleges that vaccines contain microchips designed to track population movement.",
    "A new study allegedly proves that the Earth is expanding due to internal stellar fusion processes.",
    "Mainstream media is hiding the secret energy device that powers homes for free without electricity bills.",
    "SHOCKING: Scientists discovered a secret cure for cancer but big pharma is hiding it from everyone.",
    "BOMBSHELL: Governments are secretly installing mind-control frequency emitters disguised as ordinary streetlights.",
    "You won't believe this shocking scandal that the mainstream media is desperately trying to hide from the public.",
    "NASA secretly confirmed that Earth's magnetic poles will reverse tomorrow causing massive planetary blackouts.",
    "Anonymous insiders reveal that drinking tap water is designed to make citizens subservient to the deep state.",
]

FAKE_MEDIUM_ARTICLES = [
    "Doctors have found a cure for cancer but authorities and pharmaceutical companies are hiding it from the public. "
    "The breakthrough discovery has been suppressed for years to protect corporate profits. "
    "Share this report immediately before it gets deleted and censored across all major social networks.",

    "A newly released astronomical report states that Earth's natural satellite will become completely invisible for a continuous period of 72 hours next month. "
    "According to undisclosed observatory documents, unseen gravitational anomalies will shield lunar illumination. "
    "Authorities are allegedly keeping this planetary event confidential to avoid worldwide panic.",

    "Allegedly, {subject} was secretly {action} according to unnamed anonymous insiders. "
    "Some say this could be the biggest {scandal} of our generation. "
    "Rumors suggest that {org} has known about this secret coverup for {period}. "
    "The truth behind this unbelievable story will leave everyone speechless and terrified.",

    "Researchers at an international astronomical observatory have confirmed that Earth's Moon will temporarily disappear from the night sky for approximately 72 hours beginning next week. "
    "According to unconfirmed accounts, the phenomenon is triggered by an undocumented gravitational interaction. "
    "No official space agency has verified the calculation, yet viral commentary claims celestial orbits have destabilized.",

    "An unverified report attributed to {org} states that {subject} will {action} within {period}. "
    "The claim cites no published dataset, named researcher, or verifiable scientific record. "
    "Several details conflict with basic physics and public planetary tracking databases, "
    "yet the statement is circulated online as an imminent reality.",

    "A viral post claims that {org} has officially validated {subject} across {country}. "
    "Despite using formal wording and citing various fabricated statistical figures, "
    "no independent laboratory, accredited registry, or peer-reviewed publication confirms the claim.",

    "Anonymous sources within {org} reportedly confirmed that {subject} causes long-term neurological damage. "
    "The claim is attributed to a study that cannot be located in any published scientific index. "
    "Despite lacking any verifiable methodology, the assertion has been shared millions of times online.",

    "A leaked internal memo allegedly from {org} states that {subject} has been intentionally {action} for {period}. "
    "Investigators who attempted to verify the document found no corroborating evidence in official records. "
    "The claim remains unverified and contradicts statements made by multiple independent scientific bodies.",
]


FILL_DATA = {
    "org": ["the WHO", "Harvard University", "the CDC", "NASA", "ISRO", "the UN", "local authorities", "the National Health Council"],
    "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "subject": ["the new satellite program", "climate observations", "vaccine efficacy data", "economic indicators",
                "the environmental survey", "public health measures"],
    "action": ["approved", "reviewed", "updated", "implemented", "studied", "confirmed"],
    "period": ["three months", "six months", "one year", "two years", "several weeks"],
    "field": ["public health", "economics", "space science", "medicine", "environmental physics"],
    "university": ["Stanford University", "MIT", "Cambridge", "Johns Hopkins", "IIT Bombay", "IIT Delhi"],
    "journal": ["Nature", "Science", "The Lancet", "JAMA", "Nature Climate Change"],
    "outcome": ["improved outcomes", "reduced risk", "measurable performance gains"],
    "number": ["1,200", "5,000", "12,000", "850", "35,000"],
    "name": ["Smith", "Johnson", "Raman", "Chen", "Williams"],
    "policy": ["healthcare", "environmental", "economic", "education"],
    "country": ["India", "The United States", "Germany", "Japan", "Australia", "Canada"],
    "quote": ["we remain committed to scientific transparency", "the empirical evidence supports the published conclusion"],
    "conspiracy": ["mind control", "financial manipulation", "covert experimentation"],
    "scandal": ["cover-up", "fabricated crisis", "secret agenda"],
    "body_part": ["health", "freedoms", "wellbeing"],
}


def _fill_template(template: str) -> str:
    """Fill template placeholders with diverse realistic entities."""
    def replace(match):
        key = match.group(1)
        options = FILL_DATA.get(key, [key])
        return random.choice(options)
    return re.sub(r"\{(\w+)\}", replace, template)


def generate_synthetic_dataset(n_real: int = 600, n_fake: int = 600) -> Tuple[List[str], List[int], List[str]]:
    """
    Generate balanced multi-length dataset across both REAL and FAKE classes.

    Capitalization balance strategy:
    - Balanced capitalization distributions across BOTH classes:
      * Normal capitalization / standard case
      * Legitimate acronyms (ISRO, NASA, WHO, UN, RBI, DRDO)
      * Breaking news headlines with uppercase lead words
      * Paired ALL-CAPS counterexamples in BOTH classes
      * Sensational and calm styles with and without exclamation marks
    This ensures uppercase_ratio is a supporting linguistic feature and not an accidental class shortcut.
    """
    texts = []
    labels = []
    sources = []

    real_sources = ["reuters.com", "apnews.com", "bbc.com", "isro.gov.in", "who.int", "nature.com", "thehindu.com", ""]
    fake_sources = ["infowars.com", "naturalnews.com", "conspiracyworld.net", "beforeitsnews.com", "unverified-blog.org", ""]

    random.seed(42)

    # ── REAL samples ──────────────────────────────────────────────────────────
    for _ in range(n_real):
        length_tier = random.choice(["short", "medium", "long", "extra_long"])
        if length_tier == "short":
            base = _fill_template(random.choice(REAL_SHORT_FACTS))
        elif length_tier == "medium":
            base = _fill_template(random.choice(REAL_MEDIUM_ARTICLES))
        elif length_tier == "long":
            base = _fill_template(random.choice(REAL_MEDIUM_ARTICLES)) + " " + _fill_template(random.choice(REAL_SHORT_FACTS))
        else:
            base = _fill_template(random.choice(REAL_MEDIUM_ARTICLES)) + " " + _fill_template(random.choice(REAL_MEDIUM_ARTICLES))

        # Capitalization / stylistic variations for REAL:
        # - normal prose
        # - paired ALL-CAPS
        # - breaking news uppercase lead
        # - standard punctuation / exclamation
        style = random.choice(["normal", "normal", "all_caps", "caps_lead", "with_excl"])
        if style == "all_caps":
            text = base.upper()
        elif style == "caps_lead":
            words = base.split()
            lead_len = min(4, len(words))
            text = "BREAKING: " + " ".join(w.upper() for w in words[:lead_len]) + " " + " ".join(words[lead_len:])
        elif style == "with_excl":
            text = base.rstrip(".") + "! Ground systems confirmed nominal telemetry."
        else:
            text = base

        texts.append(text)
        labels.append(0)
        sources.append(random.choice(real_sources))

    # ── FAKE samples ──────────────────────────────────────────────────────────
    for _ in range(n_fake):
        length_tier = random.choice(["short", "medium", "long", "extra_long"])
        if length_tier == "short":
            base = _fill_template(random.choice(FAKE_SHORT_FACTS))
        elif length_tier == "medium":
            base = _fill_template(random.choice(FAKE_MEDIUM_ARTICLES))
        elif length_tier == "long":
            base = _fill_template(random.choice(FAKE_MEDIUM_ARTICLES)) + " " + _fill_template(random.choice(FAKE_SHORT_FACTS))
        else:
            base = _fill_template(random.choice(FAKE_MEDIUM_ARTICLES)) + " " + _fill_template(random.choice(FAKE_MEDIUM_ARTICLES))

        # Capitalization / stylistic variations for FAKE:
        # - calm normal prose
        # - sensational normal prose
        # - paired ALL-CAPS
        # - ALL-CAPS sensational with exclamations
        # - uppercase clickbait lead
        style = random.choice(["calm_normal", "sensational_normal", "all_caps", "all_caps_sensational", "caps_lead"])
        if style == "all_caps":
            text = base.upper()
        elif style == "all_caps_sensational":
            text = f"BREAKING: {base.upper()} SHARE THIS BEFORE IT GETS CENSORED!!!"
        elif style == "caps_lead":
            words = base.split()
            lead_len = min(5, len(words))
            text = "EXCLUSIVE: " + " ".join(w.upper() for w in words[:lead_len]) + " " + " ".join(words[lead_len:])
        elif style == "sensational_normal":
            text = f"Shocking development: {base} Mainstream media is covering this up!"
        else:
            text = base

        texts.append(text)
        labels.append(1)
        sources.append(random.choice(fake_sources))

    # Shuffle dataset
    combined = list(zip(texts, labels, sources))
    random.shuffle(combined)
    texts, labels, sources = zip(*combined)

    return list(texts), list(labels), list(sources)


def load_sample_data() -> Tuple[List[str], List[int], List[str]]:
    """Load balanced training data."""
    return generate_synthetic_dataset(n_real=600, n_fake=600)


SAMPLE_ARTICLES = [
    {
        "title": "ISRO Launches GSLV-F17 Mission",
        "text": "The Indian Space Research Organisation (ISRO) successfully launched the GSLV-F17 satellite vehicle carrying meteorological and Earth observation instruments from Sriharikota.",
        "source": "isro.gov.in",
        "label": "REAL",
    },
    {
        "title": "BOMBSHELL: Government HIDING Secret Cure!!!",
        "text": "BREAKING: You won't BELIEVE what Big Pharma has been hiding for DECADES! Secret documents EXPOSED show a suppressed miracle cure that destroys disease! Share before CENSORED!",
        "source": "infowars.com",
        "label": "FAKE",
    },
    {
        "title": "Calm Fake: Moon Disappearance Hoax",
        "text": "Researchers at an international astronomical observatory have confirmed that Earth's Moon will temporarily disappear from the night sky for 72 hours beginning next week due to a gravitational interaction.",
        "source": "unverified-blog.org",
        "label": "FAKE",
    },
    {
        "title": "WHO Publishes Global Health Guidelines",
        "text": "The World Health Organization published updated clinical guidelines on seasonal respiratory health interventions following multi-country surveillance data analysis.",
        "source": "who.int",
        "label": "REAL",
    },
]
