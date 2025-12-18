from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_bench.presentation.api.dependencies import get_session
from qdrant_bench.infrastructure.persistence.models import Dataset

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("", response_model=List[Dataset])
async def list_datasets(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(Dataset))
    return result.all()

@router.post("", response_model=Dataset, status_code=201)
async def create_dataset(dataset: Dataset, session: AsyncSession = Depends(get_session)):
    session.add(dataset)
    await session.commit()
    await session.refresh(dataset)
    return dataset

