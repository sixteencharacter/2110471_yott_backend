from services import sessionmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session