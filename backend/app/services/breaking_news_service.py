"""Breaking News Detection Service for NewsSense AI.

Identifies breaking news events by combining:
  - Source priority (high-priority Kerala/India sources)
  - Publication recency (last 2 hours)
  - Importance score threshold (>= 0.75)
  - Article velocity (rapid new coverage in short window)

Used by:
  - GET /news/breaking  (API endpoint)
  - Celery beat task    (detect-breaking-news every 5 min)
  - WebSocket notifier  (push to connected clients)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.event import Event
from app.models.source import Source

logger = logging.getLogger(__name__)

# Thresholds
BREAKING_WINDOW_HOURS = 2          # Articles published in last N hours
BREAKING_IMPORTANCE_MIN = 0.75     # Minimum importance score for an event
BREAKING_VELOCITY_ARTICLES = 3     # Min articles in a short window to flag velocity
BREAKING_VELOCITY_WINDOW_MIN = 30  # Velocity window in minutes


class BreakingNewsService:
    """Detects and serves breaking news articles and events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_breaking_articles(
        self,
        region: str | None = None,
        limit: int = 20,
        skip: int = 0,
    ) -> list[dict[str, Any]]:
        """Return breaking news articles (high-priority sources, last 2 hours).

        Args:
            region: Optional KERALA | INDIA | GLOBAL filter.
            limit:  Max articles to return.
            skip:   Pagination offset.
        """
        cutoff = datetime.now(UTC) - timedelta(hours=BREAKING_WINDOW_HOURS)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")

        stmt = (
            select(Article)
            .join(Source, Article.source_id == Source.id, isouter=True)
            .where(Source.priority == "high")
            .where(Article.created_at >= cutoff_str)
        )

        if region:
            stmt = stmt.where(Article.region == region.upper())

        stmt = stmt.order_by(Article.created_at.desc()).offset(skip).limit(limit)

        results = (await self.db.execute(stmt)).scalars().all()
        return [self._article_to_dict(a) for a in results]

    async def get_breaking_events(
        self,
        region: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return breaking news events (important, recently active).

        An event is "breaking" if:
          - importance_score >= BREAKING_IMPORTANCE_MIN, AND
          - status = 'active', AND
          - Created or updated in the last 2 hours
        """
        cutoff = datetime.now(UTC) - timedelta(hours=BREAKING_WINDOW_HOURS)

        stmt = (
            select(Event)
            .where(Event.importance_score >= BREAKING_IMPORTANCE_MIN)
            .where(Event.status == "active")
            .where(Event.is_active == True)  # noqa: E712
            .where(Event.created_at >= cutoff)
            .order_by(Event.importance_score.desc())
            .limit(limit)
        )

        results = (await self.db.execute(stmt)).scalars().all()
        return [self._event_to_dict(e) for e in results]

    async def detect_velocity_events(self) -> list[dict[str, Any]]:
        """Detect events gaining rapid new coverage (velocity spike).

        Returns events where article_count increased significantly in last 30 minutes.
        This is a heuristic — we check events that have many articles created recently.
        """
        velocity_cutoff = datetime.now(UTC) - timedelta(minutes=BREAKING_VELOCITY_WINDOW_MIN)

        # Find event IDs with >= BREAKING_VELOCITY_ARTICLES new articles recently
        from app.models.event import EventArticle  # type: ignore
        try:
            stmt = (
                select(EventArticle.event_id, func.count(EventArticle.article_id).label("recent_count"))
                .join(Article, EventArticle.article_id == Article.id)
                .where(Article.created_at >= velocity_cutoff)
                .group_by(EventArticle.event_id)
                .having(func.count(EventArticle.article_id) >= BREAKING_VELOCITY_ARTICLES)
            )
            rows = (await self.db.execute(stmt)).all()
            event_ids = [r.event_id for r in rows]

            if not event_ids:
                return []

            events_stmt = select(Event).where(Event.id.in_(event_ids))
            events = (await self.db.execute(events_stmt)).scalars().all()
            return [self._event_to_dict(e) for e in events]
        except Exception as exc:
            logger.debug(f"Velocity detection failed (EventArticle may not exist): {exc}")
            return []

    async def count_breaking(self, region: str | None = None) -> int:
        """Count current breaking news articles."""
        cutoff = datetime.now(UTC) - timedelta(hours=BREAKING_WINDOW_HOURS)
        cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")

        stmt = (
            select(func.count(Article.id))
            .join(Source, Article.source_id == Source.id, isouter=True)
            .where(Source.priority == "high")
            .where(Article.created_at >= cutoff_str)
        )
        if region:
            stmt = stmt.where(Article.region == region.upper())

        return (await self.db.execute(stmt)).scalar() or 0

    # ------------------------------------------------------------------
    # Serializers
    # ------------------------------------------------------------------

    def _article_to_dict(self, a: Article) -> dict[str, Any]:
        return {
            "id": str(a.id),
            "title": a.title,
            "slug": a.slug,
            "summary": a.summary or (a.content[:250] if a.content else ""),
            "source_name": a.source_name,
            "category": a.category_name,
            "region": a.region,
            "district": a.district,
            "city": a.city,
            "published_at": a.published_at,
            "url": a.url,
            "is_breaking": True,
        }

    def _event_to_dict(self, e: Event) -> dict[str, Any]:
        return {
            "id": str(e.id),
            "title": e.title,
            "slug": e.slug,
            "summary": e.summary,
            "category": e.category,
            "importance_score": e.importance_score,
            "article_count": e.article_count,
            "status": e.status,
            "is_breaking": True,
            "created_at": str(e.created_at) if e.created_at else None,
        }
