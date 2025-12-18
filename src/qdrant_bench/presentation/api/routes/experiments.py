from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_bench.presentation.api.dtos.models import CreateExperimentRequest, ExperimentResponse
from qdrant_bench.application.usecases.experiments.create import CreateExperimentUseCase, CreateExperimentCommand, ListExperimentsUseCase
from qdrant_bench.infrastructure.persistence.repositories.experiment import SqlAlchemyExperimentRepository
from qdrant_bench.infrastructure.persistence.repositories.dataset import SqlAlchemyDatasetRepository

router = APIRouter(prefix="/experiments", tags=["Experiments"])

def get_experiment_usecase(request: Request) -> CreateExperimentUseCase:
    session_maker = request.app.state.sessionmaker
    # We create a new session for the request scope. 
    # Note: In a real app, we'd use a dependency that yields the session and closes it.
    # For now, we instantiate repositories with a fresh session context in the route handler or dependency.
    # To keep it simple and correct with `get_session_maker`, let's assume we get a session dependency.
    return None # Placeholder, see route implementation

from qdrant_bench.presentation.api.dependencies import get_session

@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    request: CreateExperimentRequest, 
    session: AsyncSession = Depends(get_session)
):
    experiment_repo = SqlAlchemyExperimentRepository(session)
    dataset_repo = SqlAlchemyDatasetRepository(session)
    use_case = CreateExperimentUseCase(experiment_repo, dataset_repo)
    
    command = CreateExperimentCommand(
        name=request.name,
        dataset_id=request.dataset_id,
        connection_id=request.connection_id,
        optimizer_config=request.optimizer_config,
        vector_config=request.vector_config
    )
    
    try:
        experiment = await use_case.execute(command)
        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            dataset_id=experiment.dataset_id,
            connection_id=experiment.connection_id,
            optimizer_config=experiment.optimizer_config,
            vector_config=experiment.vector_config
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("", response_model=List[ExperimentResponse])
async def list_experiments(session: AsyncSession = Depends(get_session)):
    experiment_repo = SqlAlchemyExperimentRepository(session)
    use_case = ListExperimentsUseCase(experiment_repo)
    experiments = await use_case.execute()
    
    return [
        ExperimentResponse(
            id=exp.id,
            name=exp.name,
            dataset_id=exp.dataset_id,
            connection_id=exp.connection_id,
            optimizer_config=exp.optimizer_config,
            vector_config=exp.vector_config
        ) for exp in experiments
    ]
