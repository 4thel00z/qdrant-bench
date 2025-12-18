from typing import Dict, Any, Protocol

class ClusterMetricsService(Protocol):
    async def get_cluster_stats(self, connection_id: str) -> Dict[str, Any]:
        ...

