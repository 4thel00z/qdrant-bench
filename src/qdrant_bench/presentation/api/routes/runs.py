from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_bench.presentation.api.dtos.models import RunResponse
from qdrant_bench.domain.entities.core import RunStatus
from qdrant_bench.application.usecases.runs.trigger import TriggerRunUseCase, TriggerRunCommand, ListRunsUseCase, GetRunUseCase
from qdrant_bench.infrastructure.persistence.repositories.run import SqlAlchemyRunRepository
from qdrant_bench.infrastructure.persistence.repositories.experiment import SqlAlchemyExperimentRepository
import logfire

router = APIRouter(tags=["Runs"])

from qdrant_bench.presentation.api.dependencies import get_session

async def execute_run_task(run_id: UUID):
    # Placeholder for actual execution logic (AI-1)
    logfire.info(f"Starting execution for Run ID: {run_id}")
    pass

@router.post("/experiments/{experiment_id}/runs", response_model=RunResponse, status_code=202)
async def trigger_run(
    experiment_id: UUID, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    run_repo = SqlAlchemyRunRepository(session)
    experiment_repo = SqlAlchemyExperimentRepository(session)
    use_case = TriggerRunUseCase(run_repo, experiment_repo)
    
    command = TriggerRunCommand(experiment_id=experiment_id)
    
    try:
        run = await use_case.execute(command)
        background_tasks.add_task(execute_run_task, run.id)
        return RunResponse(
            id=run.id,
            experiment_id=run.experiment_id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            metrics=run.metrics
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/runs", response_model=List[RunResponse])
async def list_runs(
    experiment_id: Optional[UUID] = None, 
    status: Optional[RunStatus] = None, 
    session: AsyncSession = Depends(get_session)
):
    run_repo = SqlAlchemyRunRepository(session)
    use_case = ListRunsUseCase(run_repo)
    
    runs = await use_case.execute(experiment_id, status)
    return [
        RunResponse(
            id=r.id,
            experiment_id=r.experiment_id,
            status=r.status,
            start_time=r.start_time,
            end_time=r.end_time,
            metrics=r.metrics
        ) for r in runs
    ]

@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: UUID, session: AsyncSession = Depends(get_session)):
    run_repo = SqlAlchemyRunRepository(session)
    use_case = GetRunUseCase(run_repo)
    
    run = await use_case.execute(run_id)
    if run:
        return RunResponse(
            id=run.id,
            experiment_id=run.experiment_id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            metrics=run.metrics
        )
    raise HTTPException(status_code=404, detail="Run not found")
