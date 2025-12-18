# BE-4: API Layer & Experiment Management

**Role**: Backend Engineer
**Context**: Expose the functionality via a RESTful API using FastAPI. Provide strict schema validation and support for complex multi-vector workloads.

## Requirements

### General Guidelines
1. **Versioning**: All paths must start with `/api/v1`.
2. **Naming**: Kebab-case resources (`/experiments`, `/runs`).
3. **Async**: Use `async def` handlers.
4. **Status Codes**:
   - `200 OK` for synchronous success.
   - `201 Created` for resource creation.
   - `202 Accepted` for triggering async jobs (runs).
   - `204 No Content` for deletions.
   - `404 Not Found`, `422 Validation Error`.

### Endpoints

#### 1. Connections
- **GET /api/v1/connections**
  - **Summary**: List all Qdrant connections.
  - **Response**: `[{"id": "...", "name": "Prod Cluster", "url": "..."}]`
- **POST /api/v1/connections**
  - **Summary**: Register a new Qdrant connection.
  - **Payload**:
    ```json
    {
      "name": "Dev Cluster",
      "url": "https://xyz.qdrant.io:6333",
      "api_key": "th3-s3cr3t-k3y"
    }
    ```

#### 2. Object Storage
- **GET /api/v1/storage**
  - **Summary**: List storage configurations.
- **POST /api/v1/storage**
  - **Summary**: Add S3/MinIO credentials.
  - **Payload**:
    ```json
    {
      "bucket": "qdrant-bench-data",
      "endpoint_url": "https://s3.us-east-1.amazonaws.com",
      "access_key": "...",
      "secret_key": "..."
    }
    ```

#### 3. Datasets
- **POST /api/v1/datasets**
  - **Summary**: Register a dataset reference.
  - **Description**: Define the schema of the dataset, including multi-vector capabilities.
  - **Payload (Multi-Vector Example)**:
    ```json
    {
      "name": "Wiki-Multimodal",
      "source_uri": "s3://datasets/wiki-mm.parquet",
      "schema_config": {
        "scalar_fields": ["title", "url"],
        "vectors": {
          "text_embedding": { "dim": 768, "distance": "Cosine" },
          "image_embedding": { "dim": 512, "distance": "Euclidean" }
        }
      }
    }
    ```

#### 4. Experiments
- **POST /api/v1/experiments**
  - **Summary**: Define a new benchmark experiment (template).
  - **Description**: Validates that the `vector_config` is compatible with the referenced `dataset_id`.
  - **Payload (Multi-Vector Optimization)**:
    ```json
    {
      "name": "HNSW Tuning - MultiVector",
      "dataset_id": "uuid-of-wiki-mm",
      "connection_id": "uuid-of-dev-cluster",
      "optimizer_config": {
        "indexing": {
          "text_embedding": { "type": "hnsw", "m": 16, "ef_construct": 100 },
          "image_embedding": { "type": "hnsw", "m": 32, "ef_construct": 200 }
        },
        "quantization": { "scalar": "int8" }
      }
    }
    ```

#### 5. Runs
- **POST /api/v1/experiments/{id}/runs**
  - **Summary**: Trigger an execution of an experiment.
  - **Response**: `202 Accepted` with `{"run_id": "..."}`.
- **GET /api/v1/runs**
  - **Summary**: List past runs with basic metrics.
  - **Query Params**: `?experiment_id=...&status=COMPLETED`
- **GET /api/v1/runs/{id}**
  - **Summary**: Get detailed status and results of a run.
  - **Response**:
    ```json
    {
      "id": "...",
      "status": "COMPLETED",
      "metrics": {
        "f1": 0.85,
        "p_95_latency": 0.045,
        "qps": 1200
      }
    }
    ```

## Acceptance Criteria
- [ ] All endpoints implemented using FastAPI `APIRouter`.
- [ ] Request bodies backed by Pydantic models with examples.
- [ ] Validation logic ensures `Experiment` matches `Dataset` schema before creation.
- [ ] "Run" triggering is async (just creates the record and dispatches task).
