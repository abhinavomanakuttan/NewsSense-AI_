"""FastAPI router for Multi-Faceted News Feed — NewsSense AI.

Regional endpoints:
  GET /news               — general feed with optional filters
  GET /news/kerala        — Kerala-focused news (region=KERALA)
  GET /news/india         — India national news (region=INDIA)
  GET /news/global        — Global / international news (region=GLOBAL)
  GET /news/breaking      — Breaking news (high-priority sources, last 2 hours)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.article import Article
from app.models.source import Source
from app.schemas.article import ArticleListResponse
from app.schemas.news import NewsFeedResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/news", tags=["News"])


# ---------------------------------------------------------------------------
# Shared query helper
# ---------------------------------------------------------------------------

async def _fetch_news(
    db: AsyncSession,
    skip: int,
    limit: int,
    region: str | None = None,
    category: str | None = None,
    country: str | None = None,
    language: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    source: str | None = None,
    topic: str | None = None,
    importance: float | None = None,
    breaking_only: bool = False,
) -> NewsFeedResponse:
    """Central query builder for all news endpoints."""
    stmt = select(Article)
    count_stmt = select(func.count(Article.id))

    filters_applied: dict[str, Any] = {}

    # --- Region filter ---
    if region:
        region_upper = region.upper()
        stmt = stmt.where(Article.region == region_upper)
        count_stmt = count_stmt.where(Article.region == region_upper)
        filters_applied["region"] = region_upper

    # --- Breaking news: articles from high-priority sources, last 2 hours ---
    if breaking_only:
        two_hours_ago = (datetime.now(UTC) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        stmt = (
            stmt.join(Source, Article.source_id == Source.id, isouter=True)
            .where(Source.priority == "high")
            .where(Article.created_at >= two_hours_ago)
        )
        count_stmt = (
            count_stmt.join(Source, Article.source_id == Source.id, isouter=True)
            .where(Source.priority == "high")
            .where(Article.created_at >= two_hours_ago)
        )
        filters_applied["breaking"] = True

    if category:
        stmt = stmt.where(Article.category_name.ilike(f"%{category}%"))
        count_stmt = count_stmt.where(Article.category_name.ilike(f"%{category}%"))
        filters_applied["category"] = category

    if country:
        stmt = stmt.where(Article.country == country.upper())
        count_stmt = count_stmt.where(Article.country == country.upper())
        filters_applied["country"] = country

    if language:
        stmt = stmt.where(Article.language == language.lower())
        count_stmt = count_stmt.where(Article.language == language.lower())
        filters_applied["language"] = language

    if source:
        stmt = stmt.where(Article.source_name.ilike(f"%{source}%"))
        count_stmt = count_stmt.where(Article.source_name.ilike(f"%{source}%"))
        filters_applied["source"] = source

    if topic:
        topic_filter = or_(
            Article.title.ilike(f"%{topic}%"),
            Article.keywords.ilike(f"%{topic}%"),
            Article.entities.ilike(f"%{topic}%"),
        )
        stmt = stmt.where(topic_filter)
        count_stmt = count_stmt.where(topic_filter)
        filters_applied["topic"] = topic

    if date_from:
        stmt = stmt.where(Article.published_at >= date_from)
        count_stmt = count_stmt.where(Article.published_at >= date_from)
        filters_applied["date_from"] = date_from

    if date_to:
        stmt = stmt.where(Article.published_at <= date_to)
        count_stmt = count_stmt.where(Article.published_at <= date_to)
        filters_applied["date_to"] = date_to

    stmt = stmt.order_by(Article.created_at.desc()).offset(skip).limit(limit)

    total = (await db.execute(count_stmt)).scalar() or 0
    articles = (await db.execute(stmt)).scalars().all()

    article_responses = [
        ArticleListResponse(
            id=a.id,
            title=a.title,
            slug=a.slug,
            summary=a.summary or (a.content[:300] if a.content else ""),
            source_name=a.source_name,
            category_name=a.category_name,
            image_url=None,
            published_at=a.published_at or str(a.created_at),
            sentiment=a.sentiment,
            credibility_score=a.sentiment_score,
            tags=[],
        )
        for a in articles
    ]

    return NewsFeedResponse(
        total=total,
        skip=skip,
        limit=limit,
        articles=article_responses,
        applied_filters=filters_applied,
    )


# ---------------------------------------------------------------------------
# Routes — order matters: specific paths before parameterised ones
# ---------------------------------------------------------------------------

@router.get("/breaking", response_model=NewsFeedResponse, summary="Breaking News")
async def get_breaking_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    region: str | None = Query(None, description="Filter breaking news by region (KERALA/INDIA/GLOBAL)"),
    db: AsyncSession = Depends(get_db),
):
    """Breaking news: high-priority sources published in the last 2 hours.
    Covers Kerala, India, and global breaking stories.
    """
    return await _fetch_news(
        db=db,
        skip=skip,
        limit=limit,
        region=region,
        breaking_only=True,
    )


@router.get("/kerala", response_model=NewsFeedResponse, summary="Kerala News Feed")
async def get_kerala_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    district: str | None = Query(None, description="Filter by Kerala district (e.g. Ernakulam, Kozhikode)"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    source: str | None = Query(None),
    topic: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Kerala-focused news feed. Returns articles with region=KERALA."""
    resp = await _fetch_news(
        db=db,
        skip=skip,
        limit=limit,
        region="KERALA",
        category=category,
        date_from=date_from,
        date_to=date_to,
        source=source,
        topic=topic or district,
    )
    if district:
        resp.applied_filters["district"] = district
    return resp


