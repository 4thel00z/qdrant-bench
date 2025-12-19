from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from qdrant_bench.application.usecases.connections.manage import (
    CreateConnectionCommand,
    CreateConnectionUseCase,
    ListConnectionsUseCase,
)
from qdrant_bench.presentation.api.dependencies import get_create_connection_usecase, get_list_connections_usecase


class CreateConnectionRequest(BaseModel):
    name: str
    url: str
    api_key: str


class ConnectionResponse(BaseModel):
    id: UUID
    name: str
    url: str
    api_key: str


router = APIRouter(prefix="/connections", tags=["Connections"])


@router.get("")
async def list_connections(use_case: ListConnectionsUseCase = Depends(get_list_connections_usecase)):
    connections = await use_case.execute()
    return [ConnectionResponse(id=c.id, name=c.name, url=c.url, api_key=c.api_key) for c in connections]


@router.post("", status_code=201)
async def create_connection(
    request: CreateConnectionRequest, use_case: CreateConnectionUseCase = Depends(get_create_connection_usecase)
):
    command = CreateConnectionCommand(name=request.name, url=request.url, api_key=request.api_key)
    connection = await use_case.execute(command)
    return ConnectionResponse(id=connection.id, name=connection.name, url=connection.url, api_key=connection.api_key)
