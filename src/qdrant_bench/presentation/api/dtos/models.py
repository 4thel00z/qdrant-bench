from pydantic import BaseModel
from uuid import UUID
from typing import Dict, Any, Optional, List
from datetime import datetime
from qdrant_bench.domain.entities.core import RunStatus

class CreateExperimentRequest(BaseModel):
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: Dict[str, Any]
    vector_config: Dict[str, Any]

class ExperimentResponse(BaseModel):
    id: UUID
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: Dict[str, Any]
    vector_config: Dict[str, Any]

class TriggerRunRequest(BaseModel):
    pass # No body needed for now, experiment_id is in path

class RunResponse(BaseModel):
    id: UUID
    experiment_id: UUID
    status: RunStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    metrics: Dict[str, Any]

