from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.database import get_db
from app.models.resume import ResumeAnalysis
from app.core.analysis.schemas import FullAnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/{resume_id}", response_model=FullAnalysisResponse)
async def get_resume_analysis(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the complete analysis results for a specific resume.
    """
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(ResumeAnalysis).where(ResumeAnalysis.resume_id == resume_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this resume. Ensure the resume was successfully uploaded and processed."
        )
        
    return FullAnalysisResponse(
        resume_id=str(analysis.resume_id),
        ats_score=analysis.ats_score,
        ats_result=analysis.ats_criteria,
        role_recommendations=analysis.role_recommendations,
        project_analysis=analysis.project_analysis,
        link_analysis=analysis.link_analysis,
        standardized_resume=analysis.standardized_resume,
        overall_score=analysis.overall_score
    )
