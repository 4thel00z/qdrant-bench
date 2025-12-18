import logfire
from fastapi import FastAPI


def configure_logging(app: FastAPI):
    # Use simple console logging for local development if not authenticated
    try:
        logfire.configure()
        logfire.instrument_fastapi(app)
        logfire.info("Telemetry initialized")
    except Exception:
        print("Logfire authentication failed. Continuing without remote telemetry.")
