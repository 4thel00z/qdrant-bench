from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from qdrant_bench.domain.entities.core import Run, RunStatus
from qdrant_bench.ports.repositories import RunRepository, ExperimentRepository

@dataclass
class TriggerRunCommand:
    experiment_id: UUID

class TriggerRunUseCase:
    def __init__(self, run_repo: RunRepository, experiment_repo: ExperimentRepository):
        self.run_repo = run_repo
        self.experiment_repo = experiment_repo

    async def execute(self, command: TriggerRunCommand) -> Run:
        experiment = await self.experiment_repo.get(command.experiment_id)
        if not experiment:
            raise ValueError(f"Experiment with id {command.experiment_id} not found")

        run = Run(experiment_id=command.experiment_id, status=RunStatus.CREATED)
        return await self.run_repo.save(run)

class ListRunsUseCase:
    def __init__(self, run_repo: RunRepository):
        self.run_repo = run_repo

    async def execute(self, experiment_id: Optional[UUID] = None, status: Optional[str] = None) -> List[Run]:
        return await self.run_repo.list(experiment_id, status)

class GetRunUseCase:
    def __init__(self, run_repo: RunRepository):
        self.run_repo = run_repo

    async def execute(self, run_id: UUID) -> Optional[Run]:
        return await self.run_repo.get(run_id)

