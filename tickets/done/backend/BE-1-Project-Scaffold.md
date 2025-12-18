# BE-1: Project Scaffolding & Architecture

**Role**: Backend Engineer
**Context**: Initial setup of the Python project following Hexagonal Architecture and DDD.

## Requirements
1. Initialize a Python project (3.14+ target).
2. Define the folder structure:
   - `domain/`: Core business logic and entities (Enterprise Business Rules).
   - `application/`: Application business rules, use cases.
     - `usecases/`: Application specific business rules.
   - `ports/`: Interfaces (Protocols) for input/output (can be split into inbound/outbound or kept central).
   - `presentation/`: Primary Adapters (Driving side).
     - `api/`: FastAPI implementation.
     - `cli/`: Typer implementation.
   - `infrastructure/`: Secondary Adapters (Driven side).
     - `iac/`: Terraform/Cloud management.
     - `services/`: External services (e.g., Encoding).
   - `main.py`: Entrypoint.
3. Configure dependencies (FastAPI, Typer, Pydantic) using `uv` as the package manager and `hatchling` as the build backend.
4. Enforce architectural rules:
   - No `abc` package.
   - No underscore prefixes.
   - Async first.

## Acceptance Criteria
- [ ] Project structure created with `domain`, `application`, `presentation`, and `infrastructure` layers.
- [ ] `pyproject.toml` set up with `hatchling` build backend (initialized via `uv`).
- [ ] Basic Hello World FastAPI endpoint works (in `presentation/api`).
- [ ] Basic Hello World Typer CLI command works (in `presentation/cli`).
- [ ] Linter/Formatter config reflects "Imports on top" and other rules.
