from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


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
    schema_config: dict[str, Any]
    id: UUID = field(default_factory=uuid4)


@dataclass
class Experiment:
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: dict[str, Any]
    vector_config: dict[str, Any]
    id: UUID = field(default_factory=uuid4)


@dataclass
class Run:
    experiment_id: UUID
    status: RunStatus = RunStatus.CREATED
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
