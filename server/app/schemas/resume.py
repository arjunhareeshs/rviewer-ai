from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# ── Upload ─────────────────────────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    status: str
    extraction_method: Optional[str] = None
    created_at: datetime
    message: str = "Resume uploaded successfully"

    class Config:
        from_attributes = True


# ── Resume Metadata ────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_path: str
    file_type: str
    status: str
    extraction_method: Optional[str] = None
    raw_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    resumes: List[ResumeResponse]
    total: int


# ── Section ────────────────────────────────────────────────────────────────────

class ResumeSectionResponse(BaseModel):
    id: UUID
    section_label: str
    content: str
    section_order: int
    meta: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ResumeSectionsResponse(BaseModel):
    resume_id: UUID
    extraction_method: Optional[str] = None
    sections: List[ResumeSectionResponse]


class ResumeFullJSON(BaseModel):
    """Assembled JSON payload for LLM consumption — from structured store only."""
    doc_id: UUID
    sections: Dict[str, str]


# ── Standardized Extracted Resume ──────────────────────────────────────────────

class ExperienceEntry(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None

class EducationEntry(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    dates: Optional[str] = None
    metrics: Optional[str] = None

class ProjectEntry(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    location: Optional[str] = None

class StandardizedResume(BaseModel):
    """The final strict JSON representation of a resume."""
    name: Optional[str] = None
    role: Optional[str] = None
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    professional_summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)


# ── Retrieval (PDF path only) ──────────────────────────────────────────────────

class RetrievalRequest(BaseModel):
    resume_id: UUID
    query: str
    section_filter: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievalResult(BaseModel):
    chunk_text: str
    section: str
    score: float
    chunk_index: int


class RetrievalResponse(BaseModel):
    resume_id: UUID
    query: str
    results: List[RetrievalResult]
