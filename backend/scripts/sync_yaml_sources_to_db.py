import asyncio
import sys
sys.path.insert(0, ".")

from app.db.session import async_session_factory
from app.models.source import Source
from app.pipeline.config.loader import get_config_loader
from sqlalchemy import select

async def sync_sources():
    loader = get_config_loader()
    all_defs = loader.get_all_sources()
    print(f"Loaded {len(all_defs)} source definitions from sources.yaml", flush=True)

    async with async_session_factory() as session:
        # Fetch existing sources by name and url
        res = await session.execute(select(Source))
        existing_list = list(res.scalars().all())
        existing_by_name = {s.name: s for s in existing_list}
        seen_urls = {s.url for s in existing_list if s.url}
        print(f"Existing sources in DB: {len(existing_list)}", flush=True)

        created = 0
        updated = 0

        for s_def in all_defs:
            if s_def.name in existing_by_name:
                # Update existing source with region, priority, reliability
                s = existing_by_name[s_def.name]
                s.region = s_def.region
                s.priority = s_def.priority
                s.category = s_def.category
                s.reliability_score = s_def.reliability_score
                s.reputation_score = s_def.reliability_score
                s.fetch_interval_minutes = s_def.fetch_interval_minutes
                s.rate_limit = s_def.rate_limit
                if s_def.feed_url:
                    s.feed_url = s_def.feed_url
                if s_def.domain:
                    s.domain = s_def.domain
                updated += 1
            else:
                candidate_url = s_def.feed_url or s_def.url
                if candidate_url in seen_urls:
                    candidate_url = f"{candidate_url}#{s_def.category}"
                if candidate_url in seen_urls:
                    print(f"  Skipping duplicate URL: {candidate_url} ({s_def.name})")
                    continue
                seen_urls.add(candidate_url)

                new_s = Source(
                    name=s_def.name,
                    url=candidate_url,
                    domain=s_def.domain or "",
                    feed_url=s_def.feed_url or "",
                    api_endpoint=s_def.api_endpoint or "",
                    source_type=s_def.source_type or "rss",
                    language=s_def.language or "en",
                    country=s_def.country or "",
                    category=s_def.category or "",
                    region=s_def.region or "GLOBAL",
                    priority=s_def.priority or "normal",
                    reliability_score=s_def.reliability_score or 0.5,
                    reputation_score=s_def.reliability_score or 0.5,
                    rate_limit=s_def.rate_limit or 60,
                    fetch_interval_minutes=s_def.fetch_interval_minutes or 15,
                    is_active=s_def.active,
                )
                session.add(new_s)
                created += 1

        await session.commit()
        print(f"Sources sync complete: {created} created, {updated} updated.", flush=True)

if __name__ == "__main__":
    asyncio.run(sync_sources())