@router.get("/india", response_model=NewsFeedResponse, summary="India National News Feed")
async def get_india_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    state: str | None = Query(None, description="Filter by Indian state (e.g. Kerala, Maharashtra)"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    source: str | None = Query(None),
    topic: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """India national news feed. Returns articles from India + Kerala (regional subset of India)."""
    stmt = select(Article).where(
        or_(Article.region == "INDIA", Article.region == "KERALA")
    )
    count_stmt = select(func.count(Article.id)).where(
        or_(Article.region == "INDIA", Article.region == "KERALA")
    )

    filters_applied: dict[str, Any] = {"region": "INDIA"}

    if state:
        stmt = stmt.where(Article.state.ilike(f"%{state}%"))
        count_stmt = count_stmt.where(Article.state.ilike(f"%{state}%"))
        filters_applied["state"] = state

    if category:
        stmt = stmt.where(Article.category_name.ilike(f"%{category}%"))
        count_stmt = count_stmt.where(Article.category_name.ilike(f"%{category}%"))
        filters_applied["category"] = category

    if topic:
        topic_filter = or_(
            Article.title.ilike(f"%{topic}%"),
            Article.keywords.ilike(f"%{topic}%"),
        )
        stmt = stmt.where(topic_filter)
        count_stmt = count_stmt.where(topic_filter)
        filters_applied["topic"] = topic

    if source:
        stmt = stmt.where(Article.source_name.ilike(f"%{source}%"))
        count_stmt = count_stmt.where(Article.source_name.ilike(f"%{source}%"))
        filters_applied["source"] = source

    if date_from:
        stmt = stmt.where(Article.published_at >= date_from)
        count_stmt = count_stmt.where(Article.published_at >= date_from)
        filters_applied["date_from"] = date_from

    if date_to:
        stmt = stmt.where(Article.published_at <= date_to)
        count_stmt = count_stmt.where(Article.published_at <= date_to)
        filters_applied["date_to"] = date_to

    stmt = stmt.order_by(Article.created_at.desc()).offset(skip).limit(limit)

    total = (await db.execute(count_stmt)).scalar() or 0
    articles = (await db.execute(stmt)).scalars().all()

    article_responses = [
        ArticleListResponse(
            id=a.id,
            title=a.title,
            slug=a.slug,
            summary=a.summary or (a.content[:300] if a.content else ""),
            source_name=a.source_name,
            category_name=a.category_name,
            image_url=None,
            published_at=a.published_at or str(a.created_at),
            sentiment=a.sentiment,
            credibility_score=a.sentiment_score,
            tags=[],
        )
        for a in articles
    ]

    return NewsFeedResponse(
        total=total,
        skip=skip,
        limit=limit,
        articles=article_responses,
        applied_filters=filters_applied,
    )


@router.get("/global", response_model=NewsFeedResponse, summary="Global News Feed")
async def get_global_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    country: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    source: str | None = Query(None),
    topic: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Global / international news feed. Returns articles with region=GLOBAL."""
    return await _fetch_news(
        db=db,
        skip=skip,
        limit=limit,
        region="GLOBAL",
        category=category,
        country=country,
        date_from=date_from,
        date_to=date_to,
        source=source,
        topic=topic,
    )


@router.get("", response_model=NewsFeedResponse, summary="General News Feed")
async def get_news_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    region: str | None = Query(None, description="Filter by region: KERALA, INDIA, or GLOBAL"),
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by ISO country code (IN, US, etc.)"),
    language: str | None = Query(None, description="Filter by language (en, ml, hi, etc.)"),
    date_from: str | None = Query(None, description="Filter published after (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="Filter published before (YYYY-MM-DD)"),
    source: str | None = Query(None, description="Filter by source name"),
    topic: str | None = Query(None, description="Filter by topic keyword"),
    importance: float | None = Query(None, description="Minimum importance score (0.0-1.0)"),
    db: AsyncSession = Depends(get_db),
):
    """General news feed supporting full filtering: region, category, country, language, date, source, topic."""
    return await _fetch_news(
        db=db,
        skip=skip,
        limit=limit,
        region=region,
        category=category,
        country=country,
        language=language,
        date_from=date_from,
        date_to=date_to,
        source=source,
        topic=topic,
        importance=importance,
    )


@router.get("/stats/regions", summary="Regional News Distribution Stats")
async def get_regional_stats(db: AsyncSession = Depends(get_db)):
    """Return count of articles per region (Kerala, India, Global)."""
    stmt = select(Article.region, func.count(Article.id)).group_by(Article.region)
    result = await db.execute(stmt)
    counts = {r or "UNCLASSIFIED": c for r, c in result.all()}
    return {
        "kerala": counts.get("KERALA", 0),
        "india": counts.get("INDIA", 0),
        "global": counts.get("GLOBAL", 0),
        "unclassified": counts.get("UNCLASSIFIED", 0),
        "total": sum(counts.values()),
    }
