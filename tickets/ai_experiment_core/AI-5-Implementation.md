# AI-5: Workload Definitions (Implementation)

**Role**: AI/Core Engineer
**Context**: Implement the actual search execution logic.

## Requirements
1. **Workload Protocol**:
   - Defined in `src/qdrant_bench/ports/workload.py`.

2. **SingleVectorWorkload**:
   - Logic: Standard `client.search()`.
   - Queries: Should ideally come from a dataset adapter. For MVP, simple random generation or fixed list is acceptable if documented.

3. **MultiVectorWorkload**:
   - Logic: Handle `NamedVector` queries or batch search if simulating concurrent users.

## Acceptance Criteria
- [ ] `SingleVectorWorkload` implemented.
- [ ] `MultiVectorWorkload` implemented.
- [ ] Integration with `ExecuteExperimentUseCase`.

