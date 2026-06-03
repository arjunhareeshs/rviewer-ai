import os
import uuid
import shutil
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List

from app.db.database import get_db
from app.models.resume import Resume, ResumeStatus, ExtractionMethod, FileType, User
from app.schemas.resume import (
    ResumeUploadResponse, 
    ResumeResponse, 
    ResumeListResponse,
    ResumeSectionsResponse,
    ResumeSectionResponse
)
from app.core.extraction import extract_resume, ExtractionResult
from app.core.embedding import chunk_content_blocks, embed_chunks
from app.core.rag import store_sections, store_chunks, delete_document
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["Resumes"])

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # BUG-01: now uses authenticated user
):
    """
    Upload a resume file (PDF or Image), save it, and run the extraction pipeline in the background.
    """
    user_id = current_user.id
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext == ".pdf":
        file_type = FileType.pdf
    elif file_ext in [".jpg", ".jpeg", ".png", ".webp"]:
        file_type = FileType.image
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Must be PDF or Image (JPG/PNG). Got: {file_ext}"
        )
        
    # Save file
    file_id = uuid.uuid4()
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create DB record
    resume = Resume(
        id=file_id,
        user_id=user_id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_type,
        status=ResumeStatus.uploaded
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    background_tasks.add_task(run_extraction_pipeline, resume.id, file_path, file_type)
    
    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        file_type=resume.file_type.value,
        status=resume.status.value,
        extraction_method=resume.extraction_method.value if resume.extraction_method else None,
        created_at=resume.created_at,
    )

