from dataclasses import dataclass
from typing import Any

from qdrant_bench.domain.entities.core import Dataset
from qdrant_bench.ports.repositories import DatasetRepository


@dataclass
class CreateDatasetCommand:
    name: str
    source_uri: str
    schema_config: dict[str, Any]


@dataclass
class CreateDatasetUseCase:
    dataset_repo: DatasetRepository

    async def execute(self, command: CreateDatasetCommand) -> Dataset:
        dataset = Dataset(name=command.name, source_uri=command.source_uri, schema_config=command.schema_config)
        return await self.dataset_repo.save(dataset)


@dataclass
class ListDatasetsUseCase:
    dataset_repo: DatasetRepository

    async def execute(self) -> list[Dataset]:
        return await self.dataset_repo.list()
