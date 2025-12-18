from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from qdrant_bench.ports.repositories import DatasetRepository
from qdrant_bench.domain.entities.core import Dataset
from qdrant_bench.infrastructure.persistence.models import Dataset as DbDataset

class SqlAlchemyDatasetRepository(DatasetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, dataset: Dataset) -> Dataset:
        db_ds = DbDataset(
            id=dataset.id,
            name=dataset.name,
            source_uri=dataset.source_uri,
            schema_config=dataset.schema_config
        )
        db_ds = await self.session.merge(db_ds)
        await self.session.commit()
        await self.session.refresh(db_ds)
        return self._map_to_domain(db_ds)

    async def get(self, id: UUID) -> Optional[Dataset]:
        db_ds = await self.session.get(DbDataset, id)
        if not db_ds:
            return None
        return self._map_to_domain(db_ds)

    async def list(self) -> List[Dataset]:
        result = await self.session.exec(select(DbDataset))
        return [self._map_to_domain(ds) for ds in result.all()]

    def _map_to_domain(self, db_ds: DbDataset) -> Dataset:
        return Dataset(
            id=db_ds.id,
            name=db_ds.name,
            source_uri=db_ds.source_uri,
            schema_config=db_ds.schema_config
        )

