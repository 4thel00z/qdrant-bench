# BE-5: Persistence Core & Domain Entities

**Role**: Backend Engineer
**Context**: Implement the persistence layer using PostgreSQL and define core domain entities with strict validation.

## Requirements

1. **Persistence Stack**:
   - Database: **PostgreSQL** (running in Docker or external).
   - Driver: **asyncpg**.
   - ORM: **SQLModel** (provides Pydantic validation + SQLAlchemy core).

2. **Schema Management**:
   - **No Migrations**: Do not use Alembic.
   - On application startup, check if tables exist; if not, create them:
     ```python
     async with engine.begin() as conn:
         await conn.run_sync(SQLModel.metadata.create_all)
     ```

3. **Domain Entities & Schemas**:
   Define these SQLModel classes (table=True):

   - **Connection**: Stores Qdrant Cloud credentials.
     - `id`: UUID (PK)
     - `name`: str (unique)
     - `url`: str
     - `api_key`: str (encrypted or masked in logs)

   - **ObjectStorage**: configuration for S3/MinIO.
     - `id`: UUID (PK)
     - `bucket`: str
     - `region`: str
     - `endpoint_url`: str
     - `access_key`: str
     - `secret_key`: str

   - **Dataset**: References a dataset for experiments.
     - `id`: UUID (PK)
     - `name`: str
     - `source_uri`: str (s3://... or https://...)
     - `schema_config`: JSON (Pydantic model) - defines scalar fields and vector fields.
       - *Multi-Vector Support*: `schema_config` must describe if there are named vectors (e.g., `{"text": 768, "image": 512}`) or a single dense vector.

   - **Experiment**: Defines the template for a benchmark.
     - `id`: UUID (PK)
     - `name`: str
     - `dataset_id`: UUID (FK to Dataset)
     - `connection_id`: UUID (FK to Connection)
     - `optimizer_config`: JSON - Qdrant specific settings (indexing, HNSW params, quantization).
     - `vector_config`: JSON - configuration for the collection (distance, dimensionality). *Must align with Dataset schema*.

   - **Run**: A specific execution of an Experiment.
     - `id`: UUID (PK)
     - `experiment_id`: UUID (FK to Experiment)
     - `status`: Enum (CREATED, RUNNING, COMPLETED, FAILED, CANCELED)
     - `start_time`: datetime
     - `end_time`: datetime
     - `metrics`: JSON - Resulting scores (F1, Precision, Latency, QPS).

4. **Validation Layer**:
   - Use **Pydantic** validation methods (`@validator` or `@field_validator`) on the SQLModels or separate DTOs.
   - **Strict Schema Validation**:
     - Ensure `Experiment.vector_config` matches `Dataset.schema_config`.
     - E.g. if Dataset has vectors `{"dense": 1536}`, Experiment cannot try to index a vector named `embedding` with dim 768.

## Acceptance Criteria
- [ ] PostgreSQL container/service reachable.
- [ ] SQLModel entities defined for all the above.
- [ ] Application startup creates tables automatically.
- [ ] Repository adapters implemented for CRUD operations.
- [ ] Validation logic ensures Experiment <-> Dataset compatibility, including multi-vector checks.

