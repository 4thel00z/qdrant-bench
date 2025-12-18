# Project Plan: Qdrant Bench

## Overview
This project is an automated benchmarking and optimization system for Qdrant on Qdrant Cloud. It uses an "Experimentation Loop" to run sweeps, evaluate results, and evolve configurations using both Rule-based and LLM-based agents.

## Architecture
- **Pattern**: Hexagonal Architecture (DDD).
- **Backend**: Python (FastAPI, Typer), `uv` package manager, Async-first.
- **Persistence**: PostgreSQL (via `asyncpg` and `SQLAlchemy` core) managing Experiments, Runs, Connections, and Datasets.
- **Frontend**: ReactJS (CDN), TailwindCSS v4, Chart.js.
- **Infrastructure**: Terraform for Qdrant Cloud.
- **AI**: Pydantic AI (LLM Judge).

## Modules & Tickets

### Backend (`tickets/done/` or `tickets/backend/`)
- [x] [BE-1](tickets/backend/BE-1-Project-Scaffold.md): Project Scaffolding & Architecture.
- [x] [BE-2](tickets/backend/BE-2-IAC-Core.md): IAC Core (Qdrant Cloud Terraform).
- [x] [BE-3](tickets/backend/BE-3-Encoding-Client.md): Encoding Client Adapter.
- [x] [BE-4](tickets/backend/BE-4-API-Design.md): API Layer & Experiment Management.
- [x] [BE-5](tickets/backend/BE-5-Persistence-Core.md): Persistence Core & Domain Entities.
- [x] [BE-6](tickets/backend/BE-6-Telemetry-Logging.md): Telemetry & Structured Logging.
- [x] [BE-7](tickets/backend/BE-7-Qdrant-Telemetry-Adapter.md): Qdrant Telemetry Adapter (Metrics for LLM).

### AI / Experiment Core (`tickets/ai_experiment_core/`)
- [ ] [AI-1](tickets/ai_experiment_core/AI-1-Experiment-Execution-Engine.md): Experiment Execution Engine.
- [ ] [AI-2](tickets/ai_experiment_core/AI-2-Metrics-Evaluation.md): Metrics Evaluation.
- [ ] [AI-3](tickets/ai_experiment_core/AI-3-Experiment-Generation-Rules.md): Experiment Generation (Rule-Based).
- [ ] [AI-4](tickets/ai_experiment_core/AI-4-Experiment-Generation-LLM.md): Experiment Generation (LLM Judge).
- [ ] [AI-5](tickets/ai_experiment_core/AI-5-Workload-Definitions.md): Workload Definitions.

### Frontend (`tickets/frontend/`)
- [ ] [FE-1](tickets/frontend/FE-1-Report-Generator.md): Report Generator.
- [ ] [FE-2](tickets/frontend/FE-2-Charts-Visualization.md): Charts Visualization.
- [ ] [FE-3](tickets/frontend/FE-3-Dashboard-UI.md): Dashboard UI.

## Getting Started
1. **Review Architecture**: Read `Agent.md` and `.cursorrules`.
2. **Backend Setup**: Start with `BE-1` to set up the Python environment.
3. **Persistence**: Implement `BE-5` to set up the database and entities.
4. **Infrastructure**: Configure Terraform credentials for `BE-2`.
5. **Core Logic**: Implement the Execution Engine (`AI-1`).
