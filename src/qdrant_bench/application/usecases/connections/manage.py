from dataclasses import dataclass

from qdrant_bench.domain.entities.core import Connection
from qdrant_bench.ports.repositories import ConnectionRepository


@dataclass
class CreateConnectionCommand:
    name: str
    url: str
    api_key: str


@dataclass
class CreateConnectionUseCase:
    connection_repo: ConnectionRepository

    async def execute(self, command: CreateConnectionCommand) -> Connection:
        connection = Connection(name=command.name, url=command.url, api_key=command.api_key)
        return await self.connection_repo.save(connection)


@dataclass
class ListConnectionsUseCase:
    connection_repo: ConnectionRepository

    async def execute(self) -> list[Connection]:
        return await self.connection_repo.list()
