"""
Database package initialization.
"""
from .base_class import Base  # noqa
from .init_db import (
    init_db,
    get_db,
    get_async_db,
    SessionLocal,
    AsyncSessionLocal,
    sync_engine,
    async_engine,
)

# Alias sync_engine to engine for backward compatibility
engine = sync_engine

__all__ = [
    'init_db',
    'Base',
    'get_db',
    'get_async_db',
    'SessionLocal',
    'AsyncSessionLocal',
    'sync_engine',
    'async_engine',
    'engine',
]
