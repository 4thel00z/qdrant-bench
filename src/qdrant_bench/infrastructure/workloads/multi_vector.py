import time
from typing import Any

import logfire
from qdrant_client import AsyncQdrantClient

from qdrant_bench.domain.entities.core import Dataset
from qdrant_bench.infrastructure.persistence.dataset_loader import load_query_data
from qdrant_bench.ports.workload import Workload, WorkloadConfig, WorkloadResult


class MultiVectorWorkload(Workload):
    async def execute(self, client: AsyncQdrantClient, dataset: Dataset, config: WorkloadConfig) -> WorkloadResult:
        """Execute multi-vector workload with real data"""
        collection_name = dataset.name

        vector_names = extract_vector_names(dataset)
        if not vector_names:
            raise ValueError("Multi-vector workload requires 'vectors' in schema_config")

        queries = await load_multi_vector_queries(dataset, config.query_count, vector_names)

        if not queries:
            raise ValueError(f"No queries loaded from dataset {dataset.name}")

        return await execute_multi_vector_search_batch(
            client=client, collection_name=collection_name, queries=queries, vector_names=vector_names, config=config
        )


def extract_vector_names(dataset: Dataset) -> list[str]:
    """Pure function - extract vector names from dataset schema"""
    return list(dataset.schema_config.get("vectors", {}).keys())


async def load_multi_vector_queries(
    dataset: Dataset, limit: int, vector_names: list[str]
) -> list[dict[str, list[float]]]:
    """Pure async function - load queries with multiple named vectors"""
    query_records = await load_query_data(dataset, limit)

    return [{name: rec[f"{name}_vector"] for name in vector_names if f"{name}_vector" in rec} for rec in query_records]


async def execute_multi_vector_search_batch(
    client: AsyncQdrantClient,
    collection_name: str,
    queries: list[dict[str, list[float]]],
    vector_names: list[str],
    config: WorkloadConfig,
) -> WorkloadResult:
    """Execute batch of multi-vector searches"""
    start_total = time.perf_counter()

    primary_vector = vector_names[0]

    results = [
        await execute_multi_vector_search(client, collection_name, query_bundle, primary_vector, config)
        for query_bundle in queries
    ]

    total_duration = time.perf_counter() - start_total

    predictions = [r["prediction"] for r in results]
    latencies = [r["latency"] for r in results]

    return WorkloadResult(predictions=predictions, latencies=latencies, total_duration=total_duration)


async def execute_multi_vector_search(
    client: AsyncQdrantClient,
    collection_name: str,
    query_bundle: dict[str, list[float]],
    primary_vector: str,
    config: WorkloadConfig,
) -> dict[str, Any]:
    """Execute single multi-vector search with timing"""
    start = time.perf_counter()

    with logfire.span("Multi-Vector Search", collection=collection_name):
        response = await client.query_points(
            collection_name=collection_name,
            query=query_bundle[primary_vector],
            using=primary_vector,
            limit=config.k,
            score_threshold=config.score_threshold,
            search_params=config.to_search_params(),
        )

    latency = time.perf_counter() - start

    return {"prediction": response.points, "latency": latency}
