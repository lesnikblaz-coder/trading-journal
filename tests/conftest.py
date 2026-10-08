import pytest
import pytest_asyncio
import httpx

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import AsyncMock

from app import dependencies as dep
from app.main import app
from app.core.config import settings
from app.database.base import Base
from app.ai.clients.gemini_client import GeminiClient
from app.database.models.user import User
from app.core.security import get_hash


# ==========================
# TEST DATABASE
# ==========================
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    test_database_url = settings.test_database_url

    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL environment variable not found.")

    engine = create_async_engine(
        test_database_url,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ==========================
# DATABASE SESSION
# ==========================
@pytest_asyncio.fixture
async def db_session(test_engine):
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
    )

    session = session_factory()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

# ==========================
# GEMINI MOCK
# ==========================
@pytest.fixture
def mock_gemini_client():
    return AsyncMock(spec=GeminiClient)


# ==========================
# FASTAPI DEPENDENCY OVERRIDES
# ==========================
@pytest_asyncio.fixture
async def client(db_session, mock_gemini_client):
    async def override_get_session():
        yield db_session

    async def disable_rate_limit() -> None:
        return None

    async def override_gemini_client():
        return mock_gemini_client

    app.dependency_overrides[dep._get_session] = override_get_session

    app.dependency_overrides[dep._rate_limit_login] = disable_rate_limit
    app.dependency_overrides[dep._rate_limit_authenticated] = disable_rate_limit
    app.dependency_overrides[dep._rate_limit_ai] = disable_rate_limit

    app.dependency_overrides[dep._get_gemini_client] = override_gemini_client

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


# ==========================
# TEST USER
# ==========================
@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_pw=get_hash("password123")
    )

    db_session.add(user)
    await db_session.flush()

    return user

@pytest_asyncio.fixture
async def test_user_b(db_session):
    user = User(
        email="test_b@example.com",
        hashed_pw=get_hash("password123")
    )

    db_session.add(user)
    await db_session.flush()

    return user