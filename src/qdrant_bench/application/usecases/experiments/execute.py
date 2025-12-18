import asyncio
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field, replace
from typing import Any
from uuid import UUID

import logfire
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from qdrant_bench.domain.entities.core import Connection, Dataset, Experiment, RunStatus
from qdrant_bench.domain.services.evaluator import StandardEvaluator
from qdrant_bench.infrastructure.persistence.dataset_loader import load_dataset_corpus, load_ground_truth
from qdrant_bench.infrastructure.telemetry.qdrant_adapter import QdrantTelemetryAdapter
from qdrant_bench.infrastructure.workloads.single_vector import SingleVectorWorkload
from qdrant_bench.ports.embedding_service import EmbeddingService
from qdrant_bench.ports.repositories import ConnectionRepository, DatasetRepository, ExperimentRepository, RunRepository
from qdrant_bench.ports.workload import WorkloadConfig


@dataclass
class WorkflowResult:
    status: RunStatus
    metrics: dict[str, Any]


@dataclass
class ExperimentWorkflow:
    """Orchestrates experiment execution with dependencies as fields"""
    client: AsyncQdrantClient
    embedding_service: EmbeddingService
    telemetry_adapter: QdrantTelemetryAdapter
    evaluator: StandardEvaluator

    async def execute(
        self,
        experiment: Experiment,
        dataset: Dataset,
        connection: Connection
    ) -> WorkflowResult:
        """Main workflow orchestration - pure with respect to inputs"""
        collection_name = await self.create_collection(dataset, experiment)

        indexing_duration = await self.seed_and_index(
            collection_name=collection_name,
            dataset=dataset
        )

        workload_result = await self.run_workload(
            collection_name=collection_name,
            dataset=dataset,
            experiment=experiment
        )

        eval_result = await self.evaluate_results(
            workload_result=workload_result,
            dataset=dataset
        )

        telemetry = await self.telemetry_adapter.get_cluster_stats(connection)

        return WorkflowResult(
            status=RunStatus.COMPLETED,
            metrics={
                **eval_result.scores,
                **telemetry,
                "indexing_time_ms": indexing_duration * 1000,
                "total_duration": workload_result.total_duration
            }
        )

    async def create_collection(
        self,
        dataset: Dataset,
        experiment: Experiment
    ) -> str:
        """Create collection - uses self.client"""
        collection_name = dataset.name

        await delete_collection_if_exists(self.client, collection_name)

        vectors_config = parse_vector_config(experiment.vector_config)
        optimizers_config = parse_optimizer_config(experiment.optimizer_config)

        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
            optimizers_config=optimizers_config
        )

        return collection_name

    async def seed_and_index(
        self,
        collection_name: str,
        dataset: Dataset
    ) -> float:
        """Seed collection and wait for indexing - returns duration"""
        indexing_start = time.perf_counter()

        records = await load_dataset_corpus(dataset)

        async for batch_points in create_point_batches(
            records=records,
            embedding_service=self.embedding_service,
            batch_size=100
        ):
            await self.client.upsert(
                collection_name=collection_name,
                points=batch_points
            )

        await wait_for_indexing(self.client, collection_name)

        return time.perf_counter() - indexing_start

    async def run_workload(
        self,
        collection_name: str,
        dataset: Dataset,
        experiment: Experiment
    ) -> Any:
        """Execute workload"""
        workload = SingleVectorWorkload()

        optimizer_config = experiment.optimizer_config

        config = WorkloadConfig(
            k=optimizer_config.get("k", 10),
            query_count=optimizer_config.get("query_count", 100),
            score_threshold=optimizer_config.get("score_threshold"),
            search_params=optimizer_config.get("search_params", {})
        )

        return await workload.execute(self.client, dataset, config)

    async def evaluate_results(
        self,
        workload_result: Any,
        dataset: Dataset
    ) -> Any:
        """Evaluate workload results against ground truth"""
        ground_truth = await load_ground_truth(dataset)

        return self.evaluator.evaluate(
            workload_result.predictions,
            ground_truth,
            workload_result.latencies
        )


