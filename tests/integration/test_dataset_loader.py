"""Integration tests for dataset loader functions"""
from qdrant_bench.infrastructure.persistence.dataset_loader import (
    derive_ground_truth_uri,
    derive_query_uri,
    parse_s3_uri,
)
from tests.integration.fixtures import create_multi_vector_dataset, create_test_dataset


def test_derive_query_uri_from_parquet():
    """Derives query file from parquet corpus"""
    source_uri = "s3://bucket/data/corpus.parquet"

    query_uri = derive_query_uri(source_uri)

    assert query_uri == "s3://bucket/data/corpus.queries.parquet"


def test_derive_query_uri_from_http():
    """Derives query file from HTTP source"""
    source_uri = "https://example.com/data/corpus.parquet"

    query_uri = derive_query_uri(source_uri)

    assert query_uri == "https://example.com/data/corpus.queries.parquet"


def test_derive_query_uri_from_local():
    """Derives query file from local path"""
    source_uri = "/data/corpus.parquet"

    query_uri = derive_query_uri(source_uri)

    assert query_uri == "/data/corpus.queries.parquet"


def test_derive_ground_truth_uri_from_parquet():
    """Derives ground truth file from parquet corpus"""
    source_uri = "s3://bucket/data/corpus.parquet"

    gt_uri = derive_ground_truth_uri(source_uri)

    assert gt_uri == "s3://bucket/data/corpus.ground_truth.parquet"


def test_derive_ground_truth_uri_preserves_path():
    """Preserves complex path structure"""
    source_uri = "s3://my-bucket/datasets/v2/experiment-1/corpus.parquet"

    gt_uri = derive_ground_truth_uri(source_uri)

    assert gt_uri == "s3://my-bucket/datasets/v2/experiment-1/corpus.ground_truth.parquet"


def test_parse_s3_uri_simple():
    """Parses simple S3 URI"""
    s3_uri = "s3://my-bucket/file.parquet"

    bucket, key = parse_s3_uri(s3_uri)

    assert bucket == "my-bucket"
    assert key == "file.parquet"


def test_parse_s3_uri_nested_path():
    """Parses S3 URI with nested paths"""
    s3_uri = "s3://my-bucket/path/to/data/file.parquet"

    bucket, key = parse_s3_uri(s3_uri)

    assert bucket == "my-bucket"
    assert key == "path/to/data/file.parquet"


def test_parse_s3_uri_bucket_only():
    """Parses S3 URI with bucket and single file"""
    s3_uri = "s3://bucket/data.parquet"

    bucket, key = parse_s3_uri(s3_uri)

    assert bucket == "bucket"
    assert key == "data.parquet"


def test_dataset_fixture_has_valid_schema():
    """Dataset fixtures have complete schema"""
    dataset = create_test_dataset()

    assert "vector" in dataset.schema_config
    assert "dim" in dataset.schema_config["vector"]
    assert dataset.schema_config["vector"]["dim"] == 384


def test_multi_vector_dataset_fixture_has_valid_schema():
    """Multi-vector dataset fixture has complete schema"""
    dataset = create_multi_vector_dataset()

    assert "vectors" in dataset.schema_config
    assert "text" in dataset.schema_config["vectors"]
    assert "image" in dataset.schema_config["vectors"]
    assert dataset.schema_config["vectors"]["text"]["dim"] == 384
    assert dataset.schema_config["vectors"]["image"]["dim"] == 512



