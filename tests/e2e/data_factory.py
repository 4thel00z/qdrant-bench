from pathlib import Path

import polars as pl

from qdrant_bench.infrastructure.services.deterministic_embedding import deterministic_vector


def write_tiny_single_vector_dataset(
    *,
    target_dir: Path,
    embedding_dim: int,
) -> Path:
    corpus_path = target_dir / "corpus.parquet"
    queries_path = target_dir / "corpus.queries.parquet"
    ground_truth_path = target_dir / "corpus.ground_truth.parquet"

    texts = [
        "e2e-doc-0",
        "e2e-doc-1",
        "e2e-doc-2",
    ]

    pl.DataFrame({"text": texts}).write_parquet(str(corpus_path))

    query_vectors = [
        deterministic_vector(text=texts[0], embedding_dim=embedding_dim),
        deterministic_vector(text=texts[1], embedding_dim=embedding_dim),
    ]
    pl.DataFrame({"vector": query_vectors}).write_parquet(str(queries_path))

    ground_truth = [
        {"query_id": 0, "relevant_ids": [0]},
        {"query_id": 1, "relevant_ids": [1]},
    ]
    pl.DataFrame(ground_truth).write_parquet(str(ground_truth_path))

    return corpus_path
