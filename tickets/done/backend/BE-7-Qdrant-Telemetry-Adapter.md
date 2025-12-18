# BE-7: Qdrant Telemetry Adapter

**Role**: Backend Engineer
**Context**: The LLM Judge needs system-level metrics (RAM, CPU, Indexing Time) from the Qdrant cluster to make informed tuning decisions.

## Requirements

1. **Qdrant Metrics Adapter**:
   - Implement an adapter to fetch metrics from the Qdrant instance.
   - **Sources**:
     - **Qdrant Telemetry API**: `/telemetry` endpoint (if available/exposed).
     - **Qdrant Cloud API**: If cloud-hosted, use the Qdrant Cloud API to get cluster metrics (CPU/RAM usage).
     - **Client-Side Measurement**: Measure `indexing_time` by tracking the duration of the "Optimize" or "Index" step in the execution pipeline.
   - **Metrics to Collect**:
     - RAM Usage (absolute & percentage).
     - CPU Usage.
     - Disk Usage.
     - Indexing Duration (time taken to build HNSW).

2. **Integration with Execution Engine**:
   - Update `AI-1` (Experiment Execution Engine) to call this adapter during/after the run.
   - Store these captured metrics in the `Run` entity's `metrics` JSON field alongside search performance metrics (F1, QPS).

3. **Interface**:
   - Define a `ClusterMetricsService` port.
   - Methods: `get_cluster_stats(connection_id) -> ClusterStats`.

## Acceptance Criteria
- [ ] Adapter implemented to fetch cluster stats.
- [ ] Logic to measure client-side indexing duration.
- [ ] Metrics are correctly propagated to the `Run` result object.

