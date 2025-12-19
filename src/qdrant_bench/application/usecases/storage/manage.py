from dataclasses import dataclass

from qdrant_bench.domain.entities.core import ObjectStorage
from qdrant_bench.ports.repositories import ObjectStorageRepository


@dataclass
class CreateStorageCommand:
    bucket: str
    region: str
    endpoint_url: str
    access_key: str
    secret_key: str


@dataclass
class CreateStorageUseCase:
    storage_repo: ObjectStorageRepository

    async def execute(self, command: CreateStorageCommand) -> ObjectStorage:
        return await self.storage_repo.save(
            ObjectStorage(
                bucket=command.bucket,
                region=command.region,
                endpoint_url=command.endpoint_url,
                access_key=command.access_key,
                secret_key=command.secret_key,
            )
        )


@dataclass
class ListStorageUseCase:
    storage_repo: ObjectStorageRepository

    async def execute(self) -> list[ObjectStorage]:
        return await self.storage_repo.list()