@dataclass
class ExecuteExperimentUseCase:
    run_repo: RunRepository
    experiment_repo: ExperimentRepository
    dataset_repo: DatasetRepository
    connection_repo: ConnectionRepository
    embedding_service: EmbeddingService
    telemetry_adapter: QdrantTelemetryAdapter
    evaluator: StandardEvaluator = field(default_factory=StandardEvaluator)

    async def execute(self, run_id: UUID):
        """Execute experiment run - orchestrates repositories and workflow"""
        with logfire.span("Experiment Execution", run_id=run_id):
            run = await self.run_repo.get(run_id)
            if not run:
                logfire.error(f"Run {run_id} not found")
                return

            experiment = await self.experiment_repo.get(run.experiment_id)
            if not experiment:
                logfire.error(f"Experiment {run.experiment_id} not found")
                await self.run_repo.save(replace(run, status=RunStatus.FAILED))
                return

            dataset = await self.dataset_repo.get(experiment.dataset_id)
            connection = await self.connection_repo.get(experiment.connection_id)

            if not dataset:
                logfire.error("Dataset not found")
                await self.run_repo.save(replace(run, status=RunStatus.FAILED))
                return

            if not connection:
                logfire.error("Connection not found")
                await self.run_repo.save(replace(run, status=RunStatus.FAILED))
                return

            await self.run_repo.save(replace(run, status=RunStatus.RUNNING))

            try:
                result = await self.execute_workflow(
                    experiment=experiment,
                    dataset=dataset,
                    connection=connection
                )

                await self.run_repo.save(replace(
                    run,
                    status=result.status,
                    metrics=result.metrics
                ))

                logfire.info(f"Run {run_id} completed successfully")

            except Exception as e:
                logfire.error(f"Run {run_id} failed: {e}")
                await self.run_repo.save(replace(run, status=RunStatus.FAILED))

    async def execute_workflow(
        self,
        experiment: Experiment,
        dataset: Dataset,
        connection: Connection
    ) -> WorkflowResult:
        """Create workflow orchestrator and execute"""
        client = AsyncQdrantClient(url=connection.url, api_key=connection.api_key)

        workflow = ExperimentWorkflow(
            client=client,
            embedding_service=self.embedding_service,
            telemetry_adapter=self.telemetry_adapter,
            evaluator=self.evaluator
        )

        return await workflow.execute(
            experiment=experiment,
            dataset=dataset,
            connection=connection
        )


def parse_vector_config(vector_config: dict[str, Any]) -> Any:
    """Pure function - parse vector config to Qdrant models"""
    if "size" in vector_config:
        return models.VectorParams(
            size=vector_config["size"],
            distance=models.Distance[vector_config.get("distance", "COSINE")]
        )

    if "vectors" in vector_config:
        return {
            name: models.VectorParams(
                size=cfg["size"],
                distance=models.Distance[cfg.get("distance", "COSINE")]
            )
            for name, cfg in vector_config["vectors"].items()
        }

    raise ValueError("Invalid vector_config structure")


def parse_optimizer_config(
    optimizer_config: dict[str, Any]
) -> models.OptimizersConfigDiff | None:
    """Pure function - parse optimizer config to Qdrant models"""
    if not optimizer_config:
        return None

    return models.OptimizersConfigDiff(
        indexing_threshold=optimizer_config.get("indexing_threshold", 20000)
    )


def create_point_struct(
    idx: int,
    embedding: list[float],
    record: dict[str, Any]
) -> models.PointStruct:
    """Pure function - create a single point"""
    return models.PointStruct(
        id=idx,
        vector=embedding,
        payload=record.get("metadata", {})
    )


async def delete_collection_if_exists(
    client: AsyncQdrantClient,
    collection_name: str
) -> None:
    """Helper function - delete collection if it exists"""
    try:
        await client.get_collection(collection_name)
        await client.delete_collection(collection_name)
    except Exception:
        pass


async def wait_for_indexing(
    client: AsyncQdrantClient,
    collection_name: str
) -> None:
    """Helper function - wait for collection indexing to complete"""
    await client.update_collection(
        collection_name=collection_name,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0)
    )

    while True:
        info = await client.get_collection(collection_name)
        if info.status == models.CollectionStatus.GREEN:
            break
        await asyncio.sleep(1)


async def create_point_batches(
    records: list[dict[str, Any]],
    embedding_service: EmbeddingService,
    batch_size: int,
    model: str = "text-embedding-3-small"
) -> AsyncGenerator[list[models.PointStruct], None]:
    """Generator that yields batches of embedded points"""
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        texts = [rec.get("text", "") for rec in batch]

        embeddings = await embedding_service.embed_text(texts, model=model)

        points = [
            create_point_struct(i + idx, embedding, rec)
            for idx, (rec, embedding) in enumerate(zip(batch, embeddings))
        ]

        yield points
