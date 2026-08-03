from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

