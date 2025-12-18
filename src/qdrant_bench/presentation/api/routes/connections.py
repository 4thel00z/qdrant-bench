from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_bench.presentation.api.dependencies import get_session
from qdrant_bench.infrastructure.persistence.models import Connection

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.get("", response_model=List[Connection])
async def list_connections(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Connection))
    return result.all()

@router.post("", response_model=Connection, status_code=201)
async def create_connection(connection: Connection, session: AsyncSession = Depends(get_session)):
    session.add(connection)
    await session.commit()
    await session.refresh(connection)
    return connection

