from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["System"])


@router.get("/")
async def root():
    return RedirectResponse(url="/dashboard/index.html")


@router.get("/api/health")
async def health():
    return {"status": "ok"}
