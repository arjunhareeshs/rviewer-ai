import os
import uuid
import asyncio
from pathlib import Path
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, Depends
from fastapi.responses import FileResponse  # BUG-04: was missing
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.resume import Resume
from livekit import api as livekit_api  # BUG-03: was missing


from app.config import get_settings
from app.core.interview.session_manager import session_manager
from app.core.interview.resume_service import resume_service
from app.core.interview.sanitization import sanitize_room_name, validate_candidate_name
from app.core.interview.llm_service import llm_service
from app.core.interview.report_generator import generate_pdf_report
from slowapi import Limiter
from slowapi.util import get_remote_address

settings = get_settings()
router = APIRouter(prefix="/interview", tags=["Interview"])
limiter = Limiter(key_func=get_remote_address)

class TokenResponse(BaseModel):
    token: str
    room_name: str
    expires_in_minutes: int

class SessionStatusResponse(BaseModel):
    room_name: str
    phase: str
    exchange_count: int
    report_ready: bool

@router.post("/start")
async def start_interview(
    room_name: str = Form(...),
    candidate_name: str = Form("Candidate"),
    resume_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create session and return room name for interview."""
    room_name = sanitize_room_name(room_name)
    candidate_name = validate_candidate_name(candidate_name)
    
    session = await session_manager.get_or_create_session(room_name, candidate_name)
    
    if resume_id:
        try:
            from uuid import UUID
            resume_uuid = UUID(resume_id)
            resume = await db.get(Resume, resume_uuid)
            if resume and resume.raw_text:
                session.resume_path = resume.file_path
                session.resume_parsed_text = resume.raw_text
                # Create FAISS index for the room using the resume text
                await resume_service.create_index_async(resume.raw_text, room_name)
                # Save session again to persist paths
                await session_manager.save_session(session)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to associate resume {resume_id} with room {room_name}: {e}")
            
    return {"room_name": room_name, "status": "ready"}

@router.post("/upload-resume")
@limiter.limit("5/minute")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    room_name: str = Form(...),
    candidate_name: str = Form("Candidate")
):
    room_name = sanitize_room_name(room_name)
    candidate_name = validate_candidate_name(candidate_name)
    
    if file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB")
        
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(status_code=400, detail="Only PDF and Word documents are supported for interviews.")
        
    temp_dir = Path("data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4().hex}{ext}"
    
    try:
        content = await file.read()
        temp_path.write_bytes(content)
        
        parsed_text = await resume_service.parse_resume(str(temp_path))
        
        await resume_service.create_index_async(parsed_text, room_name)
        
        session = await session_manager.get_or_create_session(room_name, candidate_name)
        session.resume_path = str(temp_path)
        session.resume_parsed_text = parsed_text
        
        return {
            "status": "success",
            "message": "Resume uploaded and indexed",
            "room_name": room_name,
            "detected_type": ext
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/token", response_model=TokenResponse)
@limiter.limit("10/minute")
async def get_token(request: Request, room_name: str, candidate_name: str = "Candidate"):
    room_name = sanitize_room_name(room_name)
    candidate_name = validate_candidate_name(candidate_name)
    
    token = livekit_api.AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    )
    token.with_identity(candidate_name)
    token.with_name(candidate_name)
    token.with_grants(livekit_api.VideoGrants(
        room_join=True,
        room=room_name,
    ))
    
    return TokenResponse(
        token=token.to_jwt(),
        room_name=room_name,
        expires_in_minutes=settings.JWT_TOKEN_EXPIRY_MINUTES
    )

async def _generate_evaluation_task(room_name: str):
    session = await session_manager.get_session(room_name)
    if not session:
        return
        
    history = session.state.history
    if not history:
        return
        
    transcript = "\n".join([f"{msg.role}: {msg.content}" for msg in history])  # BUG-08: was double-escaped
    
    prompt_path = Path("app/core/interview/prompts/report.md")
    if prompt_path.exists():
        prompt = prompt_path.read_text()
    else:
        # Fallback if file not found
        prompt = "Review the transcript and score answer_quality, technical_correctness, communication, problem_solving, attitude_confidence, overall_recommendation on 0-10 scale. Output JSON matching EvaluationScore. Transcript: {transcript}"
        
    try:
        score = await llm_service.evaluate_interview(transcript, prompt)
        session.state.evaluation = score
        
        report_path = generate_pdf_report(session)
        session.report_pdf_path = report_path
        
        # Save session to persist the evaluation score and report path
        await session_manager.save_session(session)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to generate evaluation task for {room_name}: {e}")

@router.post("/end-interview")
@limiter.limit("5/minute")
async def end_interview(request: Request, room_name: str, background_tasks: BackgroundTasks):
    room_name = sanitize_room_name(room_name)
    session = await session_manager.get_session(room_name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    import datetime
    session.end_time = datetime.datetime.now(datetime.timezone.utc)
    await session_manager.save_session(session)
    
    background_tasks.add_task(_generate_evaluation_task, room_name)
    
    return {
        "status": "success",
        "message": "Evaluation started in background."
    }

@router.get("/session-status/{room_name}", response_model=SessionStatusResponse)
async def get_session_status(room_name: str):
    room_name = sanitize_room_name(room_name)
    session = await session_manager.get_session(room_name)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return SessionStatusResponse(
        room_name=session.room_name,
        phase=session.state.phase.value,
        exchange_count=session.state.exchange_count,
        report_ready=session.report_pdf_path is not None
    )

@router.get("/session/{room_name}")
async def get_session_details(room_name: str):
    """Get the full details of an interview session."""
    room_name = sanitize_room_name(room_name)
    session = await session_manager.get_session(room_name)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/download-report/{room_name}")
@limiter.limit("10/minute")
async def download_report(request: Request, room_name: str):
    room_name = sanitize_room_name(room_name)
    session = await session_manager.get_session(room_name)
    
    if not session or not session.report_pdf_path:
        raise HTTPException(status_code=404, detail="Report not ready or session not found")
        
    return FileResponse(
        session.report_pdf_path, 
        media_type='application/pdf', 
        filename=f"{room_name}_interview_report.pdf"
    )

@router.get("/health")
async def health_check():
    return {"status": "ok"}
