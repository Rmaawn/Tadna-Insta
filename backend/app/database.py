"""Async database layer (SQLAlchemy 2.0 + SQLite).

The engine is created from ``settings.database_url``. SQLite is the default so
the app runs with zero external infrastructure, but the URL can be swapped for
Postgres (``postgresql+asyncpg://...``) without touching the rest of the code.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Create all tables. Called on application startup."""
    # Import models so they are registered on ``Base.metadata``.
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a database session."""
    async with SessionLocal() as session:
        yield session
