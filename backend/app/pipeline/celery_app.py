from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "newssense",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",  # IST for Kerala/India focus
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    beat_schedule={
        # --- Breaking news: high-priority sources every 2 minutes ---
        # Covers: Kerala (Mathrubhumi, Manorama, The Hindu Kerala, NDTV Kerala)
        #         India (The Hindu, NDTV, TOI, PIB, IMD)
        "fetch-high-priority-feeds": {
            "task": "app.pipeline.tasks.feed_fetcher.fetch_high_priority_feeds",
            "schedule": 120.0,  # 2 minutes
            "options": {"queue": "high_priority"},
        },
        # --- Standard news: normal-priority sources every 10 minutes ---
        "fetch-normal-priority-feeds": {
            "task": "app.pipeline.tasks.feed_fetcher.fetch_normal_priority_feeds",
            "schedule": 600.0,  # 10 minutes
            "options": {"queue": "default"},
        },
        # --- Background: low-priority sources every 30 minutes ---
        "fetch-low-priority-feeds": {
            "task": "app.pipeline.tasks.feed_fetcher.fetch_low_priority_feeds",
            "schedule": 1800.0,  # 30 minutes
            "options": {"queue": "low_priority"},
        },
        # --- Full fetch fallback (catches any missed sources) every 15 min ---
        "fetch-all-feeds": {
            "task": "app.pipeline.tasks.feed_fetcher.fetch_all_feeds",
            "schedule": 900.0,
        },
        # --- Trending / recommendation update every 30 minutes ---
        "update-trending": {
            "task": "app.pipeline.tasks.recommendation_updater.update_trending",
            "schedule": 1800.0,
        },
        # --- Breaking news detector: runs every 5 minutes ---
        "detect-breaking-news": {
            "task": "app.pipeline.tasks.feed_fetcher.detect_breaking_news",
            "schedule": 300.0,  # 5 minutes
        },
    },
)

# Import task modules so Celery discovers their @task decorators.
import app.pipeline.tasks.enrichment  # noqa: E402, F401
import app.pipeline.tasks.feed_fetcher  # noqa: E402, F401
import app.pipeline.tasks.indexer  # noqa: E402, F401
import app.pipeline.tasks.ner  # noqa: E402, F401
import app.pipeline.tasks.orchestration  # noqa: E402, F401
import app.pipeline.tasks.recommendation_updater  # noqa: E402, F401
import app.pipeline.tasks.sentiment  # noqa: E402, F401
