from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL

async_engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import SYNC_DATABASE_URL

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, pool_pre_ping=True)

SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)