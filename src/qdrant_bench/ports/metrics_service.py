from typing import Any, Protocol

from qdrant_bench.domain.entities.core import Connection


class MetricsPort(Protocol):
    async def get_cluster_stats(self, connection: Connection) -> dict[str, Any]: ...
