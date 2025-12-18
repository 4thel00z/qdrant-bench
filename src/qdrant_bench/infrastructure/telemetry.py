import logfire
from fastapi import FastAPI

def configure_logging(app: FastAPI):
    logfire.configure()
    logfire.instrument_fastapi(app)
    logfire.info("Telemetry initialized")

