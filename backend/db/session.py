import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import get_settings
from db.models import Base

logger = logging.getLogger("datanova.db")

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables at startup."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error("Failed to initialize database: %s", str(exc), exc_info=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency providing an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


get_db = get_session

