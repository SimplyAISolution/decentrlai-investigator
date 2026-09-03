from __future__ import annotations
import os
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from .base import Base

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/decentrlai"

def get_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL
    return create_async_engine(
        url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )

def get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_models(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
