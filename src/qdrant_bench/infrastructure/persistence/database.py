import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Default to a local postgres container if not set


def create_db_engine(url: str = None) -> AsyncEngine:
    return create_async_engine(url or os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qdrant_bench"), echo=True, future=True)


async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # For dev only
        await conn.run_sync(SQLModel.metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
