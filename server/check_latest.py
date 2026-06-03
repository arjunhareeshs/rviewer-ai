import asyncio
from app.db.database import AsyncSessionLocal
from app.models.resume import Resume
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Resume).order_by(Resume.created_at.desc()).limit(1))
        r = result.scalars().first()
        if r:
            print(f'Resume ID: {r.id}')
            print(f'Status: {r.status.value}')
            print(f'Method: {r.extraction_method.value if r.extraction_method else None}')
        else:
            print("No resumes found.")

asyncio.run(main())
