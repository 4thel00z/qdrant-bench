from dataclasses import dataclass
from uuid import UUID
from typing import List
from qdrant_bench.domain.entities.core import Experiment
from qdrant_bench.ports.repositories import ExperimentRepository, DatasetRepository

@dataclass
class CreateExperimentCommand:
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: dict
    vector_config: dict

class CreateExperimentUseCase:
    def __init__(self, experiment_repo: ExperimentRepository, dataset_repo: DatasetRepository):
        self.experiment_repo = experiment_repo
        self.dataset_repo = dataset_repo

    async def execute(self, command: CreateExperimentCommand) -> Experiment:
        # Validate Dataset exists
        dataset = await self.dataset_repo.get(command.dataset_id)
        if not dataset:
            raise ValueError(f"Dataset with id {command.dataset_id} not found")

        # Create Experiment Domain Entity
        experiment = Experiment(
            name=command.name,
            dataset_id=command.dataset_id,
            connection_id=command.connection_id,
            optimizer_config=command.optimizer_config,
            vector_config=command.vector_config
        )

        # Save to persistence
        return await self.experiment_repo.save(experiment)

class ListExperimentsUseCase:
    def __init__(self, experiment_repo: ExperimentRepository):
        self.experiment_repo = experiment_repo

    async def execute(self) -> List[Experiment]:
        return await self.experiment_repo.list()

