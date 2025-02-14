import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db import get_db
from app.database.models import Base

# Test database URL
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine for tests
engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator:
    """Create tables before test and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session for tests."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """Get test client with overridden dependencies."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
async def test_word(db_session: AsyncSession):
    """Create a test word."""
    from app.database.models import Word
    word = Word(
        japanese="テスト",
        romaji="tesuto",
        english="test"
    )
    db_session.add(word)
    await db_session.commit()
    await db_session.refresh(word)
    return word

@pytest.fixture
async def test_group(db_session: AsyncSession):
    """Create a test group."""
    from app.database.models import Group
    group = Group(name="Test Group")
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    return group

@pytest.fixture
async def test_study_activity(db_session: AsyncSession):
    """Create a test study activity."""
    from app.database.models import StudyActivity
    activity = StudyActivity(
        name="Test Activity",
        thumbnail_url="https://example.com/test.jpg",
        description="Test description"
    )
    db_session.add(activity)
    await db_session.commit()
    await db_session.refresh(activity)
    return activity 