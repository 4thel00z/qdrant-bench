from fastapi import APIRouter, Depends, HTTPException

from qdrant_bench.application.usecases.experiments.create import (
    CreateExperimentCommand,
    CreateExperimentUseCase,
    ListExperimentsUseCase,
)
from qdrant_bench.presentation.api.dependencies import get_create_experiment_usecase, get_list_experiments_usecase
from qdrant_bench.presentation.api.dtos.models import CreateExperimentRequest, ExperimentResponse

router = APIRouter(prefix="/experiments", tags=["Experiments"])


@router.post("", status_code=201)
async def create_experiment(
    request: CreateExperimentRequest, use_case: CreateExperimentUseCase = Depends(get_create_experiment_usecase)
):
    command = CreateExperimentCommand(
        name=request.name,
        dataset_id=request.dataset_id,
        connection_id=request.connection_id,
        optimizer_config=request.optimizer_config,
        vector_config=request.vector_config,
    )

    try:
        experiment = await use_case.execute(command)
        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            dataset_id=experiment.dataset_id,
            connection_id=experiment.connection_id,
            optimizer_config=experiment.optimizer_config,
            vector_config=experiment.vector_config,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("")
async def list_experiments(use_case: ListExperimentsUseCase = Depends(get_list_experiments_usecase)):
    experiments = await use_case.execute()

    return [
        ExperimentResponse(
            id=exp.id,
            name=exp.name,
            dataset_id=exp.dataset_id,
            connection_id=exp.connection_id,
            optimizer_config=exp.optimizer_config,
            vector_config=exp.vector_config,
        )
        for exp in experiments
    ]
