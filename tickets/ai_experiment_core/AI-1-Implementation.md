Create # AI-1: Experiment Execution Engine (Implementation)

**Role**: AI/Core Engineer
**Context**: This ticket covers the implementation of the `ExecuteExperimentUseCase`, which is the core orchestrator for running benchmarks.

## Requirements
1. **UseCase Implementation**:
   - Class: `ExecuteExperimentUseCase` in `src/qdrant_bench/application/usecases/experiments/execute.py`.
   - Dependencies: `RunRepository`, `ExperimentRepository`, `DatasetRepository`, `ConnectionRepository`, `EmbeddingService`, `QdrantTelemetryAdapter`.

2. **Execution Flow**:
   - **Load Entities**: Fetch Run, Experiment, Dataset, Connection by ID.
   - **Connect**: Initialize `AsyncQdrantClient`.
   - **Provision/Reset**: Ensure collection exists. *Note: For MVP, assume collection is ready or use `recreate_collection` if `optimizer_config` implies a fresh start.*
   - **Seed**: 
     - If dataset is raw text, use `EmbeddingService` to generate vectors.
     - If dataset is pre-computed (e.g. .npy/.parquet), load directly.
     - Batch upsert to Qdrant.
   - **Workload**:
     - Instantiate `SingleVectorWorkload` or `MultiVectorWorkload` based on `vector_config`.
     - Run `workload.execute()`.
   - **Evaluate**:
     - Calculate metrics using `StandardEvaluator`.
   - **Telemetry**:
     - Fetch cluster stats via `QdrantTelemetryAdapter`.
   - **Persist**:
     - Save metrics and status to `Run`.

## Acceptance Criteria
- [ ] Use Case implemented.
- [ ] Seeding logic handles at least one data source type (e.g. synthetic or text list).
- [ ] Workload execution is triggered.
- [ ] Results are saved to DB.

