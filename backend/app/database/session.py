import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
engine = create_async_engine(
    settings.get_database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    connect_args={'timeout': settings.database_connect_timeout},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def check_database_connection() -> bool:
    try:
        async with asyncio.timeout(settings.database_connect_timeout):
            async with engine.connect() as connection:
                await connection.execute(text('SELECT 1'))
        return True
    except (Exception, TimeoutError) as exc:
        logger.warning('Database connectivity check failed: %s', type(exc).__name__)
        return False
