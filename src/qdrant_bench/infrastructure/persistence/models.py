from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import JSON, Field, SQLModel

from qdrant_bench.domain.entities.core import RunStatus


class Connection(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    url: str
    api_key: str  # Encrypted handling should be done in repository/service layer


class ObjectStorage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    bucket: str
    region: str
    endpoint_url: str
    access_key: str
    secret_key: str


class Dataset(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    source_uri: str
    schema_config: dict[str, Any] = Field(default={}, sa_type=JSON)

    @field_validator("schema_config")
    @classmethod
    def validate_schema_config(cls, v: dict[str, Any]) -> dict[str, Any]:
        # Basic validation for schema structure
        if "vectors" not in v and "vector" not in v:
            # Allow loose schema for now, but ideally enforce specific structure
            pass
        return v


class Experiment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    dataset_id: UUID = Field(foreign_key="dataset.id")
    connection_id: UUID = Field(foreign_key="connection.id")
    optimizer_config: dict[str, Any] = Field(default={}, sa_type=JSON)
    vector_config: dict[str, Any] = Field(default={}, sa_type=JSON)


class Run(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    experiment_id: UUID = Field(foreign_key="experiment.id")
    status: RunStatus = Field(default=RunStatus.CREATED)
    start_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    end_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    metrics: dict[str, Any] = Field(default={}, sa_type=JSON)
