import os
import uvicorn
import logfire
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from qdrant_bench.infrastructure.persistence.database import init_db, create_db_engine, get_session_maker
from qdrant_bench.presentation.api.routes import connections, datasets, storage, experiments, runs
from qdrant_bench.infrastructure.telemetry import configure_logging

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

app.include_router(connections.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(storage.router, prefix="/api/v1")
app.include_router(experiments.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

def main():
    configure_logging(app)
    uvicorn.run("qdrant_bench.presentation.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
