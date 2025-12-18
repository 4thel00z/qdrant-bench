from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from qdrant_bench.ports.repositories import RunRepository
from qdrant_bench.domain.entities.core import Run, RunStatus
from qdrant_bench.infrastructure.persistence.models import Run as DbRun

class SqlAlchemyRunRepository(RunRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, run: Run) -> Run:
        db_run = DbRun(
            id=run.id,
            experiment_id=run.experiment_id,
            status=run.status,
            start_time=run.start_time,
            end_time=run.end_time,
            metrics=run.metrics
        )
        db_run = await self.session.merge(db_run)
        await self.session.commit()
        await self.session.refresh(db_run)
        return self._map_to_domain(db_run)

    async def get(self, id: UUID) -> Optional[Run]:
        db_run = await self.session.get(DbRun, id)
        if not db_run:
            return None
        return self._map_to_domain(db_run)

    async def list(self, experiment_id: Optional[UUID] = None, status: Optional[str] = None) -> List[Run]:
        query = select(DbRun)
        if experiment_id:
            query = query.where(DbRun.experiment_id == experiment_id)
        if status:
            query = query.where(DbRun.status == status)
        
        result = await self.session.exec(query)
        return [self._map_to_domain(run) for run in result.all()]

    def _map_to_domain(self, db_run: DbRun) -> Run:
        return Run(
            id=db_run.id,
            experiment_id=db_run.experiment_id,
            status=RunStatus(db_run.status),
            start_time=db_run.start_time,
            end_time=db_run.end_time,
            metrics=db_run.metrics
        )

