import asyncio
import sys
sys.path.insert(0, ".")

from app.db.session import async_session_factory
from app.models.article import Article
from app.ai.kerala_classifier import get_kerala_classifier
from sqlalchemy import select

async def classify_all():
    classifier = get_kerala_classifier()
    async with async_session_factory() as session:
        result = await session.execute(select(Article))
        articles = result.scalars().all()
        print(f"Classifying {len(articles)} existing articles...")
        updated = 0
        for a in articles:
            res = classifier.classify(title=a.title, content=a.content or a.summary or "")
            a.region = res.region
            a.state = res.state
            a.district = res.district
            a.city = res.city
            a.locality = res.locality
            updated += 1
            print(f"  [{res.region}] {a.title[:60]}... -> district={res.district}, city={res.city}")

        await session.commit()
        print(f"\nSuccessfully classified {updated} articles!")

if __name__ == "__main__":
    asyncio.run(classify_all())
