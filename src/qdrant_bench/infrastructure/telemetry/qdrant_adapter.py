from dataclasses import dataclass, field
from typing import Any

import httpx
import logfire

from qdrant_bench.domain.entities.core import Connection
from qdrant_bench.ports.metrics_service import MetricsPort


@dataclass
class QdrantTelemetryAdapter(MetricsPort):
    cloud_api_key: str
    http_client: httpx.AsyncClient = field(default_factory=httpx.AsyncClient)

    async def get_cluster_stats(self, connection: Connection) -> dict[str, Any]:
        """Get real cluster stats - pure async function"""
        if not self.is_cloud_connection(connection.url):
            return await self.fetch_telemetry_endpoint(connection)

        cluster_id = self.extract_cluster_id(connection.url)
        return await self.fetch_cloud_metrics(cluster_id)

    def is_cloud_connection(self, url: str) -> bool:
        """Pure function - check if cloud hosted"""
        return "cloud.qdrant.io" in url or "qdrant.tech" in url

    def extract_cluster_id(self, url: str) -> str:
        """Pure function - extract cluster ID from URL"""
        return url.split("//")[1].split(".")[0]

    async def fetch_telemetry_endpoint(self, connection: Connection) -> dict[str, Any]:
        """Fetch from /telemetry endpoint"""
        with logfire.span(f"Fetching telemetry from {connection.url}"):
            try:
                response = await self.http_client.get(
                    f"{connection.url}/telemetry",
                    headers={"api-key": connection.api_key}
                )

                response.raise_for_status()

                telemetry_data = response.json()

                return {
                    "ram_usage": telemetry_data.get("app", {}).get("memory_usage", 0),
                    "cpu_usage": telemetry_data.get("system", {}).get("cpu_load", 0.0),
                    "points_count": sum(
                        c.get("points_count", 0)
                        for c in telemetry_data.get("collections", [])
                    )
                }
            except Exception as e:
                logfire.error(f"Failed to fetch telemetry: {e}")
                return {}

    async def fetch_cloud_metrics(self, cluster_id: str) -> dict[str, Any]:
        """Fetch from Qdrant Cloud API"""
        if not self.cloud_api_key:
            logfire.warn("Cloud API key not configured, skipping cloud metrics")
            return {}

        with logfire.span(f"Fetching cloud metrics for cluster {cluster_id}"):
            try:
                response = await self.http_client.get(
                    f"https://cloud.qdrant.io/api/v1/clusters/{cluster_id}/metrics",
                    headers={"Authorization": f"Bearer {self.cloud_api_key}"}
                )

                response.raise_for_status()

                metrics = response.json()
                return {
                    "ram_usage": metrics.get("memory_bytes", 0),
                    "cpu_usage": metrics.get("cpu_percent", 0.0),
                    "disk_usage": metrics.get("disk_bytes", 0)
                }
            except Exception as e:
                logfire.error(f"Failed to fetch cloud metrics: {e}")
                return {}
