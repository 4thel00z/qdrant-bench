import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Default to a local postgres container if not set
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qdrant_bench")

def create_db_engine(url: str = DATABASE_URL) -> AsyncEngine:
    return create_async_engine(url, echo=True, future=True)

async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all) # For dev only
        await conn.run_sync(SQLModel.metadata.create_all)

def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
