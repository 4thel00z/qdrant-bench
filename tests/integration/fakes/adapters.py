"""Fake adapter implementations for testing"""

from dataclasses import dataclass, field
from typing import Any

from qdrant_bench.domain.entities.core import Connection


@dataclass
class FakeTelemetryAdapter:
    """Fake telemetry adapter that returns realistic telemetry data"""

    ram_usage: int = 1024 * 1024 * 512  # 512 MB
    cpu_usage: float = 0.45
    call_count: int = field(default=0, init=False)

    async def get_cluster_stats(self, connection: Connection) -> dict[str, Any]:
        """Returns fake but realistic telemetry data"""
        self.call_count += 1

        return {"ram_usage": self.ram_usage, "cpu_usage": self.cpu_usage, "points_count": 10000, "collections_count": 1}
