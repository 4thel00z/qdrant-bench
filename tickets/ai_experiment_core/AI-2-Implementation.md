# AI-2: Metrics Evaluator (Implementation)

**Role**: Data Scientist / Engineer
**Context**: Implement the scoring logic for experiments.

## Requirements
1. **Evaluator Service**:
   - Class: `StandardEvaluator` in `src/qdrant_bench/domain/services/evaluator.py`.
   - Protocol: `Evaluator` in `ports`.

2. **Metric Logic**:
   - **Recall**: Intersection of retrieved vs relevant / total relevant.
   - **Precision**: Intersection / total retrieved.
   - **F1**: 2 * (P * R) / (P + R).
   - **Latency**: numpy `percentile` (50, 95, 99).
   - **QPS**: Total Queries / Total Time.

## Acceptance Criteria
- [ ] `StandardEvaluator` fully implemented.
- [ ] Unit tests covering edge cases (e.g. empty results, divide by zero).

