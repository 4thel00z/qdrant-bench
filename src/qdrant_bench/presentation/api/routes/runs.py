from uuid import UUID

import logfire
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from qdrant_bench.application.usecases.runs.trigger import (
    GetRunUseCase,
    ListRunsUseCase,
    TriggerRunCommand,
    TriggerRunUseCase,
)
from qdrant_bench.domain.entities.core import RunStatus
from qdrant_bench.presentation.api.dependencies import (
    get_execute_experiment_usecase,
    get_get_run_usecase,
    get_list_runs_usecase,
    get_trigger_run_usecase,
)
from qdrant_bench.presentation.api.dtos.models import RunResponse

router = APIRouter(tags=["Runs"])


async def execute_run_task(run_id: UUID, request: Request):
    logfire.info(f"Starting execution for Run ID: {run_id}")

    # We manually construct the session and dependencies for the background task
    # because `Depends` only works in the request-response cycle context.
    session_maker = request.app.state.sessionmaker

    async with session_maker() as session:
        # Use the factory function to get the use case with all dependencies wired
        use_case = get_execute_experiment_usecase(session)

        await use_case.execute(run_id)


@router.post("/experiments/{experiment_id}/runs", status_code=202)
async def trigger_run(
    experiment_id: UUID,
    background_tasks: BackgroundTasks,
    request: Request,
    use_case: TriggerRunUseCase = Depends(get_trigger_run_usecase),
):
    command = TriggerRunCommand(experiment_id=experiment_id)

    try:
        run = await use_case.execute(command)
        # Pass request to task to access app state (sessionmaker)
        background_tasks.add_task(execute_run_task, run.id, request)

        return RunResponse(
            id=run.id,
            experiment_id=run.experiment_id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            metrics=run.metrics,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/runs")
async def list_runs(
    experiment_id: UUID | None = None,
    status: RunStatus | None = None,
    use_case: ListRunsUseCase = Depends(get_list_runs_usecase),
):
    runs = await use_case.execute(experiment_id, status)
    return [
        RunResponse(
            id=r.id,
            experiment_id=r.experiment_id,
            status=r.status,
            start_time=r.start_time,
            end_time=r.end_time,
            metrics=r.metrics,
        )
        for r in runs
    ]


@router.get("/runs/{run_id}")
async def get_run(run_id: UUID, use_case: GetRunUseCase = Depends(get_get_run_usecase)):
    run = await use_case.execute(run_id)
    if run:
        return RunResponse(
            id=run.id,
            experiment_id=run.experiment_id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            metrics=run.metrics,
        )
    raise HTTPException(status_code=404, detail="Run not found")
