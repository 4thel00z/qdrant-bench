from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, TypedDict

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from qdrant_bench.domain.entities.core import Dataset


class Distance(str, Enum):
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


class ScalarType(str, Enum):
    INT8 = "int8"


class CompressionRatio(str, Enum):
    X4 = "x4"
    X8 = "x8"
    X16 = "x16"
    X32 = "x32"
    X64 = "x64"


class HnswConfig(TypedDict, total=False):
    m: int
    ef_construct: int
    full_scan_threshold: int
    max_indexing_threads: int
    on_disk: bool
    payload_m: int


class ScalarQuantizationConfig(TypedDict, total=False):
    type: ScalarType
    quantile: float | None
    always_ram: bool


class ProductQuantizationConfig(TypedDict, total=False):
    compression: CompressionRatio
    always_ram: bool


class BinaryQuantizationConfig(TypedDict, total=False):
    always_ram: bool


class QuantizationConfig(TypedDict, total=False):
    scalar: ScalarQuantizationConfig | None
    product: ProductQuantizationConfig | None
    binary: BinaryQuantizationConfig | None


class OptimizersConfig(TypedDict, total=False):
    deleted_threshold: float
    vacuum_min_vector_number: int
    default_segment_number: int
    max_segment_size: int | None
    memmap_threshold: int | None
    indexing_threshold: int
    flush_interval_sec: int
    max_optimization_threads: int


class VectorParams(TypedDict, total=False):
    size: int
    distance: Distance
    hnsw_config: HnswConfig | None
    quantization_config: QuantizationConfig | None
    on_disk: bool | None


class SearchParams(TypedDict, total=False):
    hnsw_ef: int | None
    exact: bool
    quantization: models.QuantizationSearchParams | None
    indexed_only: bool


def create_empty_search_params() -> SearchParams:
    return {}


@dataclass
class WorkloadConfig:
    k: int = 10
    query_count: int = 1000
    score_threshold: float | None = None
    search_params: SearchParams = field(default_factory=create_empty_search_params)

    def to_search_params(self) -> models.SearchParams:
        """Convert to Qdrant search params model"""
        return models.SearchParams(
            hnsw_ef=self.search_params.get("hnsw_ef"),
            exact=self.search_params.get("exact"),
            quantization=self.search_params.get("quantization"),
            indexed_only=self.search_params.get("indexed_only"),
        )


@dataclass
class WorkloadResult:
    predictions: list[Any]
    latencies: list[float]
    total_duration: float


class Workload(Protocol):
    async def execute(self, client: AsyncQdrantClient, dataset: Dataset, config: WorkloadConfig) -> WorkloadResult: ...
