"""Test fixtures and helper functions for integration tests"""
from uuid import uuid4

from qdrant_bench.domain.entities.core import Connection, Dataset, Experiment, Run, RunStatus


def create_test_connection() -> Connection:
    """Create a test connection entity"""
    return Connection(
        id=uuid4(),
        name="test-connection",
        url="http://localhost:6333",
        api_key="test-api-key"
    )


def create_test_dataset() -> Dataset:
    """Create a test dataset entity"""
    return Dataset(
        id=uuid4(),
        name="test-dataset",
        source_uri="test://data/corpus.parquet",
        schema_config={
            "vector": {"dim": 384, "distance": "Cosine"},
            "scalar_fields": ["text", "metadata"]
        }
    )


def create_test_experiment(dataset_id, connection_id) -> Experiment:
    """Create a test experiment entity"""
    return Experiment(
        id=uuid4(),
        name="test-experiment",
        dataset_id=dataset_id,
        connection_id=connection_id,
        optimizer_config={
            "indexing_threshold": 20000,
            "k": 10,
            "query_count": 100,
            "search_params": {}
        },
        vector_config={
            "size": 384,
            "distance": "COSINE"
        }
    )


def create_test_run(experiment_id) -> Run:
    """Create a test run entity"""
    return Run(
        id=uuid4(),
        experiment_id=experiment_id,
        status=RunStatus.CREATED
    )


def create_multi_vector_dataset() -> Dataset:
    """Create a test dataset with multi-vector schema"""
    return Dataset(
        id=uuid4(),
        name="multi-vector-dataset",
        source_uri="test://data/multi-corpus.parquet",
        schema_config={
            "vectors": {
                "text": {"dim": 384, "distance": "Cosine"},
                "image": {"dim": 512, "distance": "Euclidean"}
            },
            "scalar_fields": ["title", "url"]
        }
    )


def create_multi_vector_experiment(dataset_id, connection_id) -> Experiment:
    """Create a test experiment with multi-vector config"""
    return Experiment(
        id=uuid4(),
        name="multi-vector-experiment",
        dataset_id=dataset_id,
        connection_id=connection_id,
        optimizer_config={
            "indexing_threshold": 20000,
            "k": 10,
            "query_count": 50
        },
        vector_config={
            "vectors": {
                "text": {"size": 384, "distance": "COSINE"},
                "image": {"size": 512, "distance": "EUCLIDEAN"}
            }
        }
    )

