import time, sys
sys.path.insert(0, ".")

def test_imp(name, stmt):
    t0 = time.time()
    print(f"Executing: {stmt} ...", end="", flush=True)
    exec(stmt)
    print(f" OK ({round(time.time() - t0, 2)}s)", flush=True)

test_imp("uuid", "from uuid import uuid4")
test_imp("pytest", "import pytest")
test_imp("httpx", "from httpx import ASGITransport, AsyncClient")
test_imp("app.core.config", "from app.core.config import settings")
test_imp("app.db.session", "from app.db.session import async_session_factory")
test_imp("app.models.user", "from app.models.user import User")
test_imp("app.repositories.user_repository", "from app.repositories.user_repository import UserRepository")
test_imp("app.main", "from app.main import app")
print("All imports in auth flow OK!", flush=True)
