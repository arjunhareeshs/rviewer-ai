import asyncio
import uuid
import logging
import sys
from pathlib import Path
from sqlalchemy.future import select

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from app.db.database import AsyncSessionLocal
from app.models.resume import Resume
from app.api.v1.resumes import run_extraction_pipeline

async def main():
    resume_id = uuid.UUID('0c985e70-178e-45c3-966a-2e3f31676948')
    async with AsyncSessionLocal() as db:
        resume = await db.get(Resume, resume_id)
        if not resume:
            print("Resume not found")
            return
            
        file_path = Path(resume.file_path)
        file_type = resume.file_type
        
        print(f"Running pipeline for {file_path}")
        # Run it again
        try:
            await run_extraction_pipeline(resume_id, file_path, file_type)
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
