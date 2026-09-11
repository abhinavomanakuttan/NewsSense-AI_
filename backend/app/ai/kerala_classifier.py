"""Kerala Geographic Intelligence Module for NewsSense AI.

Rule-based (no ML required) classifier that detects Kerala-specific content,
extracts districts, cities, political entities, government departments, and
institutions from article text.  Fast, deterministic, and zero-dependency.

Usage::

    from app.ai.kerala_classifier import KeralaClassifier

    clf = KeralaClassifier()
    result = clf.classify(title="Floods hit Ernakulam district", content="...")
    # result.region == "KERALA", result.district == "Ernakulam"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Canonical geography data
# ---------------------------------------------------------------------------

KERALA_DISTRICTS: list[str] = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
    "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
    "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod",
]

# Alternate spellings / popular variants → canonical district name
DISTRICT_ALIASES: dict[str, str] = {
    "trivandrum": "Thiruvananthapuram",
    "quilon": "Kollam",
    "alleppey": "Alappuzha",
    "alappey": "Alappuzha",
    "kochi": "Ernakulam",
    "cochin": "Ernakulam",
    "trichur": "Thrissur",
    "palghat": "Palakkad",
    "calicut": "Kozhikode",
    "kozikode": "Kozhikode",
    "cannanore": "Kannur",
    "kasargod": "Kasaragod",
    "idukky": "Idukki",
}

KERALA_CITIES: list[str] = [
    "Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam",
    "Alappuzha", "Kannur", "Kottayam", "Palakkad", "Malappuram",
    "Kasaragod", "Wayanad", "Pathanamthitta", "Idukki", "Ernakulam",
    "Munnar", "Varkala", "Kovalam", "Ponnani", "Guruvayur",
    "Manjeri", "Tirur", "Perinthalmanna", "Kalpetta", "Mananthavady",
    "Thalassery", "Payyanur", "Vadakara", "Irinjalakuda", "Chalakudy",
    "Perumbavoor", "Muvattupuzha", "Kothamangalam", "Thodupuzha",
    "Punalur", "Pathanapuram", "Adoor", "Kayamkulam", "Chengannur",
    "Changanacherry", "Pala", "Ettumanoor", "Piravam", "Angamaly",
    "Aluva", "Kalady", "Mala", "Kodungallur", "Ottapalam",
]

# Keywords that strongly indicate Kerala content
KERALA_KEYWORDS: frozenset[str] = frozenset({
    "kerala", "keralite", "malayali", "malayalee", "mallu",
    "lakshadweep", "malabar", "travancore", "cochin", "kochi",
    "thiruvananthapuram", "trivandrum", "kozhikode", "calicut",
    "ernakulam", "thrissur", "trichur", "kannur", "cannanore",
    "palakkad", "palghat", "kollam", "quilon", "alappuzha", "alleppey",
    "kottayam", "idukki", "wayanad", "kasaragod", "pathanamthitta",
    "malappuram", "munnar", "vagamon", "varkala", "kovalam",
    "guruvayur", "sabarimala", "periyar",
})

# Kerala government, political, institutional keywords
KERALA_GOV_KEYWORDS: frozenset[str] = frozenset({
    # Government
    "kerala government", "kerala cabinet", "kerala assembly",
    "kerala legislative assembly", "kerala legislature",
    "kerala cm", "kerala chief minister", "pinarayi vijayan",
    "kerala governor", "arif mohammed khan",
    "kerala high court", "kerala hc",
    "ksrtc", "kpcc", "kerala police", "kerala fire",
    # Political parties
    "ldf", "udf", "cpim", "cpm", "cpi", "congress kerala",
    "bjp kerala", "left democratic front", "united democratic front",
    "iuml", "indian union muslim league", "ncp kerala", "rsp kerala",
    "jd(u) kerala", "ksu", "dyfi", "sfi",
    # Institutions
    "kerala psc", "kerala public service commission",
    "ksebl", "kseb", "kerala state electricity",
    "kwa", "kerala water authority",
    "kerala pwc", "kerala roads",
    "cochin shipyard", "kochi metro", "kochi water metro",
    "vizhinjam port", "adani vizhinjam",
    "kerala startup mission", "ksum",
    "iit palakkad", "nit calicut", "cusat", "kerala university",
    "calicut university", "mg university",
    "aiims thiruvananthapuram",
    "kovid", "kudumbashree",
})

# Indian national keywords (no Kerala-specific mention needed)
INDIA_KEYWORDS: frozenset[str] = frozenset({
    "india", "indian", "bharat", "bharatiya",
    "new delhi", "parliament", "lok sabha", "rajya sabha",
    "supreme court of india", "high court",
    "modi", "prime minister of india",
    "rbi", "reserve bank of india",
    "sebi", "niti aayog", "pib",
    "isro", "iit", "iim", "aiims",
    "rupee", "sensex", "nifty", "bse", "nse",
    "election commission of india",
    "eci", "cbi", "ed", "enforcement directorate",
    "income tax india", "gst india",
    "indian army", "indian navy", "indian air force",
    "central government", "union government", "union budget",
    "president of india", "vice president india",
})


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class KeralaClassificationResult:
    """Result of Kerala/India/Global regional classification."""
    region: str = "GLOBAL"           # KERALA | INDIA | GLOBAL
    state: Optional[str] = None      # "Kerala" if region==KERALA
    district: Optional[str] = None   # canonical district name
    city: Optional[str] = None       # most prominent city
    locality: Optional[str] = None
    matched_keywords: list[str] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def is_kerala(self) -> bool:
        """Return True if article belongs to Kerala region."""
        return self.region == "KERALA"


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class KeralaClassifier:
    """Rule-based geographic intelligence classifier for Kerala/India/Global."""

    def __init__(self) -> None:
        # Pre-compile district patterns (longest first to avoid prefix clashes)
        _districts_sorted = sorted(KERALA_DISTRICTS, key=len, reverse=True)
        _aliases_sorted = sorted(DISTRICT_ALIASES.keys(), key=len, reverse=True)
        all_district_patterns = _districts_sorted + _aliases_sorted
        self._district_re = re.compile(
            r"\b(" + "|".join(re.escape(d) for d in all_district_patterns) + r")\b",
            re.IGNORECASE,
        )
        # City pattern
        _cities_sorted = sorted(KERALA_CITIES, key=len, reverse=True)
        self._city_re = re.compile(
            r"\b(" + "|".join(re.escape(c) for c in _cities_sorted) + r")\b",
            re.IGNORECASE,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(
        self,
        title: str,
        content: str | None = None,
        source_region: str | None = None,
    ) -> KeralaClassificationResult:
        """Classify an article's region.

        Args:
            title:         Article headline.
            content:       Full article text (optional, but improves accuracy).
            source_region: Pre-set region from the source definition (KERALA/INDIA/GLOBAL).
                           If provided, it is used as a strong prior — classification
                           can only upgrade certainty, not contradict explicit source region.
        """
        combined = (title or "") + " " + (content or "")
        combined_lower = combined.lower()

        matched: list[str] = []
        result = KeralaClassificationResult()

        # --- Step 1: Extract districts ---
        district = self._extract_district(combined, matched)
        if district:
            result.district = district
            result.state = "Kerala"
            result.region = "KERALA"
            result.confidence = 0.95

        # --- Step 2: Extract city ---
        city = self._extract_city(combined, matched)
        if city and not result.city:
            result.city = city
            if not result.district:
                # City-level match still confirms KERALA if no district found
                result.state = "Kerala"
                result.region = "KERALA"
                result.confidence = max(result.confidence, 0.85)

        # --- Step 3: Kerala keyword matching ---
        if result.region != "KERALA":
            kerala_hits = [
                kw for kw in KERALA_KEYWORDS
                if (kw in combined_lower if " " in kw else re.search(r"\b" + re.escape(kw) + r"\b", combined_lower))
            ]
            if kerala_hits:
                matched.extend(kerala_hits)
                result.region = "KERALA"
                result.state = "Kerala"
                result.confidence = max(result.confidence, 0.80)

        # --- Step 4: Kerala gov / institutional keyword matching ---
        if result.region != "KERALA":
            gov_hits = [
                kw for kw in KERALA_GOV_KEYWORDS
                if (kw in combined_lower if " " in kw else re.search(r"\b" + re.escape(kw) + r"\b", combined_lower))
            ]
            if gov_hits:
                matched.extend(gov_hits)
                result.region = "KERALA"
                result.state = "Kerala"
                result.confidence = max(result.confidence, 0.88)

        # --- Step 5: India keyword matching (only if not already Kerala) ---
        if result.region == "GLOBAL":
            india_hits = [
                kw for kw in INDIA_KEYWORDS
                if (kw in combined_lower if " " in kw else re.search(r"\b" + re.escape(kw) + r"\b", combined_lower))
            ]
            if india_hits:
                matched.extend(india_hits[:5])
                result.region = "INDIA"
                result.confidence = max(result.confidence, 0.75)

        # --- Step 6: Honor source_region as a prior / tie-breaker ---
        if source_region:
            src = source_region.upper()
            if src in ("KERALA", "INDIA", "GLOBAL"):
                if result.region == "GLOBAL" and src != "GLOBAL":
                    # Source says India/Kerala but we found nothing — trust source
                    result.region = src
                    if src == "KERALA":
                        result.state = "Kerala"
                    result.confidence = max(result.confidence, 0.70)
                elif src == "KERALA" and result.region == "INDIA":
                    # Kerala source publishing India-tagged article → still Kerala
                    result.region = "KERALA"
                    result.state = "Kerala"
                    result.confidence = max(result.confidence, 0.80)

        result.matched_keywords = matched[:10]
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_district(self, text: str, matched: list[str]) -> str | None:
        """Return the first matched Kerala district (canonical name)."""
        m = self._district_re.search(text)
        if m:
            raw = m.group(1).lower()
            matched.append(raw)
            # Resolve alias
            if raw in DISTRICT_ALIASES:
                return DISTRICT_ALIASES[raw]
            # Return properly cased canonical name
            for district in KERALA_DISTRICTS:
                if district.lower() == raw:
                    return district
            return m.group(1).title()
        return None

    def _extract_city(self, text: str, matched: list[str]) -> str | None:
        """Return the first matched Kerala city."""
        m = self._city_re.search(text)
        if m:
            raw = m.group(1)
            matched.append(raw.lower())
            # Return canonical casing
            for city in KERALA_CITIES:
                if city.lower() == raw.lower():
                    return city
            return raw.title()
        return None

    def classify_batch(
        self,
        articles: list[dict],
        source_region: str | None = None,
    ) -> list[KeralaClassificationResult]:
        """Classify a batch of articles.

        Args:
            articles: list of dicts with 'title' and optional 'content' keys.
            source_region: default region from source definition.
        """
        return [
            self.classify(
                title=art.get("title", ""),
                content=art.get("content") or art.get("summary", ""),
                source_region=source_region,
            )
            for art in articles
        ]


_classifier_instance: KeralaClassifier | None = None


def get_kerala_classifier() -> KeralaClassifier:
    """Return a singleton instance of KeralaClassifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = KeralaClassifier()
    return _classifier_instance
