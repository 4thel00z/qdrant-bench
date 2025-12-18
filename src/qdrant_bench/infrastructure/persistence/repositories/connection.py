from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from qdrant_bench.domain.entities.core import Connection
from qdrant_bench.infrastructure.persistence.models import Connection as DbConnection
from qdrant_bench.ports.repositories import ConnectionRepository


class SqlAlchemyConnectionRepository(ConnectionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, connection: Connection) -> Connection:
        db_conn = DbConnection(id=connection.id, name=connection.name, url=connection.url, api_key=connection.api_key)
        db_conn = await self.session.merge(db_conn)
        await self.session.commit()
        await self.session.refresh(db_conn)
        return self.to_domain(db_conn)

    async def get(self, id: UUID) -> Connection | None:
        db_conn = await self.session.get(DbConnection, id)
        if not db_conn:
            return None
        return self.to_domain(db_conn)

    async def list(self) -> list[Connection]:
        result = await self.session.execute(select(DbConnection))
        return [self.to_domain(c) for c in result.scalars().all()]

    def to_domain(self, db_conn: DbConnection) -> Connection:
        return Connection(id=db_conn.id, name=db_conn.name, url=db_conn.url, api_key=db_conn.api_key)
