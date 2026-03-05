"""
Async SQLAlchemy engine, session factory, and dependency injection helper.

Usage in FastAPI endpoints:
    from src.storage.database import get_db
    async def my_endpoint(db: AsyncSession = Depends(get_db)): ...

Usage elsewhere:
    async with async_session() as db:
        result = await db.execute(select(User))
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings
from src.storage.models.base_model import Base

# A single engine is shared across the process lifetime.
# echo=True in dev is helpful for seeing generated SQL.
engine = create_async_engine(
    settings.database_url,
    echo=(settings.app_env == "development"),
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """
    Create all tables. Call once at startup (in main.py lifespan).
    In production, replace this with Alembic migrations:
        alembic upgrade head
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
