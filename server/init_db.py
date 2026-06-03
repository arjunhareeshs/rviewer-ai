import asyncio
import logging
from app.db.database import engine, Base
# Import ALL models so they are registered with Base.metadata
from app.models.resume import User, Resume, ResumeSection, ResumeChunk, ResumeAnalysis
from app.models.admin import Shortlist, RecruiterNote
from app.models.builder import ResumeTemplate, BuilderDraft
from app.models.roadmap import Roadmap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
