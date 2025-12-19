"""Fake repository implementations for testing"""

from dataclasses import dataclass, field
from uuid import UUID

from qdrant_bench.domain.entities.core import Connection, Dataset, Experiment, ObjectStorage, Run


@dataclass
class FakeRunRepository:
    """In-memory run repository"""

    runs: dict[UUID, Run] = field(default_factory=dict)

    async def save(self, run: Run) -> Run:
        self.runs[run.id] = run
        return run

    async def get(self, id: UUID) -> Run | None:
        return self.runs.get(id)

    async def list(self, experiment_id: UUID | None = None, status: str | None = None) -> list[Run]:
        """Pure function - filter runs based on criteria"""
        runs = list(self.runs.values())

        filters = [
            *([] if not experiment_id else [lambda r: r.experiment_id == experiment_id]),
            *([] if not status else [lambda r: r.status == status]),
        ]

        return [run for run in runs if all(f(run) for f in filters)]


@dataclass
class FakeExperimentRepository:
    """In-memory experiment repository"""

    experiments: dict[UUID, Experiment] = field(default_factory=dict)

    async def save(self, experiment: Experiment) -> Experiment:
        self.experiments[experiment.id] = experiment
        return experiment

    async def get(self, id: UUID) -> Experiment | None:
        return self.experiments.get(id)

    async def list(self) -> list[Experiment]:
        return list(self.experiments.values())


@dataclass
class FakeDatasetRepository:
    """In-memory dataset repository"""

    datasets: dict[UUID, Dataset] = field(default_factory=dict)

    async def save(self, dataset: Dataset) -> Dataset:
        self.datasets[dataset.id] = dataset
        return dataset

    async def get(self, id: UUID) -> Dataset | None:
        return self.datasets.get(id)

    async def list(self) -> list[Dataset]:
        return list(self.datasets.values())


@dataclass
class FakeConnectionRepository:
    """In-memory connection repository"""

    connections: dict[UUID, Connection] = field(default_factory=dict)

    async def save(self, connection: Connection) -> Connection:
        self.connections[connection.id] = connection
        return connection

    async def get(self, id: UUID) -> Connection | None:
        return self.connections.get(id)

    async def list(self) -> list[Connection]:
        return list(self.connections.values())


@dataclass
class FakeObjectStorageRepository:
    """In-memory object storage repository"""

    storages: dict[UUID, ObjectStorage] = field(default_factory=dict)

    async def save(self, storage: ObjectStorage) -> ObjectStorage:
        self.storages[storage.id] = storage
        return storage

    async def list(self) -> list[ObjectStorage]:
        return list(self.storages.values())
