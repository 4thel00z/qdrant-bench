import os
from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from qdrant_bench.application.usecases.connections.manage import CreateConnectionUseCase, ListConnectionsUseCase
from qdrant_bench.application.usecases.datasets.manage import CreateDatasetUseCase, ListDatasetsUseCase
from qdrant_bench.application.usecases.experiments.create import CreateExperimentUseCase, ListExperimentsUseCase
from qdrant_bench.application.usecases.experiments.execute import ExecuteExperimentUseCase
from qdrant_bench.application.usecases.reports.generate import GenerateReportUseCase
from qdrant_bench.application.usecases.runs.trigger import GetRunUseCase, ListRunsUseCase, TriggerRunUseCase
from qdrant_bench.application.usecases.storage.manage import CreateStorageUseCase, ListStorageUseCase
from qdrant_bench.infrastructure.persistence.repositories.connection import SqlAlchemyConnectionRepository
from qdrant_bench.infrastructure.persistence.repositories.dataset import SqlAlchemyDatasetRepository
from qdrant_bench.infrastructure.persistence.repositories.experiment import SqlAlchemyExperimentRepository
from qdrant_bench.infrastructure.persistence.repositories.run import SqlAlchemyRunRepository
from qdrant_bench.infrastructure.persistence.repositories.storage import SqlAlchemyObjectStorageRepository
from qdrant_bench.infrastructure.services.deterministic_embedding import DeterministicEmbeddingAdapter
from qdrant_bench.infrastructure.services.openai_embedding import OpenAIEmbeddingAdapter
from qdrant_bench.infrastructure.telemetry.qdrant_adapter import QdrantTelemetryAdapter
from qdrant_bench.presentation.reports.generator import ReportGenerator


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_maker = request.app.state.sessionmaker
    async with session_maker() as session:
        yield session


def get_create_experiment_usecase(session: AsyncSession = Depends(get_session)) -> CreateExperimentUseCase:
    experiment_repo = SqlAlchemyExperimentRepository(session)
    dataset_repo = SqlAlchemyDatasetRepository(session)
    return CreateExperimentUseCase(experiment_repo, dataset_repo)


def get_list_experiments_usecase(session: AsyncSession = Depends(get_session)) -> ListExperimentsUseCase:
    experiment_repo = SqlAlchemyExperimentRepository(session)
    return ListExperimentsUseCase(experiment_repo)


def get_trigger_run_usecase(session: AsyncSession = Depends(get_session)) -> TriggerRunUseCase:
    run_repo = SqlAlchemyRunRepository(session)
    experiment_repo = SqlAlchemyExperimentRepository(session)
    return TriggerRunUseCase(run_repo, experiment_repo)


def get_list_runs_usecase(session: AsyncSession = Depends(get_session)) -> ListRunsUseCase:
    run_repo = SqlAlchemyRunRepository(session)
    return ListRunsUseCase(run_repo)


def get_get_run_usecase(session: AsyncSession = Depends(get_session)) -> GetRunUseCase:
    run_repo = SqlAlchemyRunRepository(session)
    return GetRunUseCase(run_repo)


def get_execute_experiment_usecase(session: AsyncSession = Depends(get_session)) -> ExecuteExperimentUseCase:
    run_repo = SqlAlchemyRunRepository(session)
    experiment_repo = SqlAlchemyExperimentRepository(session)
    dataset_repo = SqlAlchemyDatasetRepository(session)
    connection_repo = SqlAlchemyConnectionRepository(session)

    embedding_backend = os.getenv("QDRANT_BENCH_EMBEDDING_BACKEND", "openai")
    embedding_service = (
        DeterministicEmbeddingAdapter()
        if embedding_backend == "deterministic"
        else OpenAIEmbeddingAdapter(api_key=os.getenv("OPENAI_API_KEY", ""))
    )
    qdrant_cloud_api_key = os.getenv("QDRANT_API_KEY", "")
    telemetry_adapter = QdrantTelemetryAdapter(cloud_api_key=qdrant_cloud_api_key)

    return ExecuteExperimentUseCase(
        run_repo=run_repo,
        experiment_repo=experiment_repo,
        dataset_repo=dataset_repo,
        connection_repo=connection_repo,
        embedding_service=embedding_service,
        telemetry_adapter=telemetry_adapter,
    )


def get_create_connection_usecase(session: AsyncSession = Depends(get_session)) -> CreateConnectionUseCase:
    return CreateConnectionUseCase(SqlAlchemyConnectionRepository(session))


def get_list_connections_usecase(session: AsyncSession = Depends(get_session)) -> ListConnectionsUseCase:
    return ListConnectionsUseCase(SqlAlchemyConnectionRepository(session))


def get_create_dataset_usecase(session: AsyncSession = Depends(get_session)) -> CreateDatasetUseCase:
    return CreateDatasetUseCase(SqlAlchemyDatasetRepository(session))


def get_list_datasets_usecase(session: AsyncSession = Depends(get_session)) -> ListDatasetsUseCase:
    return ListDatasetsUseCase(SqlAlchemyDatasetRepository(session))


def get_create_storage_usecase(session: AsyncSession = Depends(get_session)) -> CreateStorageUseCase:
    return CreateStorageUseCase(SqlAlchemyObjectStorageRepository(session))


def get_list_storage_usecase(session: AsyncSession = Depends(get_session)) -> ListStorageUseCase:
    return ListStorageUseCase(SqlAlchemyObjectStorageRepository(session))


def get_generate_report_usecase(session: AsyncSession = Depends(get_session)) -> GenerateReportUseCase:
    experiment_repo = SqlAlchemyExperimentRepository(session)
    run_repo = SqlAlchemyRunRepository(session)
    report_generator = ReportGenerator()
    return GenerateReportUseCase(experiment_repo, run_repo, report_generator)
