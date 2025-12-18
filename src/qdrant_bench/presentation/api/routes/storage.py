from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_bench.presentation.api.dependencies import get_session
from qdrant_bench.infrastructure.persistence.models import ObjectStorage

router = APIRouter(prefix="/storage", tags=["Object Storage"])

@router.get("", response_model=List[ObjectStorage])
async def list_storage(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(ObjectStorage))
    return result.all()

@router.post("", response_model=ObjectStorage, status_code=201)
async def create_storage(storage: ObjectStorage, session: AsyncSession = Depends(get_session)):
    session.add(storage)
    await session.commit()
    await session.refresh(storage)
    return storage

