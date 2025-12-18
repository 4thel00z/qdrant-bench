from typing import Protocol, Any, Dict, List
from dataclasses import dataclass
from qdrant_client import AsyncQdrantClient
from qdrant_bench.domain.entities.core import Dataset

@dataclass
class WorkloadConfig:
    k: int = 10
    query_count: int = 1000
    search_params: Dict[str, Any] = None

@dataclass
class WorkloadResult:
    predictions: List[Any]
    latencies: List[float]
    total_duration: float

class Workload(Protocol):
    async def execute(
        self, 
        client: AsyncQdrantClient, 
        dataset: Dataset, 
        config: WorkloadConfig
    ) -> WorkloadResult:
        ...

