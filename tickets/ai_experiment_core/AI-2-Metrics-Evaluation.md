# AI-2: Metrics Evaluation

**Role**: Data Scientist / Engineer
**Context**: We need to measure the quality of the search results to score experiments.

## Requirements
1. **Evaluator Protocol**:
   - Define `Evaluator` Protocol in `src/qdrant_bench/ports/evaluator.py`.

2. **Metric Logic**:
   - Implement logic for standard retrieval metrics:
     - **Recall@K**: Proportion of relevant items retrieved in top K.
     - **Precision@K**: Proportion of retrieved items that are relevant in top K.
     - **F1 Score**: Harmonic mean of Precision and Recall.
     - **QPS**: Queries Per Second (derived from total duration / num queries).
     - **Latency**: Calculate p50, p95, p99 latency from per-query timings.

3. **Input/Output**:
   - Input: `WorkloadResult` (containing predictions and timings) vs `GroundTruth` (from Dataset).
   - Output: Dictionary of scores (e.g., `{"recall_at_10": 0.95, "p95_latency": 0.02}`).

## Acceptance Criteria
- [ ] Metric calculation functions implemented and unit tested.
- [ ] `Evaluator` service implemented taking results and outputting scores.
- [ ] Integration with the Execution Engine to compute scores after a run.
