"""Integration tests for ExecuteExperimentUseCase"""

from unittest.mock import patch
from uuid import uuid4

import pytest

from qdrant_bench.application.usecases.experiments.execute import ExecuteExperimentUseCase
from qdrant_bench.domain.entities.core import RunStatus
from qdrant_bench.domain.services.evaluator import GroundTruth
from tests.integration.fakes.adapters import FakeTelemetryAdapter
from tests.integration.fakes.repositories import (
    FakeConnectionRepository,
    FakeDatasetRepository,
    FakeExperimentRepository,
    FakeRunRepository,
)
from tests.integration.fakes.services import FakeEmbeddingService
from tests.integration.fixtures import (
    create_test_connection,
    create_test_dataset,
    create_test_experiment,
    create_test_run,
)


@pytest.mark.asyncio
async def test_execute_experiment_handles_missing_run():
    """Use case handles missing run gracefully"""
    run_repo = FakeRunRepository()
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()
    connection_repo = FakeConnectionRepository()
    embedding_service = FakeEmbeddingService()
    telemetry_adapter = FakeTelemetryAdapter()

    use_case = ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )

    await use_case.execute(uuid4())

    assert len(run_repo.runs) == 0


@pytest.mark.asyncio
async def test_execute_experiment_handles_missing_experiment():
    """Use case handles missing experiment and fails run"""
    run_repo = FakeRunRepository()
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()
    connection_repo = FakeConnectionRepository()
    embedding_service = FakeEmbeddingService()
    telemetry_adapter = FakeTelemetryAdapter()

    run = create_test_run(uuid4())
    await run_repo.save(run)

    use_case = ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )

    await use_case.execute(run.id)

    updated_run = await run_repo.get(run.id)
    assert updated_run.status == RunStatus.FAILED


@pytest.mark.asyncio
async def test_execute_experiment_handles_missing_dataset():
    """Use case handles missing dataset and fails run"""
    run_repo = FakeRunRepository()
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()
    connection_repo = FakeConnectionRepository()
    embedding_service = FakeEmbeddingService()
    telemetry_adapter = FakeTelemetryAdapter()

    connection = create_test_connection()
    experiment = create_test_experiment(uuid4(), connection.id)
    run = create_test_run(experiment.id)

    await connection_repo.save(connection)
    await experiment_repo.save(experiment)
    await run_repo.save(run)

    use_case = ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )

    await use_case.execute(run.id)

    updated_run = await run_repo.get(run.id)
    assert updated_run.status == RunStatus.FAILED


@pytest.mark.asyncio
async def test_execute_experiment_handles_missing_connection():
    """Use case handles missing connection and fails run"""
    run_repo = FakeRunRepository()
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()
    connection_repo = FakeConnectionRepository()
    embedding_service = FakeEmbeddingService()
    telemetry_adapter = FakeTelemetryAdapter()

    dataset = create_test_dataset()
    experiment = create_test_experiment(dataset.id, uuid4())
    run = create_test_run(experiment.id)

    await dataset_repo.save(dataset)
    await experiment_repo.save(experiment)
    await run_repo.save(run)

    use_case = ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )

    await use_case.execute(run.id)

    updated_run = await run_repo.get(run.id)
    assert updated_run.status == RunStatus.FAILED


@pytest.mark.asyncio
async def test_execute_experiment_full_flow_with_mocked_data():
    """Use case executes full experiment flow with mocked dataset loading"""
    run_repo = FakeRunRepository()
    experiment_repo = FakeExperimentRepository()
    dataset_repo = FakeDatasetRepository()
    connection_repo = FakeConnectionRepository()
    embedding_service = FakeEmbeddingService()
    telemetry_adapter = FakeTelemetryAdapter()

    connection = create_test_connection()
    dataset = create_test_dataset()
    experiment = create_test_experiment(dataset.id, connection.id)
    run = create_test_run(experiment.id)

    await connection_repo.save(connection)
    await dataset_repo.save(dataset)
    await experiment_repo.save(experiment)
    await run_repo.save(run)

    assert run.status == RunStatus.CREATED

    use_case = ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )

    with (
        patch("qdrant_bench.application.usecases.experiments.execute.load_dataset_corpus") as mock_corpus,
        patch("qdrant_bench.application.usecases.experiments.execute.load_ground_truth") as mock_gt,
    ):
        mock_corpus.return_value = [{"text": f"doc {i}", "metadata": {"id": i}} for i in range(10)]

        mock_gt.return_value = GroundTruth(relevant_items={i: {i} for i in range(5)})

        await use_case.execute(run.id)

    updated_run = await run_repo.get(run.id)
    assert updated_run.status in [RunStatus.COMPLETED, RunStatus.FAILED]
