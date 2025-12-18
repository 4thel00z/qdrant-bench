from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

@dataclass
class Connection:
    name: str
    url: str
    api_key: str
    id: UUID = field(default_factory=uuid4)

@dataclass
class ObjectStorage:
    bucket: str
    region: str
    endpoint_url: str
    access_key: str
    secret_key: str
    id: UUID = field(default_factory=uuid4)

@dataclass
class Dataset:
    name: str
    source_uri: str
    schema_config: Dict[str, Any]
    id: UUID = field(default_factory=uuid4)

@dataclass
class Experiment:
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: Dict[str, Any]
    vector_config: Dict[str, Any]
    id: UUID = field(default_factory=uuid4)

class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

@dataclass
class Run:
    experiment_id: UUID
    status: RunStatus = RunStatus.CREATED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

