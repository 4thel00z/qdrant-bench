import os
import socket
import subprocess
import time
from collections.abc import Generator

import httpx
import pytest


def docker_is_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def wait_for_http_ok(url: str, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s

    while time.monotonic() < deadline:
        try:
            response = httpx.get(url, timeout=0.5)
            if response.status_code < 500:
                return
        except Exception:
            pass

        time.sleep(0.25)

    raise RuntimeError(f"Timed out waiting for {url}")


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: End-to-end tests that require Docker (Qdrant + Postgres)")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if docker_is_available():
        return

    skip_marker = pytest.mark.skip(reason="Docker is required for e2e tests (docker info failed)")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def docker_compose_up() -> Generator[None, None, None]:
    if not docker_is_available():
        pytest.skip("Docker is required for e2e tests")

    if is_port_open("127.0.0.1", 6335) or is_port_open("127.0.0.1", 5436):
        raise RuntimeError("Ports 6335 and/or 5436 are already in use; cannot run e2e docker compose stack")

    compose_file = os.path.join("tests", "e2e", "docker-compose.yml")

    up_result = subprocess.run(
        ["docker", "compose", "-f", compose_file, "up", "-d", "--wait"],
        check=False,
    )
    if up_result.returncode != 0:
        raise RuntimeError("docker compose up failed")

    wait_for_http_ok("http://127.0.0.1:6335/", timeout_s=30.0)

    yield

    subprocess.run(
        ["docker", "compose", "-f", compose_file, "down", "-v"],
        check=False,
    )


@pytest.fixture(scope="session")
def api_server(docker_compose_up: None) -> Generator[str, None, None]:
    api_port = 1338
    if is_port_open("127.0.0.1", api_port):
        raise RuntimeError(f"Port {api_port} is already in use; cannot run e2e API server")

    env = {
        **os.environ,
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5436/qdrant_bench",
        "QDRANT_BENCH_EMBEDDING_BACKEND": "deterministic",
        "LOGFIRE_IGNORE_NO_CONFIG": "1",
    }

    process = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "qdrant_bench.presentation.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(api_port),
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_for_http_ok(f"http://127.0.0.1:{api_port}/api/health", timeout_s=45.0)
        yield f"http://127.0.0.1:{api_port}"
    finally:
        process.terminate()
        process.wait(timeout=10)

