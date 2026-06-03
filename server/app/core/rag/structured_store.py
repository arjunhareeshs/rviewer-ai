"""
Structured content store (PostgreSQL).

This module manages the storage and retrieval of full resume sections.
This is the EXCLUSIVE data source for all LLM operations (ATS scoring,
role match, interview context).

Both PDF (via Docling) and Image (via VLM) pipelines write their final
extracted sections here.
"""

import logging
from typing import Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.models.resume import ResumeSection
from app.schemas.resume import ResumeFullJSON

logger = logging.getLogger(__name__)


async def store_sections(
    db: AsyncSession, 
    resume_id: UUID, 
    sections: Dict[str, str],
    metadata: Dict = None
) -> None:
    """
    Store full sections into PostgreSQL.
    Overwrites any existing sections for this resume.
    """
    # Delete existing sections first (useful for re-extraction)
    await db.execute(delete(ResumeSection).where(ResumeSection.resume_id == resume_id))
    
    order = 0
    for label, content in sections.items():
        if not content or not content.strip():
            continue
            
        section_record = ResumeSection(
            resume_id=resume_id,
            section_label=label.lower(),
            content=content.strip(),
            section_order=order,
            meta=metadata
        )
        db.add(section_record)
        order += 1
        
    await db.commit()
    logger.info(f"Stored {order} sections for resume {resume_id} in structured store")


async def get_full_resume_json(db: AsyncSession, resume_id: UUID) -> ResumeFullJSON:
    """
    Retrieve all sections and assemble into a single JSON payload.
    This payload is fed directly to the LLM.
    """
    stmt = (
        select(ResumeSection)
        .where(ResumeSection.resume_id == resume_id)
        .order_by(ResumeSection.section_order)
    )
    result = await db.execute(stmt)
    db_sections = result.scalars().all()
    
    if not db_sections:
        logger.warning(f"No structured sections found for resume {resume_id}")
        return ResumeFullJSON(doc_id=resume_id, sections={})
        
    sections_dict = {
        sec.section_label: sec.content 
        for sec in db_sections
    }
    
    return ResumeFullJSON(
        doc_id=resume_id,
        sections=sections_dict
    )
