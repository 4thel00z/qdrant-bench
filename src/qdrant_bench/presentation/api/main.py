import os
from contextlib import asynccontextmanager

import logfire
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from qdrant_bench.infrastructure.persistence.database import create_db_engine, get_session_maker, init_db
from qdrant_bench.infrastructure.telemetry import configure_logging
from qdrant_bench.presentation.api.routes import connections, datasets, experiments, reports, runs, storage, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    logfire.info("Starting Qdrant Bench API")

    # Initialize Database Engine explicitly and store in app.state
    engine = create_db_engine()
    await init_db(engine)
    app.state.engine = engine
    app.state.sessionmaker = get_session_maker(engine)

    logfire.info("Database initialized")
    yield

    # Cleanup
    await engine.dispose()
    logfire.info("Stopping Qdrant Bench API")

app = FastAPI(title="Qdrant Bench API", version="v1", lifespan=lifespan)

configure_logging(app)

# Mount API Routes
app.include_router(connections.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(storage.router, prefix="/api/v1")
app.include_router(experiments.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(system.router)

# Mount Static Files for Dashboard (FE-3)
# Note: We use absolute path relative to this file to ensure it works regardless of CWD
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "../static")
app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")

def main():
    configure_logging(app)
    uvicorn.run("qdrant_bench.presentation.api.main:app", host="0.0.0.0", port=1337, reload=True)

if __name__ == "__main__":
    main()
