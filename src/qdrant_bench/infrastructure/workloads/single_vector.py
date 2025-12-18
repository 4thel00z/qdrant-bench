import asyncio
import time
from typing import Any

import logfire
from qdrant_client import AsyncQdrantClient

from qdrant_bench.domain.entities.core import Dataset
from qdrant_bench.infrastructure.persistence.dataset_loader import load_query_data
from qdrant_bench.ports.workload import Workload, WorkloadConfig, WorkloadResult


class SingleVectorWorkload(Workload):
    async def execute(self, client: AsyncQdrantClient, dataset: Dataset, config: WorkloadConfig) -> WorkloadResult:
        """Execute workload with real data"""
        collection_name = dataset.name

        queries = await load_query_vectors(dataset, config.query_count)

        if not queries:
            raise ValueError(f"No queries loaded from dataset {dataset.name}")

        return await execute_search_batch(
            client=client,
            collection_name=collection_name,
            queries=queries,
            config=config
        )


async def load_query_vectors(dataset: Dataset, limit: int) -> list[list[float]]:
    """Pure async function - load query vectors from dataset"""
    query_records = await load_query_data(dataset, limit)

    return [rec["vector"] for rec in query_records if "vector" in rec]


async def execute_search_batch(
    client: AsyncQdrantClient,
    collection_name: str,
    queries: list[list[float]],
    config: WorkloadConfig
) -> WorkloadResult:
    """Execute batch of searches and collect timing"""
    start_total = time.perf_counter()

    results = await asyncio.gather(*[
        execute_single_search(client, collection_name, query, config)
        for query in queries
    ])

    total_duration = time.perf_counter() - start_total

    predictions = [r["prediction"] for r in results]
    latencies = [r["latency"] for r in results]

    return WorkloadResult(
        predictions=predictions,
        latencies=latencies,
        total_duration=total_duration
    )


async def execute_single_search(
    client: AsyncQdrantClient,
    collection_name: str,
    query: list[float],
    config: WorkloadConfig
) -> dict[str, Any]:
    """Execute single search with timing"""
    start = time.perf_counter()

    with logfire.span("Single Search", collection=collection_name):
        response = await client.query_points(
            collection_name=collection_name,
            query=query,
            limit=config.k,
            score_threshold=config.score_threshold,
            search_params=config.to_search_params()
        )

    latency = time.perf_counter() - start

    return {"prediction": response.points, "latency": latency}
