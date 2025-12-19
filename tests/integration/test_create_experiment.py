"""Integration tests for CreateExperimentUseCase"""

from uuid import uuid4

import pytest

from qdrant_bench.application.usecases.experiments.create import CreateExperimentCommand, CreateExperimentUseCase
from tests.integration.fakes.repositories import FakeDatasetRepository, FakeExperimentRepository
from tests.integration.fixtures import create_test_dataset


@pytest.mark.asyncio
async def test_create_experiment_with_valid_config():
    """Create experiment succeeds with valid configuration"""
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()

    dataset = create_test_dataset()
    await dataset_repo.save(dataset)

    use_case = CreateExperimentUseCase(experiment_repo=experiment_repo, dataset_repo=dataset_repo)

    command = CreateExperimentCommand(
        name="test-experiment",
        dataset_id=dataset.id,
        connection_id=uuid4(),
        optimizer_config={"indexing_threshold": 20000},
        vector_config={"size": 384, "distance": "COSINE"},
    )

    experiment = await use_case.execute(command)

    assert experiment.id in experiment_repo.experiments
    assert experiment.name == "test-experiment"
    assert experiment.dataset_id == dataset.id
    assert experiment.vector_config["size"] == 384


@pytest.mark.asyncio
async def test_create_experiment_validation_fails_dimension_mismatch():
    """Create experiment fails when dimensions don't match"""
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()

    dataset = create_test_dataset()
    await dataset_repo.save(dataset)

    use_case = CreateExperimentUseCase(experiment_repo=experiment_repo, dataset_repo=dataset_repo)

    command = CreateExperimentCommand(
        name="test",
        dataset_id=dataset.id,
        connection_id=uuid4(),
        optimizer_config={},
        vector_config={"size": 768},  # Wrong dimension
    )

    with pytest.raises(ValueError) as exc:
        await use_case.execute(command)

    assert "Dimension mismatch" in str(exc.value)
    assert "384" in str(exc.value)
    assert "768" in str(exc.value)
    assert len(experiment_repo.experiments) == 0


@pytest.mark.asyncio
async def test_create_experiment_fails_dataset_not_found():
    """Create experiment fails when dataset doesn't exist"""
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()

    use_case = CreateExperimentUseCase(experiment_repo=experiment_repo, dataset_repo=dataset_repo)

    command = CreateExperimentCommand(
        name="test",
        dataset_id=uuid4(),  # Non-existent dataset
        connection_id=uuid4(),
        optimizer_config={},
        vector_config={"size": 384},
    )

    with pytest.raises(ValueError) as exc:
        await use_case.execute(command)

    assert "not found" in str(exc.value)
    assert len(experiment_repo.experiments) == 0


@pytest.mark.asyncio
async def test_list_experiments_returns_all():
    """List experiments returns all saved experiments"""
    from qdrant_bench.application.usecases.experiments.create import ListExperimentsUseCase

    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()

    dataset = create_test_dataset()
    await dataset_repo.save(dataset)

    create_use_case = CreateExperimentUseCase(experiment_repo=experiment_repo, dataset_repo=dataset_repo)

    command1 = CreateExperimentCommand(
        name="exp-1", dataset_id=dataset.id, connection_id=uuid4(), optimizer_config={}, vector_config={"size": 384}
    )

    command2 = CreateExperimentCommand(
        name="exp-2", dataset_id=dataset.id, connection_id=uuid4(), optimizer_config={}, vector_config={"size": 384}
    )

    await create_use_case.execute(command1)
    await create_use_case.execute(command2)

    list_use_case = ListExperimentsUseCase(experiment_repo=experiment_repo)
    experiments = await list_use_case.execute()

    assert len(experiments) == 2
    assert {exp.name for exp in experiments} == {"exp-1", "exp-2"}
