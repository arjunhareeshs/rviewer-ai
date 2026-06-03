import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.resume import Resume, ExtractionMethod
from app.schemas.resume import RetrievalRequest, RetrievalResponse
from app.core.rag.retriever import hybrid_retrieve

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.post("/search", response_model=RetrievalResponse)
async def search_resume(
    request: RetrievalRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search a specific resume using hybrid retrieval (Semantic + Keyword).
    Only available for PDF resumes (Docling extraction).
    """
    resume = await db.get(Resume, request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if resume.extraction_method not in (ExtractionMethod.docling, ExtractionMethod.vlm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retrieval is only supported for resumes processed via Docling or VLM."
        )
        
    try:
        results = await hybrid_retrieve(
            resume_id=request.resume_id,
            query=request.query,
            section_filter=request.section_filter,
            top_k=request.top_k
        )
        
        return RetrievalResponse(
            resume_id=request.resume_id,
            query=request.query,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search execution failed: {str(e)}"
        )
