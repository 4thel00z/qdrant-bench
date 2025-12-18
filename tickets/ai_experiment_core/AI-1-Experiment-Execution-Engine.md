# AI-1: Experiment Execution Engine (Orchestrator)

**Role**: AI/Core Engineer
**Context**: The heart of the system. It orchestrates the lifecycle of an experiment.

## Requirements
1. **Orchestration Logic**:
   - Create `ExecuteExperimentUseCase` in `src/qdrant_bench/application/usecases/experiments/execute.py`.
   - **Flow**:
     1. **Provision**: Use `QdrantCloudAdapter` (BE-2) to get/create instance.
     2. **Configure**: Apply `Experiment.optimizer_config` and `vector_config` to Qdrant.
        - *Use strict `qdrant_client.models` for HnswConfig, OptimizersConfig, etc.*
     3. **Seed**: Use `EncodingService` (BE-3) to embed data from `Dataset`.
     4. **Workload**: Execute `AI-5` Workload.
     5. **Evaluate**: Run `AI-2` Evaluator.
     6. **Telemetry**: Capture `AI-7` System Metrics (RAM, CPU).
     7. **Persist**: Update `Run` entity in DB with status and metrics.

2. **Qdrant Configuration**:
   - Support complex configs (Multi-vector, quantization).
   - Example:
     ```python
     vectors_config={
         "text": models.VectorParams(size=1536, distance=models.Distance.COSINE),
         "image": models.VectorParams(size=512, distance=models.Distance.EUCLIDEAN)
     }
     ```

3. **Integration**:
   - Integrate with all previously built adapters (Cloud, Encoding, Telemetry).

## Acceptance Criteria
- [ ] `ExecuteExperimentUseCase` implemented.
- [ ] End-to-end execution flow works (mocked or real).
- [ ] Database reflects final state (COMPLETED) and metrics.
