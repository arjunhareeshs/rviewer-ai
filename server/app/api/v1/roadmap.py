from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.db.database import get_db
from app.models.resume import Resume
from app.models.roadmap import Roadmap
from app.core.roadmap.generator import generate_skill_roadmap

router = APIRouter(prefix="/roadmap", tags=["roadmap"])

class GenerateRoadmapRequest(BaseModel):
    resume_id: UUID
    target_role: str

class ToggleNodeRequest(BaseModel):
    is_completed: bool

@router.post("/generate")
async def generate_roadmap(request: GenerateRoadmapRequest, db: AsyncSession = Depends(get_db)):
    """
    Generates a personalized Skill Roadmap for a given resume and target role.
    This uses LLM for the structure and DDGS for dynamic learning links.
    """
    # 1. Fetch Resume
    result = await db.execute(select(Resume).where(Resume.id == request.resume_id))
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # 2. Extract parsed content
    # In a full app we'd fetch the parsed chunks or structured analysis. 
    # For now, we simulate passing the raw text or basic structured data if available.
    resume_content = {
        "text": resume.content_text[:2000] if resume.content_text else "", 
        "metadata": resume.metadata_json or {}
    }

    # Extract score logic
    overall_score = 60
    if resume.metadata_json and "analysis" in resume.metadata_json:
        overall_score = resume.metadata_json["analysis"].get("overall_score", 60)

    # 3. Call core generator
    try:
        roadmap_json = await generate_skill_roadmap(
            resume_content=resume_content,
            target_role=request.target_role,
            analysis_scores={"overall_score": overall_score}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Save to DB
    new_roadmap = Roadmap(
        resume_id=request.resume_id,
        target_role=request.target_role,
        schema_json=roadmap_json,
        progress_json={}
    )
    db.add(new_roadmap)
    await db.commit()
    await db.refresh(new_roadmap)

    return {
        "id": new_roadmap.id,
        "resume_id": new_roadmap.resume_id,
        "schema": new_roadmap.schema_json,
        "progress": new_roadmap.progress_json
    }

@router.get("/{resume_id}")
async def get_roadmap(resume_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetches the latest roadmap generated for this resume.
    """
    result = await db.execute(
        select(Roadmap)
        .where(Roadmap.resume_id == resume_id)
        .order_by(Roadmap.created_at.desc())
        .limit(1)
    )
    roadmap = result.scalars().first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="No roadmap found for this resume")
        
    return {
        "id": roadmap.id,
        "resume_id": roadmap.resume_id,
        "target_role": roadmap.target_role,
        "schema": roadmap.schema_json,
        "progress": roadmap.progress_json
    }

@router.post("/{roadmap_id}/node/{node_id}/toggle")
async def toggle_node_progress(
    roadmap_id: UUID, 
    node_id: str, 
    request: ToggleNodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggles the completion status of a specific node in the roadmap.
    """
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalars().first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    # Update progress dict
    progress = roadmap.progress_json.copy() if roadmap.progress_json else {}
    progress[node_id] = request.is_completed
    
    # Needs to re-assign for SQLAlchemy JSON tracking
    roadmap.progress_json = progress
    await db.commit()
    
    return {"status": "success", "progress": progress}
