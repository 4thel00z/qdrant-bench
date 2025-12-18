from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, JSON
from pydantic import field_validator, model_validator

class Connection(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    url: str
    api_key: str # Encrypted handling should be done in repository/service layer

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
    schema_config: Dict[str, Any] = Field(default={}, sa_type=JSON)

    @field_validator("schema_config")
    @classmethod
    def validate_schema_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
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
    optimizer_config: Dict[str, Any] = Field(default={}, sa_type=JSON)
    vector_config: Dict[str, Any] = Field(default={}, sa_type=JSON)

    @model_validator(mode="after")
    def validate_vector_config_match(self):
        # In a real scenario, we would check if dataset_id is resolved and match 
        # vector_config with dataset.schema_config. 
        # Since this is a DB model, deep validation usually happens in Service layer 
        # or we need to fetch the dataset. 
        # For now, we just ensure vector_config is a dict.
        return self

class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class Run(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    experiment_id: UUID = Field(foreign_key="experiment.id")
    status: RunStatus = Field(default=RunStatus.CREATED)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = Field(default={}, sa_type=JSON)

