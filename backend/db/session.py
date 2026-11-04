import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import get_settings
from db.models import Base

logger = logging.getLogger("datanova.db")

settings = get_settings()

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
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
    """Initialize database tables at startup and ensure schema is migrated."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            # Auto-migrate SQLite columns if table already existed from earlier phases
            if engine.dialect.name == "sqlite" and getattr(settings, "AUTO_MIGRATE", True):
                # Ensure documents columns
                res = await conn.execute(text("PRAGMA table_info(documents)"))
                existing_doc_cols = {row[1] for row in res.fetchall()}
                if existing_doc_cols:
                    if "tenant_id" not in existing_doc_cols:
                        await conn.execute(
                            text("ALTER TABLE documents ADD COLUMN tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL")
                        )
                    if "doc_type" not in existing_doc_cols:
                        await conn.execute(
                            text("ALTER TABLE documents ADD COLUMN doc_type VARCHAR(64) DEFAULT 'invoice' NOT NULL")
                        )
                    if "storage_key" not in existing_doc_cols:
                        await conn.execute(text("ALTER TABLE documents ADD COLUMN storage_key VARCHAR(255)"))

                # Ensure page_images columns
                res_page = await conn.execute(text("PRAGMA table_info(page_images)"))
                existing_page_cols = {row[1] for row in res_page.fetchall()}
                if existing_page_cols and "storage_key" not in existing_page_cols:
                    await conn.execute(text("ALTER TABLE page_images ADD COLUMN storage_key VARCHAR(255)"))

        logger.info("Database initialized and verified successfully.")
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
