from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from qdrant_bench.application.usecases.datasets.manage import (
    CreateDatasetCommand,
    CreateDatasetUseCase,
    ListDatasetsUseCase,
)
from qdrant_bench.presentation.api.dependencies import get_create_dataset_usecase, get_list_datasets_usecase


class CreateDatasetRequest(BaseModel):
    name: str
    source_uri: str
    schema_config: dict[str, Any]

class DatasetResponse(BaseModel):
    id: UUID
    name: str
    source_uri: str
    schema_config: dict[str, Any]

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("")
async def list_datasets(
    use_case: ListDatasetsUseCase = Depends(get_list_datasets_usecase)
):
    datasets = await use_case.execute()
    return [
        DatasetResponse(
            id=d.id, name=d.name, source_uri=d.source_uri, schema_config=d.schema_config
        ) for d in datasets
    ]

@router.post("", status_code=201)
async def create_dataset(
    request: CreateDatasetRequest,
    use_case: CreateDatasetUseCase = Depends(get_create_dataset_usecase)
):
    command = CreateDatasetCommand(
        name=request.name,
        source_uri=request.source_uri,
        schema_config=request.schema_config
    )
    dataset = await use_case.execute(command)
    return DatasetResponse(
        id=dataset.id, name=dataset.name, source_uri=dataset.source_uri, schema_config=dataset.schema_config
    )