async def run_extraction_pipeline(resume_id: UUID, file_path: Path, file_type: FileType):
    from app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        resume = await db.get(Resume, resume_id)
        if not resume:
            return
            
        try:
            logger.info(f"Starting extraction for resume {resume.id}")
            resume.status = ResumeStatus.extracting
            await db.commit()
            
            # Stage 1 & 2: Extraction
            ext_result: ExtractionResult = await extract_resume(str(file_path))
            
            resume.extraction_method = ExtractionMethod(ext_result.method)
            resume.raw_text = ext_result.raw_text
            resume.extraction_metadata = ext_result.metadata
            
            sections_dict = {}
            # Stage 3-5: Chunking, Embedding & Storage
            if ext_result.method == "docling" and ext_result.content_blocks:
                resume.status = ResumeStatus.embedding
                await db.commit()
                
                # PDF Path
                from app.core.embedding import chunk_content_blocks, embed_chunks
                from app.core.rag import store_sections, store_chunks
                chunks, sections_dict = chunk_content_blocks(ext_result.content_blocks)
                
                # Store structured sections
                await store_sections(db, resume.id, sections_dict, metadata={"method": "docling"})
                
                # Embed and store chunks
                chunks_with_vectors = await embed_chunks(chunks)
                try:
                    await store_chunks(resume.id, chunks_with_vectors)
                except Exception as e:
                    logger.error(f"Failed to store docling chunks in vector DB: {e}")
                
            elif ext_result.method == "vlm" and ext_result.sections:
                # VLM Path (PDF or Image)
                from app.core.rag import store_sections
                await store_sections(db, resume.id, ext_result.sections, metadata={"method": "vlm"})

                # Generate virtual ContentBlocks from VLM sections for chunking/embedding/RAG
                from app.core.extraction import ContentBlock
                virtual_blocks = []
                reading_order = 0

                for section_label, content in ext_result.sections.items():
                    if not content or not content.strip():
                        continue

                    # 1. Section Header Block
                    virtual_blocks.append(ContentBlock(
                        block_type="heading",
                        font_size=12.0,  # Dummy section header font size
                        text_weight="bold",
                        reading_order_index=reading_order,
                        raw_text=section_label.capitalize()
                    ))
                    reading_order += 1

                    # 2. Section Content Blocks
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    for line in lines:
                        if line.startswith(("-", "*", "•")):
                            block_type = "list_item"
                            clean_line = line.lstrip("-*• ").strip()
                        else:
                            block_type = "body"
                            clean_line = line

                        virtual_blocks.append(ContentBlock(
                            block_type=block_type,
                            font_size=10.0,
                            text_weight="normal",
                            reading_order_index=reading_order,
                            raw_text=clean_line
                        ))
                        reading_order += 1

                # Store virtual chunks in Qdrant so retrieval works
                if virtual_blocks:
                    resume.status = ResumeStatus.embedding
                    await db.commit()

                    from app.core.embedding import chunk_content_blocks, embed_chunks
                    from app.core.rag import store_chunks

                    chunks, _ = chunk_content_blocks(virtual_blocks)
                    chunks_with_vectors = await embed_chunks(chunks)
                    try:
                        await store_chunks(resume.id, chunks_with_vectors)
                    except Exception as e:
                        logger.error(f"Failed to store virtual chunks in vector DB: {e}")
                
            # ── Synthesis & Analysis Pipeline ────────────────────────────────────
            from app.core.rag.synthesizer import synthesizer
            from app.core.analysis.ats_analyzer import ats_analyzer
            from app.core.analysis.role_recommender import role_recommender
            from app.core.analysis.project_analyzer import project_analyzer
            from app.core.link_analysis.analyzer import link_orchestrator
            from app.models.resume import ResumeAnalysis
            
            # 1. Standardize Schema using LLM
            sections_for_synthesis = sections_dict if ext_result.method == "docling" else ext_result.sections
            try:
                standardized_resume = await synthesizer.synthesize(sections_for_synthesis)
            except Exception as e:
                logger.error(f"Synthesis failed, defaulting to empty: {e}")
                from app.schemas.resume import StandardizedResume
                standardized_resume = StandardizedResume()

            # 2. ATS Analysis
            ats_result = await ats_analyzer.analyze(
                raw_text=ext_result.raw_text, 
                file_type=file_type.value, 
                sections=sections_for_synthesis,
                content_blocks=ext_result.content_blocks
            )
            
            # 3. Role Recommendation
            role_result = await role_recommender.recommend(standardized_resume)
        
            # 4. Project Analysis
            project_result = await project_analyzer.analyze(standardized_resume.projects)

            # 5. Link Analysis
            urls_to_analyze = []
            if standardized_resume.contact_info and standardized_resume.contact_info.links:
                urls_to_analyze = list(standardized_resume.contact_info.links)
            
            # Robust fallback regex link extraction
            import re
            
            # Find standard URLs
            url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
            found_urls = url_pattern.findall(ext_result.raw_text or "")
            
            platforms = ['github.com', 'linkedin.com', 'leetcode.com', 'gitlab.com', 'dev.to', 'stackoverflow.com', 'bitbucket', 'hackerrank', 'hackerearth', 'kaggle', 'geeksforgeeks']
            
            # Also find platform domains without http
            domain_pattern = re.compile(r'(?:github\.com|linkedin\.com|leetcode\.com|gitlab\.com|dev\.to|stackoverflow\.com|bitbucket|hackerrank|hackerearth|kaggle|geeksforgeeks)[^\s<>"]*')
            found_domains = domain_pattern.findall(ext_result.raw_text or "")
            
            for url in found_urls + found_domains:
                if url not in urls_to_analyze:
                    urls_to_analyze.append(url)
                    
            # Ensure urls are strings and not Pydantic objects or dicts
            clean_urls = []
            for u in urls_to_analyze:
                if isinstance(u, str):
                    clean_urls.append(u)
                elif hasattr(u, "url"):
                    clean_urls.append(str(u.url))
                elif isinstance(u, dict) and "url" in u:
                    clean_urls.append(str(u["url"]))
                else:
                    clean_urls.append(str(u))

            link_result = await link_orchestrator.analyze_links(clean_urls)

            # 6. Career Roadmap Generation (runs dynamically in pipeline for the top recommended role)
            from app.core.roadmap.generator import generate_skill_roadmap
            top_role = "Software Engineer"
            if role_result.top_role:
                top_role = role_result.top_role
            elif role_result.recommendations:
                top_role = role_result.recommendations[0].role_name
                
            resume_content = {
                "text": ext_result.raw_text[:2000] if ext_result.raw_text else "",
                "metadata": ext_result.metadata or {}
            }
            
            roadmap_json = None
            try:
                logger.info(f"Generating skill roadmap for target role: {top_role}")
                roadmap_json = await generate_skill_roadmap(
                    resume_content=resume_content,
                    target_role=top_role,
                    analysis_scores={"overall_score": ats_result.overall_score}
                )
            except Exception as roadmap_err:
                logger.error(f"Background roadmap generation failed: {roadmap_err}")

            project_analysis_data = project_result.model_dump()
            project_analysis_data["roadmap"] = roadmap_json

            # Calculate overall score (weighted average)
            overall_score = int((ats_result.overall_score * 0.4) +
                                (project_result.overall_project_score * 0.4) +
                                (link_result.overall_presence_score * 0.2))

            # Save Analysis Results
            analysis = ResumeAnalysis(
                resume_id=resume.id,
                ats_score=ats_result.overall_score,
                ats_criteria=ats_result.model_dump(),
                role_recommendations=role_result.model_dump(),
                project_analysis=project_analysis_data,
                link_analysis=link_result.model_dump(),
                standardized_resume=standardized_resume.model_dump() if standardized_resume else None,
                overall_score=overall_score
            )
            db.add(analysis)

            resume.status = ResumeStatus.completed
            await db.commit()
            logger.info(f"Pipeline completed successfully for resume {resume.id}")

        except Exception as e:
            import traceback
            logger.error(f"Pipeline failed for resume {resume.id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            try:
                await db.rollback()
            except Exception:
                pass
            
            # Re-fetch or create a new session if necessary, but rollback usually clears the state
            resume.status = ResumeStatus.failed
            db.add(resume)
            await db.commit()


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get status and metadata for a specific resume."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.get("/{resume_id}/sections", response_model=ResumeSectionsResponse)
async def get_resume_sections(resume_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all structured sections for a resume."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Wait until processing completes
    if resume.status not in (ResumeStatus.completed, ResumeStatus.failed):
        return ResumeSectionsResponse(
            resume_id=resume_id,
            extraction_method=resume.extraction_method.value if resume.extraction_method else None,
            sections=[]
        )
        
    from app.models.resume import ResumeSection
    stmt = select(ResumeSection).where(ResumeSection.resume_id == resume_id).order_by(ResumeSection.section_order)
    result = await db.execute(stmt)
    sections = result.scalars().all()
    
    return ResumeSectionsResponse(
        resume_id=resume_id,
        extraction_method=resume.extraction_method.value if resume.extraction_method else None,
        sections=[
            ResumeSectionResponse(
                id=sec.id,
                section_label=sec.section_label,
                content=sec.content,
                section_order=sec.section_order,
                meta=sec.meta
            ) for sec in sections
        ]
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a resume and all its related data (vectors, chunks, sections)."""
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Delete from Qdrant vector store
    if resume.extraction_method in (ExtractionMethod.docling, ExtractionMethod.vlm):
        await delete_document(resume_id)
        
    # Delete file from disk
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {resume.file_path}: {e}")
        
    # DB cascade handles deleting sections and chunks
    await db.delete(resume)
    await db.commit()
