from dataclasses import dataclass
from uuid import UUID

from qdrant_bench.ports.repositories import ExperimentRepository, RunRepository
from qdrant_bench.presentation.reports.generator import ReportGenerator


@dataclass
class GenerateReportUseCase:
    experiment_repo: ExperimentRepository
    run_repo: RunRepository
    report_generator: ReportGenerator

    async def execute(self, experiment_id: UUID) -> str:
        experiment = await self.experiment_repo.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        runs = await self.run_repo.list(experiment_id=experiment_id)
        return self.report_generator.generate(experiment, runs)




