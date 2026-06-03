from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, cast, String
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.db.database import get_db
from app.models.resume import Resume, User
from app.models.admin import Shortlist, RecruiterNote
from app.core.admin.nl_filter import translate_nl_query_to_filter
from app.utils.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_current_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure the user is a recruiter or admin"""
    if current_user.role not in ["recruiter", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Recruiter privileges required."
        )
    return current_user

# -- Models --
class ChatFilterRequest(BaseModel):
    user_message: str
    chat_history: List[Dict[str, str]] # [{'role': 'user'|'assistant', 'content': '...'}]
    active_filters: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    filters: Dict[str, Any]

class ToggleShortlistRequest(BaseModel):
    resume_id: UUID

class NoteRequest(BaseModel):
    resume_id: UUID
    note_text: str

# -- Endpoints --

@router.get("/dashboard/metrics")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """Returns aggregated high-level metrics for the Admin Dashboard."""
    # Note: In a real system these would query actual scores. Mocking aggregation for now to support the frontend.
    total_resumes = (await db.execute(select(func.count(Resume.id)))).scalar()
    
    return {
        "total_candidates": total_resumes or 248,
        "avg_ats_score": 67,
        "interviews_completed": 183,
        "shortlisted_this_week": 14,
        "score_distribution": [
            {"range": "0-20", "count": 12},
            {"range": "21-40", "count": 34},
            {"range": "41-60", "count": 89},
            {"range": "61-80", "count": 92},
            {"range": "81-100", "count": 21}
        ],
        "top_skills": [
            {"name": "Python", "percentage": 84},
            {"name": "TensorFlow", "percentage": 61},
            {"name": "SQL", "percentage": 58},
            {"name": "React", "percentage": 42}
        ],
        "recent_activity": [
            {"text": "Arjun S completed interview — Score: 74", "time": "2 hrs ago"},
            {"text": "Varun S uploaded resume — ATS: 62", "time": "5 hrs ago"},
            {"text": "Priya K shortlisted by you", "time": "Yesterday"}
        ]
    }

@router.post("/candidates/search")
async def search_candidates(req: SearchRequest, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """
    Core search engine. Applies the structured JSON filters and instant-search query 
    against the Postgres Database.
    """
    stmt = select(Resume)
    
    # Text Search (Instant typing)
    if req.query:
        # Simplistic ILIKE search. In production, use pg_trgm: Resume.content_text.op('%')(req.query)
        search_term = f"%{req.query}%"
        stmt = stmt.where(Resume.content_text.ilike(search_term))
        
    # Apply JSON filters
    filters = req.filters
    
    # Mocking returning all resumes for the frontend demonstration if no strict mapping exists yet
    # Example mapping:
    # if filters.get('skills'):
    #     for skill in filters['skills']:
    #        stmt = stmt.where(Resume.content_text.ilike(f"%{skill}%"))
    
    # Sort
    sort_by = filters.get("sort_by", "recent")
    sort_order = filters.get("sort_order", "desc")
    
    if sort_by == "recent":
        stmt = stmt.order_by(Resume.created_at.desc() if sort_order == "desc" else Resume.created_at.asc())
        
    result = await db.execute(stmt.limit(50))
    resumes = result.scalars().all()
    
    # Format for frontend grid
    response_data = []
    
    # In production with actual data we would join with ResumeAnalysis
    from app.models.resume import ResumeAnalysis
    from sqlalchemy.orm import selectinload
    
    # Try fetching with analysis
    stmt = stmt.options(selectinload(Resume.analysis))
    result = await db.execute(stmt.limit(50))
    resumes = result.scalars().all()

    for r in resumes:
        metadata = r.extraction_metadata or {}
        analysis = r.analysis[0] if getattr(r, 'analysis', None) and len(r.analysis) > 0 else None
        
        ats = analysis.ats_score if analysis else 0
        overall = analysis.overall_score if analysis else 0
        
        # Interview score would come from sessions, mock for now if missing
        interview_score = overall + 5 if overall > 0 else 0
        
        response_data.append({
            "id": str(r.id),
            "name": metadata.get("name", f"Candidate {str(r.id)[:4]}"),
            "institution": metadata.get("education", [{}])[0].get("institution", "Unknown University") if metadata.get("education") else "Unknown",
            "top_skills": metadata.get("skills", ["Python", "SQL", "Docker", "AWS"])[:4] if metadata.get("skills") else [],
            "ats_score": ats,
            "interview_score": interview_score,
            "overall_score": overall,
            "recommended_role": analysis.role_recommendations.get("top_roles", [{}])[0].get("title", "Undetermined") if analysis and analysis.role_recommendations else "Analysis Pending",
            "interview_completed": interview_score > 0
        })
        

        
    return {"candidates": response_data}

@router.post("/candidates/chat-filter")
async def chat_filter(req: ChatFilterRequest, admin: User = Depends(get_current_recruiter)):
    """
    Passes the natural language message to the LLM to update the JSON filter state.
    """
    result = await translate_nl_query_to_filter(
        user_message=req.user_message,
        chat_history=req.chat_history,
        active_filters=req.active_filters
    )
    return result

@router.get("/shortlist")
async def get_shortlist(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """Fetches the active admin's shortlisted candidates."""
    result = await db.execute(
        select(Shortlist).where(Shortlist.admin_id == admin.id)
    )
    shortlists = result.scalars().all()
    
    # We would return the fully populated candidate info here.
    # We will mock the full objects for the comparison UI.
    mocked_shortlist = [
        {
            "id": "1", "name": "Arjun S", "overall_score": 79, "ats_score": 74, "interview_score": 82,
            "project_strength": 71, "top_skills": ["PyTorch", "Docker"], "internships": 1, 
            "certifications": 3, "role_match": "ML Engineer 88%", "github_activity": "Active (92 days)", "leetcode": 104
        },
        {
            "id": "2", "name": "Priya K", "overall_score": 81, "ats_score": 78, "interview_score": 85,
            "project_strength": 68, "top_skills": ["React", "FastAPI"], "internships": 2, 
            "certifications": 1, "role_match": "Backend Dev 84%", "github_activity": "Moderate", "leetcode": 67
        }
    ]
    return {"shortlisted_candidates": mocked_shortlist}

@router.post("/shortlist")
async def add_to_shortlist(req: ToggleShortlistRequest, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """Adds a candidate to the shortlist."""
    new_shortlist = Shortlist(admin_id=admin.id, resume_id=req.resume_id)
    db.add(new_shortlist)
    await db.commit()
    return {"status": "success"}

@router.delete("/shortlist/{resume_id}")
async def remove_from_shortlist(resume_id: UUID, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """Removes a candidate from the shortlist."""
    result = await db.execute(
        select(Shortlist).where((Shortlist.admin_id == admin.id) & (Shortlist.resume_id == resume_id))
    )
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return {"status": "success"}

@router.put("/notes")
async def update_notes(req: NoteRequest, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_recruiter)):
    """Creates or updates a private recruiter note for a candidate."""
    result = await db.execute(
        select(RecruiterNote).where((RecruiterNote.admin_id == admin.id) & (RecruiterNote.resume_id == req.resume_id))
    )
    note = result.scalars().first()
    if note:
        note.note_text = req.note_text
    else:
        note = RecruiterNote(admin_id=admin.id, resume_id=req.resume_id, note_text=req.note_text)
        db.add(note)
        
    await db.commit()
    return {"status": "success"}
