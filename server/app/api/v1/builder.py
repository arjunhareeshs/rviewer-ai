import uuid as uuid_lib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.db.database import get_db
from app.models.builder import ResumeTemplate, BuilderDraft
from app.core.builder.template_injector import template_injector
from app.core.builder.pdf_generator import pdf_generator
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/builder", tags=["builder"])

# ── Schemas ─────────────────────────────────────────────────────────────

class TemplateUploadRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_premium: bool = False
    base64_image: str  # The image of the template to be reversed-engineered

class TemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_premium: bool
    template_schema: Dict[str, Any]

class PDFExportRequest(BaseModel):
    html_content: str

class AIRefineRequest(BaseModel):
    section: str
    raw_text: str
    context: Optional[str] = None

class DraftSaveRequest(BaseModel):
    resume_id: UUID
    template_id: Optional[UUID] = None
    state_json: Dict[str, Any]

class DraftResponse(BaseModel):
    id: UUID
    resume_id: UUID
    template_id: Optional[UUID]
    state_json: Dict[str, Any]
    
# ── Endpoints ───────────────────────────────────────────────────────────

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates():
    """Fetch all available templates from the server/templates directory."""
    import os
    import json
    from pathlib import Path
    import uuid as uuid_lib
    
    templates_dir = Path("server/templates")
    templates = []
    
    if templates_dir.exists():
        for file_path in templates_dir.glob("*_spec.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                    
                # Generate a consistent UUID based on filename
                template_id = uuid_lib.uuid5(uuid_lib.NAMESPACE_URL, file_path.name)
                # Pretty format the name (e.g. tempoi_spec -> Tempoi)
                name = file_path.stem.replace("_spec", "").replace("_", " ").title()
                
                templates.append(
                    TemplateResponse(
                        id=template_id,
                        name=name,
                        description="Professional VLM-extracted layout.",
                        is_premium=False,
                        template_schema=schema_data
                    )
                )
            except Exception as e:
                print(f"Error loading template {file_path}: {e}")
                
    # If no templates exist, return a default mock template
    if not templates:
        return [
            TemplateResponse(
                id=uuid_lib.uuid4(),
                name="Minimalist Professional",
                description="A clean, modern template focusing on content.",
                is_premium=False,
                template_schema={"layout": "single-column", "colors": ["#000", "#fff"]}
            )
        ]
        
    return templates

@router.post("/templates/upload", response_model=TemplateResponse)
async def upload_template(
    request: TemplateUploadRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Superadmin endpoint to upload an image of a template.
    Uses Gemini Vision to reverse engineer the layout into our JSON schema.
    """
    # 1. Send image to Gemini Vision to extract layout
    extracted_schema = await template_injector.extract_template_schema(request.base64_image)
    
    # 2. Create the new template record
    new_template = ResumeTemplate(
        name=request.name,
        description=request.description,
        is_premium=request.is_premium,
        schema_json=extracted_schema
    )
    
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return TemplateResponse(
        id=new_template.id,
        name=new_template.name,
        description=new_template.description,
        is_premium=new_template.is_premium,
        template_schema=new_template.schema_json
    )

@router.post("/export-pdf")
async def export_pdf(request: PDFExportRequest):
    """
    Generates a PDF from the fully hydrated HTML content.
    Returns the raw PDF bytes.
    """
    from fastapi.responses import Response
    
    pdf_bytes = await pdf_generator.generate_pdf(request.html_content)
    
    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate PDF. Check server logs."
        )
        
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": 'attachment; filename="resume.pdf"'
    })

@router.post("/refine")
async def refine_content(request: AIRefineRequest):
    """
    AI refinement endpoint — uses the platform's LangChain LLM (synthesizer.llm).
    """
    try:
        from app.core.rag.synthesizer import synthesizer
        from langchain_core.messages import SystemMessage, HumanMessage

        if not synthesizer.llm:
            raise HTTPException(
                status_code=503,
                detail="LLM is not configured. Please set LLM_API_KEY in .env."
            )

        prompt = (
            f"Improve this resume text for a {request.section} section.\n"
            f"Context: {request.context or 'None'}\n"
            f"Raw Text: {request.raw_text}\n\n"
            "Rewrite it to be highly professional, impactful, and ideally in the STAR format "
            "if it's an experience bullet. Return ONLY the rewritten text, no explanations."
        )

        response = await synthesizer.llm.ainvoke(
            [
                SystemMessage(content="You are a professional resume editor. Output ONLY the improved text."),
                HumanMessage(content=prompt),
            ]
        )
        refined_text = response.content.strip()
        return {"refined_text": refined_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/draft/{resume_id}", response_model=DraftResponse)
async def get_draft(
    resume_id: UUID,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the latest builder draft for a specific resume."""
    result = await db.execute(
        select(BuilderDraft)
        .where(BuilderDraft.user_id == current_user.id)
        .where(BuilderDraft.resume_id == resume_id)
        .order_by(BuilderDraft.updated_at.desc())
        .limit(1)
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    return DraftResponse(
        id=draft.id,
        resume_id=draft.resume_id,
        template_id=draft.template_id,
        state_json=draft.state_json
    )

@router.post("/draft", response_model=DraftResponse)
async def save_draft(
    request: DraftSaveRequest,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update a builder draft for a specific resume."""
    result = await db.execute(
        select(BuilderDraft)
        .where(BuilderDraft.user_id == current_user.id)
        .where(BuilderDraft.resume_id == request.resume_id)
        .limit(1)
    )
    draft = result.scalar_one_or_none()
    
    if draft:
        # Update existing
        draft.template_id = request.template_id
        draft.state_json = request.state_json
    else:
        # Create new
        draft = BuilderDraft(
            user_id=current_user.id,
            resume_id=request.resume_id,
            template_id=request.template_id,
            state_json=request.state_json
        )
        db.add(draft)
        
    await db.commit()
    await db.refresh(draft)
    
    return DraftResponse(
        id=draft.id,
        resume_id=draft.resume_id,
        template_id=draft.template_id,
        state_json=draft.state_json
    )
