import os

# --- config crash bo'lmasligi uchun env'larni app importidan OLDIN o'rnatamiz ---
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/testdb")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("EMAIL_TOKEN_EXPIRE_MIN", "3")
os.environ.setdefault("UNVERIFIED_USER_TTL_MIN", "1")
os.environ.setdefault("CLEANUP_INTERVAL_SECONDS", "60")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base
from app.db import get_db


# --- Har bir test uchun toza in-memory SQLite baza + client ---
@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    # jadvallarni yaratamiz
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


USER = {
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "secret123",
}


# 1) Muvaffaqiyatli ro'yxatdan o'tish
@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/auth/register", json=USER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == USER["email"]
    assert data["username"] == USER["username"]
    assert data["is_verified"] is False


# 2) Muvaffaqiyatsiz ro'yxatdan o'tish (dublikat email/username)
@pytest.mark.asyncio
async def test_register_duplicate(client):
    r1 = await client.post("/auth/register", json=USER)
    assert r1.status_code == 201

    r2 = await client.post("/auth/register", json=USER)  # xuddi shu email/username
    assert r2.status_code == 400


# 3) Muvaffaqiyatli login + himoyalangan endpoint (to'g'ri va noto'g'ri token)
@pytest.mark.asyncio
async def test_login_and_protected_endpoint(client):
    await client.post("/auth/register", json=USER)

    # login
    login = await client.post(
        "/auth/login",
        json={"username_or_email": USER["username"], "password": USER["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    # to'g'ri token bilan -> 200
    ok = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
    assert ok.json()["username"] == USER["username"]

    # noto'g'ri token bilan -> 401
    bad = await client.get("/auth/me", headers={"Authorization": "Bearer notogri.token.xxx"})
    assert bad.status_code == 401
