from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.engine import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia inyectable que provee una sesión de base de datos asíncrona por request.
    Se asegura de cerrar la conexión cuando la request termina.
    """
    async with AsyncSessionLocal() as session:
        yield session
