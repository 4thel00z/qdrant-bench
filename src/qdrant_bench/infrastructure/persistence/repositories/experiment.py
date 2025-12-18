from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from qdrant_bench.ports.repositories import ExperimentRepository
from qdrant_bench.domain.entities.core import Experiment
from qdrant_bench.infrastructure.persistence.models import Experiment as DbExperiment

class SqlAlchemyExperimentRepository(ExperimentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, experiment: Experiment) -> Experiment:
        # Map Domain -> DB
        db_exp = DbExperiment(
            id=experiment.id,
            name=experiment.name,
            dataset_id=experiment.dataset_id,
            connection_id=experiment.connection_id,
            optimizer_config=experiment.optimizer_config,
            vector_config=experiment.vector_config
        )
        # Merge to handle updates or inserts
        db_exp = await self.session.merge(db_exp)
        await self.session.commit()
        await self.session.refresh(db_exp)
        
        # Map DB -> Domain
        return self._map_to_domain(db_exp)

    async def get(self, id: UUID) -> Optional[Experiment]:
        db_exp = await self.session.get(DbExperiment, id)
        if not db_exp:
            return None
        return self._map_to_domain(db_exp)

    async def list(self) -> List[Experiment]:
        result = await self.session.exec(select(DbExperiment))
        return [self._map_to_domain(exp) for exp in result.all()]

    def _map_to_domain(self, db_exp: DbExperiment) -> Experiment:
        return Experiment(
            id=db_exp.id,
            name=db_exp.name,
            dataset_id=db_exp.dataset_id,
            connection_id=db_exp.connection_id,
            optimizer_config=db_exp.optimizer_config,
            vector_config=db_exp.vector_config
        )

