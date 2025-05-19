"""
Database session management.
"""
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session as SyncSession
from sqlalchemy.pool import NullPool

from app.core.config import settings
from .base_class import Base

# Create async engine for async operations
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Create sync engine for sync operations (Alembic, etc.)
sync_engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=100,
)

# Alias for backward compatibility
engine = sync_engine

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Dependency to get async DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions.
    Handles session lifecycle including rollback on exceptions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Dependency to get sync DB session
def get_sync_db() -> Generator[SyncSession, None, None]:
    """
    Dependency function that yields sync db sessions.
    Used for operations that require a sync session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
