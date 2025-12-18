# Qdrant Bench

<p align="center">
  <img src="logo.png" alt="Qdrant Bench Logo" width="300">
</p>

<p align="center">
  <strong>Automated benchmarking and optimization system for Qdrant</strong>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.14+-blue.svg" alt="Python 3.14+">
  </a>
  <a href="https://github.com/4thel00z/qdrant-bench/actions/workflows/ci.yml">
    <img src="https://github.com/4thel00z/qdrant-bench/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/4thel00z/qdrant-bench/actions/workflows/e2e.yml">
    <img src="https://github.com/4thel00z/qdrant-bench/actions/workflows/e2e.yml/badge.svg" alt="E2E (nightly)">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
</p>

---

`qdrant-bench` is a powerful tool designed to automate the process of tuning, benchmarking, and optimizing Qdrant vector database configurations. It leverages advanced experimentation frameworks and LLM-based agents to find the optimal parameters for your specific workload.

---

## ✨ Features

*   🚀 **Async-first** - Built on modern Python async capabilities for high-performance benchmarking.
*   🎯 **Type-safe** - Fully typed codebase using Pydantic and rigorous type checking.
*   🏗️ **Hexagonal Architecture** - Robust and maintainable design separating Domain, Application, and Infrastructure layers.
*   🧠 **Smart Optimization** - Supports both Rule-based and LLM-based (LLM-as-a-judge) tuning strategies.
*   ☁️ **IAC Core** - Integrated Terraform support for managing Qdrant Cloud infrastructure.
*   📊 **Experiment Management** - Track, compare, and visualize experiment runs and metrics.

## 📦 Installation

This project uses `uv` for package management.

```bash
# Clone the repository
git clone https://github.com/your-org/qdrant-bench.git
cd qdrant-bench

# Sync dependencies
uv sync
```

## ⚙️ Configuration

The application requires the following environment variables. Create a `.env` file or export them:

| Variable | Description |
| :--- | :--- |
| `PHARIA_API_KEY` | API Key for Pharia (or `OPENAI_API_KEY` if using OpenAI adapter directly) |
| `QDRANT_API_KEY` | Qdrant Cloud API Key |
| `DATABASE_URL` | Connection string for the persistence layer (default: postgresql+asyncpg://...) |

## 🚀 Quick Start

Start the API server:

```bash
uv run python src/qdrant_bench/main.py api
```

Trigger a new experiment using the API:

```python
import httpx

# 1. Create an Experiment Definition
experiment_payload = {
    "name": "HNSW Tuning",
    "dataset_id": "uuid-...", 
    "connection_id": "uuid-...",
    "optimizer_config": {},
    "vector_config": {"size": 1536, "distance": "Cosine"}
}

response = httpx.post("http://localhost:8000/api/v1/experiments", json=experiment_payload)
print(response.json())
```

## 🏗️ Architecture

This project follows a **Hexagonal Architecture** (Ports and Adapters):

*   **Domain**: Core business logic and entities (`src/qdrant_bench/domain`). Pure Python, no external dependencies.
*   **Application**: Use Cases that orchestrate domain logic (`src/qdrant_bench/application`).
*   **Ports**: Interfaces defining how the application interacts with the outside world (`src/qdrant_bench/ports`).
*   **Infrastructure**: Concrete implementations of ports (Database, Qdrant Client, LLM Client) (`src/qdrant_bench/infrastructure`).
*   **Presentation**: Entry points like API (FastAPI) and CLI (Typer) (`src/qdrant_bench/presentation`).

## 💻 Development

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

```bash
uv run ruff check src
uv run ruff format src
```

## 🤝 Contributing

Contributions are welcome! Please adhere to the project's coding standards:
- Use **snake_case** for all methods.
- Follow the **Guardian Pattern** to reduce nesting.
- No global state or singletons.
- 100% Type coverage.

## 📄 License

MIT
