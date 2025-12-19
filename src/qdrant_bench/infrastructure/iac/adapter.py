import asyncio
from dataclasses import dataclass
from typing import Any, cast

import logfire
import python_terraform


@dataclass
class QdrantClusterConfig:
    name: str
    cloud_provider: str
    cloud_region: str
    num_nodes: int
    resource_id: str  # e.g. "free-tier" or "aws-t3-medium"


@dataclass
class ClusterConnectionInfo:
    cluster_id: str
    url: str
    api_key: str


class QdrantCloudAdapter:
    def __init__(self, working_dir: str, api_key: str):
        self.tf = python_terraform.Terraform(working_dir=working_dir)
        self.api_key = api_key
        self.working_dir = working_dir

    def get_vars(self, config: QdrantClusterConfig) -> dict[str, Any]:
        return {
            "api_key": self.api_key,
            "cluster_name": config.name,
            "cloud_provider": config.cloud_provider,
            "cloud_region": config.cloud_region,
            "cluster_configuration": {
                "num_nodes": config.num_nodes,
                "node_config": {"resource_id": config.resource_id},
            },
        }

    async def apply(self, config: QdrantClusterConfig) -> ClusterConnectionInfo:
        logfire.info(f"Provisioning Qdrant Cluster: {config.name}")

        # Terraform operations are blocking, so we run them in a thread
        return await asyncio.to_thread(self.apply_sync, config)

    def apply_sync(self, config: QdrantClusterConfig) -> ClusterConnectionInfo:
        return_code, stdout, stderr = self.tf.init()
        if return_code != 0:
            logfire.error(f"Terraform init failed: {stderr}")
            raise RuntimeError(f"Terraform init failed: {stderr}")

        vars = self.get_vars(config)
        return_code, stdout, stderr = self.tf.apply(skip_plan=True, var=vars)

        if return_code != 0:
            logfire.error(f"Terraform apply failed: {stderr}")
            raise RuntimeError(f"Terraform apply failed: {stderr}")

        # Fetch outputs
        outputs = self.tf.output()
        if not outputs:
            raise RuntimeError("Terraform output is empty")

        return ClusterConnectionInfo(
            cluster_id=outputs["cluster_id"]["value"],
            url=outputs["cluster_endpoint"]["value"],
            api_key=outputs["api_key"]["value"],
        )

    async def destroy(self, config: QdrantClusterConfig):
        logfire.info(f"Destroying Qdrant Cluster: {config.name}")
        await asyncio.to_thread(self.destroy_sync, config)

    def destroy_sync(self, config: QdrantClusterConfig):
        vars = self.get_vars(config)
        return_code, stdout, stderr = cast(Any, self.tf).destroy(var=vars, force=True)
        if return_code != 0:
            logfire.error(f"Terraform destroy failed: {stderr}")
            raise RuntimeError(f"Terraform destroy failed: {stderr}")
        logfire.info(f"Cluster {config.name} destroyed successfully")
