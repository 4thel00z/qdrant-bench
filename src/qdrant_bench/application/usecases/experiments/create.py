from dataclasses import dataclass
from typing import Any
from uuid import UUID

from qdrant_bench.domain.entities.core import Experiment
from qdrant_bench.ports.repositories import DatasetRepository, ExperimentRepository


@dataclass
class CreateExperimentCommand:
    name: str
    dataset_id: UUID
    connection_id: UUID
    optimizer_config: dict
    vector_config: dict


@dataclass
class CreateExperimentUseCase:
    experiment_repo: ExperimentRepository
    dataset_repo: DatasetRepository

    async def execute(self, command: CreateExperimentCommand) -> Experiment:
        dataset = await self.dataset_repo.get(command.dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {command.dataset_id} not found")

        validation_error = validate_vector_config_match(
            vector_config=command.vector_config, schema_config=dataset.schema_config
        )
        if validation_error:
            raise ValueError(validation_error)

        experiment = Experiment(
            name=command.name,
            dataset_id=command.dataset_id,
            connection_id=command.connection_id,
            optimizer_config=command.optimizer_config,
            vector_config=command.vector_config,
        )

        return await self.experiment_repo.save(experiment)


@dataclass
class ListExperimentsUseCase:
    experiment_repo: ExperimentRepository

    async def execute(self) -> list[Experiment]:
        return await self.experiment_repo.list()


def validate_vector_config_match(vector_config: dict[str, Any], schema_config: dict[str, Any]) -> str | None:
    """
    Pure validation function.
    Returns error message or None if valid.
    """
    dataset_vector = schema_config.get("vector")
    dataset_vectors = schema_config.get("vectors")

    if dataset_vector:
        return validate_single_vector(vector_config, dataset_vector)

    if dataset_vectors:
        return validate_multi_vector(vector_config, dataset_vectors)

    return "Dataset schema missing vector configuration"


def validate_single_vector(vector_config: dict[str, Any], schema_vector: dict[str, Any]) -> str | None:
    """Pure function - validate single vector config"""
    if "size" not in vector_config:
        return "vector_config missing 'size' field"

    expected_dim = schema_vector.get("dim")
    actual_dim = vector_config.get("size")

    if expected_dim and expected_dim != actual_dim:
        return f"Dimension mismatch: dataset expects {expected_dim}, config has {actual_dim}"

    return None


def validate_multi_vector(vector_config: dict[str, Any], dataset_vectors: dict[str, Any]) -> str | None:
    """Pure function - validate multi-vector config"""
    experiment_vectors = vector_config.get("vectors")

    if not experiment_vectors:
        return "Multi-vector dataset requires 'vectors' in config"

    for name, params in experiment_vectors.items():
        if name not in dataset_vectors:
            available = ", ".join(dataset_vectors.keys())
            return f"Vector '{name}' not in dataset. Available: {available}"

        expected_dim = dataset_vectors[name].get("dim")
        actual_dim = params.get("size")

        if expected_dim and actual_dim and expected_dim != actual_dim:
            return f"Vector '{name}' dimension mismatch: expected {expected_dim}, got {actual_dim}"

    return None
