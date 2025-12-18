"""Integration tests for experiment validation"""
from qdrant_bench.application.usecases.experiments.create import (
    validate_multi_vector,
    validate_single_vector,
    validate_vector_config_match,
)
from tests.integration.fixtures import create_multi_vector_dataset, create_test_dataset


def test_valid_single_vector_config():
    """Valid single vector config passes validation"""
    dataset = create_test_dataset()
    vector_config = {"size": 384, "distance": "COSINE"}

    error = validate_single_vector(vector_config, dataset.schema_config["vector"])

    assert error is None


def test_missing_size_field():
    """Missing size field returns error"""
    dataset = create_test_dataset()
    vector_config = {"distance": "COSINE"}

    error = validate_single_vector(vector_config, dataset.schema_config["vector"])

    assert error == "vector_config missing 'size' field"


def test_dimension_mismatch():
    """Dimension mismatch returns specific error"""
    dataset = create_test_dataset()
    vector_config = {"size": 768, "distance": "COSINE"}

    error = validate_single_vector(vector_config, dataset.schema_config["vector"])

    assert error == "Dimension mismatch: dataset expects 384, config has 768"


def test_matching_dimensions():
    """Matching dimensions pass validation"""
    dataset = create_test_dataset()
    vector_config = {"size": 384}

    error = validate_single_vector(vector_config, dataset.schema_config["vector"])

    assert error is None


def test_valid_multi_vector_config():
    """Valid multi-vector config passes validation"""
    dataset = create_multi_vector_dataset()
    vector_config = {
        "vectors": {
            "text": {"size": 384, "distance": "COSINE"},
            "image": {"size": 512, "distance": "EUCLIDEAN"}
        }
    }

    error = validate_multi_vector(vector_config, dataset.schema_config["vectors"])

    assert error is None


def test_missing_vectors_field():
    """Missing vectors field returns error"""
    dataset = create_multi_vector_dataset()
    vector_config = {"size": 384}

    error = validate_multi_vector(vector_config, dataset.schema_config["vectors"])

    assert error == "Multi-vector dataset requires 'vectors' in config"


def test_vector_not_in_dataset():
    """Vector not in dataset schema returns error"""
    dataset = create_multi_vector_dataset()
    vector_config = {
        "vectors": {
            "audio": {"size": 256, "distance": "COSINE"}
        }
    }

    error = validate_multi_vector(vector_config, dataset.schema_config["vectors"])

    assert error is not None
    assert "audio" in error
    assert "text, image" in error


def test_dimension_mismatch_specific_vector():
    """Dimension mismatch for specific vector returns detailed error"""
    dataset = create_multi_vector_dataset()
    vector_config = {
        "vectors": {
            "text": {"size": 768, "distance": "COSINE"},
            "image": {"size": 512, "distance": "EUCLIDEAN"}
        }
    }

    error = validate_multi_vector(vector_config, dataset.schema_config["vectors"])

    assert error is not None
    assert "text" in error
    assert "expected 384" in error
    assert "got 768" in error


def test_partial_vectors_allowed():
    """Subset of vectors is allowed"""
    dataset = create_multi_vector_dataset()
    vector_config = {
        "vectors": {
            "text": {"size": 384, "distance": "COSINE"}
        }
    }

    error = validate_multi_vector(vector_config, dataset.schema_config["vectors"])

    assert error is None


def test_single_vector_validation_flow():
    """Single vector validation delegates correctly"""
    dataset = create_test_dataset()
    vector_config = {"size": 384, "distance": "COSINE"}

    error = validate_vector_config_match(vector_config, dataset.schema_config)

    assert error is None


def test_multi_vector_validation_flow():
    """Multi-vector validation delegates correctly"""
    dataset = create_multi_vector_dataset()
    vector_config = {
        "vectors": {
            "text": {"size": 384},
            "image": {"size": 512}
        }
    }

    error = validate_vector_config_match(vector_config, dataset.schema_config)

    assert error is None


def test_missing_schema_configuration():
    """Missing both vector and vectors returns error"""
    vector_config = {"size": 384}
    schema_config = {"scalar_fields": ["text"]}

    error = validate_vector_config_match(vector_config, schema_config)

    assert error == "Dataset schema missing vector configuration"


def test_dimension_error_propagates():
    """Dimension errors from validation functions propagate"""
    dataset = create_test_dataset()
    vector_config = {"size": 1536}

    error = validate_vector_config_match(vector_config, dataset.schema_config)

    assert error is not None
    assert "Dimension mismatch" in error
    assert "384" in error
    assert "1536" in error

