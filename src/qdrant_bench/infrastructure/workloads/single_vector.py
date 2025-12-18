import time
from typing import List, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
import logfire
from qdrant_bench.ports.workload import Workload, WorkloadConfig, WorkloadResult
from qdrant_bench.domain.entities.core import Dataset

class SingleVectorWorkload(Workload):
    async def execute(
        self, 
        client: AsyncQdrantClient, 
        dataset: Dataset, 
        config: WorkloadConfig
    ) -> WorkloadResult:
        collection_name = dataset.name
        
        # Mock fetching queries from dataset (in real implementation, this would read from source_uri)
        # For now, we generate random vectors or use a placeholder if dataset adapter is not fully ready
        queries = self._get_queries(dataset, config.query_count) 
        
        predictions = []
        latencies = []
        
        start_total = time.perf_counter()
        
        with logfire.span("Executing Single Vector Workload", collection=collection_name, k=config.k):
            for query_vector in queries:
                start_query = time.perf_counter()
                
                search_result = await client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=config.k,
                    search_params=models.SearchParams(**(config.search_params or {}))
                )
                
                duration = time.perf_counter() - start_query
                latencies.append(duration)
                predictions.append(search_result)
                
        total_duration = time.perf_counter() - start_total
        
        return WorkloadResult(
            predictions=predictions,
            latencies=latencies,
            total_duration=total_duration
        )

    def _get_queries(self, dataset: Dataset, count: int) -> List[List[float]]:
        # TODO: Integrate with a Dataset Adapter to actually read query vectors
        # Placeholder: Returning random vectors matching dimension
        # Assuming dimension is part of schema_config, defaulting to 1536 for now
        dim = dataset.schema_config.get("vector_config", {}).get("size", 1536)
        import random
        return [[random.random() for _ in range(dim)] for _ in range(count)]

