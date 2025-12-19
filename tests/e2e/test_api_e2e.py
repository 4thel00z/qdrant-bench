import time
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest

from tests.e2e.data_factory import write_tiny_single_vector_dataset


def wait_for_run_completion(*, base_url: str, run_id: UUID, timeout_s: float) -> dict:
    deadline = time.monotonic() + timeout_s
    url = f"{base_url}/api/v1/runs/{run_id}"

    while time.monotonic() < deadline:
        response = httpx.get(url, timeout=2.0)
        response.raise_for_status()
        body = response.json()
        status = body.get("status")

        if status == "COMPLETED":
            return body

        if status == "FAILED":
            raise AssertionError(f"Run failed: {body}")

        time.sleep(0.5)

    raise TimeoutError(f"Timed out waiting for run {run_id} to complete")


@pytest.mark.e2e
def test_api_e2e_single_node_qdrant(tmp_path: Path, api_server: str) -> None:
    embedding_dim = 384
    dataset_parquet_path = write_tiny_single_vector_dataset(
        target_dir=tmp_path,
        embedding_dim=embedding_dim,
    )

    dataset_name = f"e2e-dataset-{uuid4().hex[:8]}"
    connection_name = f"e2e-connection-{uuid4().hex[:8]}"
    experiment_name = f"e2e-experiment-{uuid4().hex[:8]}"

    dataset_response = httpx.post(
        f"{api_server}/api/v1/datasets",
        json={
            "name": dataset_name,
            "source_uri": str(dataset_parquet_path),
            "schema_config": {"vector": {"dim": embedding_dim}},
        },
        timeout=10.0,
    )
    dataset_response.raise_for_status()
    dataset_id = UUID(dataset_response.json()["id"])

    connection_response = httpx.post(
        f"{api_server}/api/v1/connections",
        json={
            "name": connection_name,
            "url": "http://127.0.0.1:6335",
            "api_key": "",
        },
        timeout=10.0,
    )
    connection_response.raise_for_status()
    connection_id = UUID(connection_response.json()["id"])

    experiment_response = httpx.post(
        f"{api_server}/api/v1/experiments",
        json={
            "name": experiment_name,
            "dataset_id": str(dataset_id),
            "connection_id": str(connection_id),
            "optimizer_config": {"k": 3, "query_count": 2, "indexing_threshold": 0},
            "vector_config": {"size": embedding_dim, "distance": "COSINE"},
        },
        timeout=10.0,
    )
    experiment_response.raise_for_status()
    experiment_id = UUID(experiment_response.json()["id"])

    run_response = httpx.post(
        f"{api_server}/api/v1/experiments/{experiment_id}/runs",
        timeout=10.0,
    )
    assert run_response.status_code == 202, run_response.text
    run_id = UUID(run_response.json()["id"])

    completed_run = wait_for_run_completion(base_url=api_server, run_id=run_id, timeout_s=90.0)

    metrics = completed_run.get("metrics", {})
    assert "recall" in metrics, metrics
    assert metrics["recall"] > 0.0, metrics
    assert "p95_latency" in metrics, metrics
    assert "qps" in metrics, metrics
