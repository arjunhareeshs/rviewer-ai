import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/rviewer"

async def run_migration():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE resume_analysis ADD COLUMN standardized_resume JSON;"))
            logger.info("Successfully added standardized_resume column to resume_analysis table.")
        except Exception as e:
            logger.error(f"Migration failed or column already exists: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
