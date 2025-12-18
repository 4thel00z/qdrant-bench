from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from qdrant_bench.domain.entities.core import RunStatus


class CreateExperimentRequest(BaseModel):
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: dict[str, Any]
    vector_config: dict[str, Any]


class ExperimentResponse(BaseModel):
    id: UUID
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: dict[str, Any]
    vector_config: dict[str, Any]


class TriggerRunRequest(BaseModel):
    pass  # No body needed for now, experiment_id is in path


class RunResponse(BaseModel):
    id: UUID
    experiment_id: UUID
    status: RunStatus
    start_time: datetime | None
    end_time: datetime | None
    metrics: dict[str, Any]
