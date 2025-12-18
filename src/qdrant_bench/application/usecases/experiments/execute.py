from typing import Any, Dict
from uuid import UUID
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
import logfire

from qdrant_bench.domain.entities.core import Run, RunStatus, Experiment
from qdrant_bench.ports.repositories import RunRepository, ExperimentRepository, DatasetRepository, ConnectionRepository
from qdrant_bench.ports.workload import WorkloadConfig
from qdrant_bench.infrastructure.workloads.single_vector import SingleVectorWorkload
from qdrant_bench.domain.services.evaluator import StandardEvaluator, GroundTruth
from qdrant_bench.infrastructure.telemetry.qdrant_adapter import QdrantTelemetryAdapter
from qdrant_bench.ports.embedding_service import EmbeddingService

class ExecuteExperimentUseCase:
    def __init__(
        self,
        run_repo: RunRepository,
        experiment_repo: ExperimentRepository,
        dataset_repo: DatasetRepository,
        connection_repo: ConnectionRepository,
        embedding_service: EmbeddingService,
        telemetry_adapter: QdrantTelemetryAdapter
    ):
        self.run_repo = run_repo
        self.experiment_repo = experiment_repo
        self.dataset_repo = dataset_repo
        self.connection_repo = connection_repo
        self.embedding_service = embedding_service
        self.telemetry_adapter = telemetry_adapter
        self.evaluator = StandardEvaluator()

    async def execute(self, run_id: UUID):
        with logfire.span("Experiment Execution", run_id=run_id):
            run = await self.run_repo.get(run_id)
            if not run:
                logfire.error(f"Run {run_id} not found")
                return

            experiment = await self.experiment_repo.get(run.experiment_id)
            if not experiment:
                logfire.error(f"Experiment {run.experiment_id} not found")
                return

            dataset = await self.dataset_repo.get(experiment.dataset_id)
            connection = await self.connection_repo.get(experiment.connection_id) # We need this repo

            if not dataset or not connection:
                logfire.error("Dataset or Connection not found")
                run.status = RunStatus.FAILED
                await self.run_repo.save(run)
                return

            # Update status to RUNNING
            run.status = RunStatus.RUNNING
            await self.run_repo.save(run)

            try:
                # 1. Connect to Qdrant
                client = AsyncQdrantClient(url=connection.url, api_key=connection.api_key)
                
                # 2. Configure Collection (Simulated Provisioning/Config logic)
                # In a real scenario, we would check if collection exists, recreate it with experiment.vector_config
                # For now, assuming collection exists or just using it
                
                # 3. Workload Execution
                workload = SingleVectorWorkload() # Logic to choose workload type based on config
                
                workload_config = WorkloadConfig(
                    k=10,
                    query_count=100, # Should come from Experiment config
                    search_params=experiment.optimizer_config.get("search_params")
                )
                
                result = await workload.execute(client, dataset, workload_config)
                
                # 4. Evaluation
                # Mock Ground Truth for now
                ground_truth = GroundTruth(relevant_items={i: {i} for i in range(100)})
                eval_result = self.evaluator.evaluate(result.predictions, ground_truth, result.latencies)
                
                # 5. Telemetry
                cluster_stats = await self.telemetry_adapter.get_cluster_stats(str(connection.id))
                
                # 6. Persist Results
                run.metrics = {
                    **eval_result.scores,
                    **cluster_stats,
                    "total_duration": result.total_duration
                }
                run.status = RunStatus.COMPLETED
                await self.run_repo.save(run)
                
                logfire.info(f"Run {run_id} completed successfully")

            except Exception as e:
                logfire.error(f"Run {run_id} failed: {e}")
                run.status = RunStatus.FAILED
                await self.run_repo.save(run)

