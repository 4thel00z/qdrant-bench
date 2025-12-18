# AI-5: Workload Definitions (Base Layer)

**Role**: AI/Core Engineer
**Context**: Experiments run different types of searches (Single Vector, Multi-Vector, Hybrid). We need a unified way to execute these.

## Requirements
1. **Workload Protocol**:
   - Define `Workload` Protocol in `src/qdrant_bench/ports/workload.py`.
   - Method signature:
     ```python
     async def execute(self, client: QdrantClient, dataset: Dataset, config: WorkloadConfig) -> WorkloadResult: ...
     ```

2. **Concrete Implementations**:
   - Implement `SingleVectorWorkload` in `src/qdrant_bench/infrastructure/workloads/single_vector.py`.
     - Should handle standard dense vector search.
   - Implement `MultiVectorWorkload` in `src/qdrant_bench/infrastructure/workloads/multi_vector.py`.
     - Should handle multi-vector search (e.g., ColBERT style late interaction or hybrid dense+sparse).

3. **Qdrant Integration**:
   - Use the `qdrant-client` async client.
   - Ensure handling of connection parameters passed from the `Experiment` config.

## Acceptance Criteria
- [ ] `Workload` Protocol defined in ports.
- [ ] `SingleVectorWorkload` implemented and unit tested.
- [ ] `MultiVectorWorkload` implemented and unit tested.
- [ ] Can run a search against a live Qdrant instance (integration test).
