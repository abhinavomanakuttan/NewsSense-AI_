"""Multi-Factor News Importance Scorer for NewsSense AI.

Replaces the placeholder `credibility_score or 0.5` used in the deduplication
service with a principled, multi-signal importance formula.

Signals used:
  1. Source reliability score (0.0–1.0, from sources.yaml)
  2. Source priority weight (high=1.0, normal=0.7, low=0.4)
  3. Independent source count (corroboration signal)
  4. Category weight (disasters, politics, public safety score higher)
  5. Region boost (Kerala/India boost for primary users)
  6. Recency factor (breaking events score higher)
  7. Article count in event (more coverage = more important)

Output: float in [0.0, 1.0]
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ImportanceScoreResult:
    score: float
    region_boost: float
    is_breaking: bool
    urgency_tier: str  # CRITICAL | HIGH | MEDIUM | LOW


# ---------------------------------------------------------------------------
# Category weights — how intrinsically important each category is
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS: dict[str, float] = {
    # Highest: Direct public impact
    "disaster": 1.00,
    "weather": 0.95,
    "flood": 1.00,
    "public_safety": 1.00,
    "crime": 0.85,
    "health": 0.88,
    "politics": 0.90,
    "elections": 0.95,
    "india_elections": 0.95,
    "kerala_news": 0.92,
    "government": 0.85,
    "government_india": 0.88,
    "india_politics": 0.88,
    "india_defence": 0.85,
    "india_judiciary": 0.83,
    "india_economy": 0.82,
    # Medium: General importance
    "world_news": 0.80,
    "business": 0.78,
    "economy": 0.78,
    "science": 0.75,
    "technology": 0.72,
    "environment": 0.75,
    "education": 0.70,
    # Lower: Lifestyle / entertainment
    "sports": 0.65,
    "entertainment": 0.55,
    "lifestyle": 0.50,
}

DEFAULT_CATEGORY_WEIGHT = 0.65

# Priority weights
PRIORITY_WEIGHTS: dict[str, float] = {
    "high": 1.00,
    "normal": 0.70,
    "low": 0.40,
}

# Region boost multipliers (applied on top of base score for regional relevance)
REGION_BOOST: dict[str, float] = {
    "KERALA": 1.20,   # Primary focus
    "INDIA": 1.05,    # Primary focus
    "GLOBAL": 0.85,   # Secondary
}


class ImportanceScorer:
    """Compute a normalized importance score for a news event."""

    def score(
        self,
        source_reliability: float = 0.5,
        source_priority: str = "normal",
        category: str | None = None,
        region: str | None = None,
        independent_source_count: int = 1,
        article_count: int = 1,
        published_at: str | None = None,
        age_hours: float | None = None,
        extra_signals: dict[str, Any] | None = None,
    ) -> float:
        """Compute the importance score.

        Args:
            source_reliability: Source credibility (0.0–1.0).
            source_priority: 'high', 'normal', or 'low'.
            category: Article/event category string.
            region: 'KERALA', 'INDIA', or 'GLOBAL'.
            independent_source_count: Number of independent sources covering this event.
            article_count: Total articles in the event cluster.
            published_at: ISO timestamp of article publication.
            age_hours: Optional explicit age in hours for recency decay.
            extra_signals: Optional dict of additional signals for future extensions.

        Returns:
            float: Importance score in [0.0, 1.0].
        """
        try:
            return self._compute(
                source_reliability=source_reliability,
                source_priority=source_priority,
                category=category,
                region=region,
                independent_source_count=independent_source_count,
                article_count=article_count,
                published_at=published_at,
                age_hours=age_hours,
            )
        except Exception as exc:
            logger.warning(f"ImportanceScorer failed, using default: {exc}")
            return 0.50

    def calculate(
        self,
        category: str | None = None,
        source_priority: str = "normal",
        source_reliability: float = 0.5,
        independent_source_count: int = 1,
        article_count: int = 1,
        region: str | None = None,
        age_hours: float | None = None,
        published_at: str | None = None,
    ) -> ImportanceScoreResult:
        """Calculate detailed importance metrics including tier and breaking flag."""
        score_val = self.score(
            source_reliability=source_reliability,
            source_priority=source_priority,
            category=category,
            region=region,
            independent_source_count=independent_source_count,
            article_count=article_count,
            published_at=published_at,
            age_hours=age_hours,
        )
        boost = REGION_BOOST.get((region or "GLOBAL").upper(), 1.0)
        is_breaking = score_val >= 0.75 and (age_hours is None or age_hours <= 2.0)

        if score_val >= 0.85:
            urgency = "CRITICAL"
        elif score_val >= 0.70:
            urgency = "HIGH"
        elif score_val >= 0.50:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        return ImportanceScoreResult(
            score=score_val,
            region_boost=boost,
            is_breaking=is_breaking,
            urgency_tier=urgency,
        )

    def _compute(
        self,
        source_reliability: float,
        source_priority: str,
        category: str | None,
        region: str | None,
        independent_source_count: int,
        article_count: int,
        published_at: str | None,
        age_hours: float | None = None,
    ) -> float:
        # 1. Source credibility signal (0–1)
        reliability = max(0.0, min(1.0, float(source_reliability or 0.5)))

        # 2. Source priority weight
        priority_w = PRIORITY_WEIGHTS.get((source_priority or "normal").lower(), 0.70)

        # 3. Category weight
        cat_lower = (category or "").lower().replace(" ", "_")
        cat_weight = CATEGORY_WEIGHTS.get(cat_lower, None)
        if cat_weight is None:
            for key in CATEGORY_WEIGHTS:
                if key in cat_lower or cat_lower in key:
                    cat_weight = CATEGORY_WEIGHTS[key]
                    break
        cat_weight = cat_weight or DEFAULT_CATEGORY_WEIGHT

        # 4. Corroboration signal
        corroboration = min(1.0, 0.5 + 0.25 * math.log1p(independent_source_count))

        # 5. Coverage breadth
        coverage = min(1.0, 0.3 + 0.07 * math.log1p(min(article_count, 20)))

        # 6. Recency factor
        recency = 1.0
        if age_hours is not None:
            recency = math.exp(-0.029 * max(0.0, age_hours))
        elif published_at:
            try:
                now = datetime.now(UTC)
                pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                age = max(0.0, (now - pub).total_seconds() / 3600)
                recency = math.exp(-0.029 * age)
            except Exception:
                pass

        # --- Combine signals ---
        # Weighted harmonic blend prioritising reliability + priority + category
        base_score = (
            0.25 * reliability
            + 0.20 * priority_w
            + 0.20 * cat_weight
            + 0.15 * corroboration
            + 0.10 * coverage
            + 0.10 * recency
        )

        # 7. Region boost (multiplicative, applied last)
        region_mult = REGION_BOOST.get((region or "GLOBAL").upper(), 1.0)
        final_score = min(1.0, base_score * region_mult)

        return round(final_score, 4)

    def score_from_article(self, article: Any, source: Any | None = None) -> float:
        """Convenience wrapper that accepts ORM Article and Source objects."""
        return self.score(
            source_reliability=getattr(source, "reliability_score", 0.5) if source else 0.5,
            source_priority=getattr(source, "priority", "normal") if source else "normal",
            category=getattr(article, "category_name", None),
            region=getattr(article, "region", "GLOBAL"),
            independent_source_count=1,
            article_count=1,
            published_at=getattr(article, "published_at", None),
        )


# Module-level singleton
_importance_scorer: ImportanceScorer | None = None


def get_importance_scorer() -> ImportanceScorer:
    global _importance_scorer
    if _importance_scorer is None:
        _importance_scorer = ImportanceScorer()
    return _importance_scorer
