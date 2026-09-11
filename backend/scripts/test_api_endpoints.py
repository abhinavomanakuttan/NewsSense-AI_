import asyncio
import sys
sys.path.insert(0, ".")

from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.session import async_session_factory
from app.models.article import Article
from app.models.source import Source
from uuid import uuid4

async def run_api_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Test /api/v1/news
        r = await client.get("/api/v1/news?limit=5")
        print(f"GET /api/v1/news: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        print(f"  Articles returned: {len(data.get('articles', []))}, total={data.get('total')}", flush=True)

        # 2. Test /api/v1/news/kerala
        r = await client.get("/api/v1/news/kerala?limit=5")
        print(f"GET /api/v1/news/kerala: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        print(f"  Kerala news returned: {len(data.get('articles', []))}", flush=True)

        # 3. Test /api/v1/news/india
        r = await client.get("/api/v1/news/india?limit=5")
        print(f"GET /api/v1/news/india: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

        # 4. Test /api/v1/news/global
        r = await client.get("/api/v1/news/global?limit=5")
        print(f"GET /api/v1/news/global: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

        # 5. Test /api/v1/news/breaking
        r = await client.get("/api/v1/news/breaking?limit=5")
        print(f"GET /api/v1/news/breaking: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

        # 6. Test /api/v1/news/stats/regions
        r = await client.get("/api/v1/news/stats/regions")
        print(f"GET /api/v1/news/stats/regions: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        print(f"  Regional breakdown: {r.json()}", flush=True)

        # 7. Test /api/v1/sources
        r = await client.get("/api/v1/sources")
        print(f"GET /api/v1/sources: status={r.status_code}", flush=True)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    print("\nALL API ENDPOINTS VERIFIED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    asyncio.run(run_api_tests())
