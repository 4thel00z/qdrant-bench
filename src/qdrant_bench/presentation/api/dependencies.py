from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session(request: Request):
    session_maker = request.app.state.sessionmaker
    async with session_maker() as session:
        yield session

