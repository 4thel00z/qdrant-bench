from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from qdrant_bench.domain.entities.core import ObjectStorage
from qdrant_bench.infrastructure.persistence.models import ObjectStorage as DbObjectStorage
from qdrant_bench.ports.repositories import ObjectStorageRepository


@dataclass
class SqlAlchemyObjectStorageRepository(ObjectStorageRepository):
    session: AsyncSession

    async def save(self, storage: ObjectStorage) -> ObjectStorage:
        db_storage = DbObjectStorage(
            id=storage.id,
            bucket=storage.bucket,
            region=storage.region,
            endpoint_url=storage.endpoint_url,
            access_key=storage.access_key,
            secret_key=storage.secret_key,
        )
        db_storage = await self.session.merge(db_storage)
        await self.session.commit()
        await self.session.refresh(db_storage)
        return self.to_domain(db_storage)

    async def list(self) -> list[ObjectStorage]:
        result = await self.session.execute(select(DbObjectStorage))
        return [self.to_domain(s) for s in result.scalars().all()]

    def to_domain(self, db_storage: DbObjectStorage) -> ObjectStorage:
        return ObjectStorage(
            id=db_storage.id,
            bucket=db_storage.bucket,
            region=db_storage.region,
            endpoint_url=db_storage.endpoint_url,
            access_key=db_storage.access_key,
            secret_key=db_storage.secret_key,
        )
