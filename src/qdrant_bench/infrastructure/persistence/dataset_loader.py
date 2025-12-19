import asyncio
import io
from typing import Any, cast

import aioboto3
import httpx
import polars as pl

from qdrant_bench.domain.entities.core import Dataset
from qdrant_bench.domain.services.evaluator import GroundTruth


async def load_dataset_corpus(dataset: Dataset, limit: int | None = None) -> list[dict[str, Any]]:
    """Pure async function - load corpus data"""
    return await load_from_uri(dataset.source_uri, limit)


async def load_query_data(dataset: Dataset, limit: int | None = None) -> list[dict[str, Any]]:
    """Pure async function - load query data"""
    query_uri = derive_query_uri(dataset.source_uri)
    return await load_from_uri(query_uri, limit)


async def load_ground_truth(dataset: Dataset) -> GroundTruth:
    """Pure async function - load ground truth judgments"""
    gt_uri = derive_ground_truth_uri(dataset.source_uri)
    records = await load_from_uri(gt_uri, limit=None)

    relevant_items = {rec["query_id"]: set(rec["relevant_ids"]) for rec in records}

    return GroundTruth(relevant_items=relevant_items)


async def load_from_uri(uri: str, limit: int | None) -> list[dict[str, Any]]:
    """Pure async function - load from any URI type"""

    if uri.startswith("s3://"):
        return await load_from_s3(uri, limit)

    if uri.startswith("http"):
        return await load_from_http(uri, limit)

    return await load_from_local(uri, limit)


async def load_from_s3(s3_uri: str, limit: int | None) -> list[dict[str, Any]]:
    """Pure async function - load from S3"""
    bucket, key = parse_s3_uri(s3_uri)

    data = await download_from_s3(bucket, key)

    return parse_parquet_bytes(data, limit)


async def load_from_http(http_uri: str, limit: int | None) -> list[dict[str, Any]]:
    """Pure async function - load from HTTP"""
    async with httpx.AsyncClient() as client:
        response = await client.get(http_uri)
        response.raise_for_status()

        return parse_parquet_bytes(response.content, limit)


async def load_from_local(file_path: str, limit: int | None) -> list[dict[str, Any]]:
    """Pure async function - load from local file"""

    def read_file():
        return pl.read_parquet(file_path)

    df = await asyncio.to_thread(read_file)

    if limit:
        df = df.head(limit)

    return df.to_dicts()


async def download_from_s3(bucket: str, key: str) -> bytes:
    """Pure async function - download from S3"""
    session = aioboto3.Session()
    async with cast(Any, session.client("s3")) as s3:
        response = await s3.get_object(Bucket=bucket, Key=key)
        return await response["Body"].read()


def parse_s3_uri(s3_uri: str) -> tuple[str, str]:
    """Pure function - parse S3 URI"""
    parts = s3_uri.replace("s3://", "").split("/", 1)
    return (parts[0], parts[1])


def parse_parquet_bytes(data: bytes, limit: int | None) -> list[dict[str, Any]]:
    """Pure function - parse parquet bytes to records"""
    df = pl.read_parquet(io.BytesIO(data))

    if limit:
        df = df.head(limit)

    return df.to_dicts()


def derive_query_uri(source_uri: str) -> str:
    """Pure function - derive query file path from corpus path"""
    return source_uri.replace(".parquet", ".queries.parquet")


def derive_ground_truth_uri(source_uri: str) -> str:
    """Pure function - derive ground truth file path from corpus path"""
    return source_uri.replace(".parquet", ".ground_truth.parquet")
