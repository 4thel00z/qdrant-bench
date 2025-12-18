from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from qdrant_bench.ports.repositories import ConnectionRepository
from qdrant_bench.domain.entities.core import Connection
from qdrant_bench.infrastructure.persistence.models import Connection as DbConnection

class SqlAlchemyConnectionRepository(ConnectionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, connection: Connection) -> Connection:
        db_conn = DbConnection(
            id=connection.id,
            name=connection.name,
            url=connection.url,
            api_key=connection.api_key
        )
        db_conn = await self.session.merge(db_conn)
        await self.session.commit()
        await self.session.refresh(db_conn)
        return self._map_to_domain(db_conn)

    async def list(self) -> List[Connection]:
        result = await self.session.exec(select(DbConnection))
        return [self._map_to_domain(c) for c in result.all()]

    def _map_to_domain(self, db_conn: DbConnection) -> Connection:
        return Connection(
            id=db_conn.id,
            name=db_conn.name,
            url=db_conn.url,
            api_key=db_conn.api_key
        )

