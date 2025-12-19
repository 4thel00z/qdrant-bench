from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from qdrant_bench.application.usecases.storage.manage import (
    CreateStorageCommand,
    CreateStorageUseCase,
    ListStorageUseCase,
)
from qdrant_bench.presentation.api.dependencies import get_create_storage_usecase, get_list_storage_usecase


class CreateStorageRequest(BaseModel):
    bucket: str
    region: str
    endpoint_url: str
    access_key: str
    secret_key: str


class StorageResponse(BaseModel):
    id: UUID
    bucket: str
    region: str
    endpoint_url: str
    access_key: str
    # Explicitly exclude secret_key from response for security if desired, but for now mirroring domain
    # secret_key: str


router = APIRouter(prefix="/storage", tags=["Object Storage"])


@router.get("")
async def list_storage(use_case: ListStorageUseCase = Depends(get_list_storage_usecase)):
    storage_list = await use_case.execute()
    return [
        StorageResponse(
            id=s.id,
            bucket=s.bucket,
            region=s.region,
            endpoint_url=s.endpoint_url,
            access_key=s.access_key,
        )
        for s in storage_list
    ]


@router.post("", status_code=201)
async def create_storage(
    request: CreateStorageRequest, use_case: CreateStorageUseCase = Depends(get_create_storage_usecase)
):
    command = CreateStorageCommand(
        bucket=request.bucket,
        region=request.region,
        endpoint_url=request.endpoint_url,
        access_key=request.access_key,
        secret_key=request.secret_key,
    )
    storage = await use_case.execute(command)
    return StorageResponse(
        id=storage.id,
        bucket=storage.bucket,
        region=storage.region,
        endpoint_url=storage.endpoint_url,
        access_key=storage.access_key,
    )
