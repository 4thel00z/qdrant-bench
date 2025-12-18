# BE-6: Telemetry & Structured Logging

**Role**: Backend/DevOps Engineer
**Context**: Implement observability for the system to track performance, debug issues, and monitor experiment execution.

## Requirements

1. **Structured Logging & Telemetry**:
   - Use **Logfire** (by Pydantic) for both structured logging and tracing.
   - Leverage Logfire's native integration with **Pydantic AI** to automatically track LLM calls, prompts, and completions.
   - Configure Logfire to output structured JSON logs in production and pretty-printed logs in development.
   - Ensure auto-instrumentation for FastAPI and Pydantic models.

2. **Tracing / Telemetry**:
   - Logfire is built on **OpenTelemetry (OTEL)**, so ensure standard OTEL export capability is preserved if needed (e.g., to external collectors).
   - Instrument HTTP clients (httpx/openai) and DB drivers (asyncpg/SQLModel) via Logfire's instrumentation helpers.
   - Export traces to Logfire's platform (if configured) or standard OTLP destinations.

3. **Metrics**:
   - Use Logfire or standard OTEL metrics for application performance monitoring.
   - Expose system and application metrics (request latency, experiment duration, Qdrant operation stats).

4. **Integration**:
   - Create a `telemetry` adapter/module in `infrastructure/`.
   - Middleware in FastAPI to initialize trace context.

## Acceptance Criteria
- [ ] `logfire` configured and integrated with FastAPI.
- [ ] Pydantic AI LLM calls automatically traced by Logfire.
- [ ] Logs contain correlation IDs.

