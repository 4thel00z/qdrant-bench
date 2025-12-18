from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from qdrant_bench.application.usecases.reports.generate import GenerateReportUseCase
from qdrant_bench.presentation.api.dependencies import get_generate_report_usecase

router = APIRouter(tags=["Reports"])

@router.get("/reports/{experiment_id}", response_class=HTMLResponse)
async def view_report(
    experiment_id: str,
    use_case: GenerateReportUseCase = Depends(get_generate_report_usecase)
):
    try:
        exp_uuid = UUID(experiment_id)
    except ValueError:
        return HTMLResponse("Invalid UUID", status_code=400)

    report_html = await use_case.execute(exp_uuid)

    if not report_html:
        return HTMLResponse("Experiment not found", status_code=404)

    return HTMLResponse(content=report_html, status_code=200)
