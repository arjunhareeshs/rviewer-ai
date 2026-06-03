from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.database import Base


# ── User (required for Resume foreign key) ─────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)  # Null for legacy/default users
    role = Column(String(50), default="user", nullable=False)  # "user" | "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user")

    def __repr__(self):
        return f"<User {self.email or self.id}>"


# ── Enums ──────────────────────────────────────────────────────────────────────

class FileType(str, enum.Enum):
    pdf = "pdf"
    image = "image"


class ResumeStatus(str, enum.Enum):
    uploaded = "uploaded"
    extracting = "extracting"
    embedding = "embedding"
    completed = "completed"
    failed = "failed"


class ExtractionMethod(str, enum.Enum):
    docling = "docling"
    vlm = "vlm"


# ── Resume ─────────────────────────────────────────────────────────────────────

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    status = Column(Enum(ResumeStatus), default=ResumeStatus.uploaded, nullable=False)
    raw_text = Column(Text, nullable=True)
    extraction_method = Column(Enum(ExtractionMethod), nullable=True)
    extraction_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
    chunks = relationship("ResumeChunk", back_populates="resume", cascade="all, delete-orphan")
    analysis = relationship("ResumeAnalysis", back_populates="resume", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume {self.id} ({self.filename})>"


# ── ResumeSection (Structured Store — used for LLM input & image display) ──────

class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    section_label = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    section_order = Column(Integer, nullable=False, default=0)
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="sections")
    chunks = relationship("ResumeChunk", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResumeSection {self.section_label} (resume={self.resume_id})>"


# ── ResumeChunk (Vector-indexed chunks — PDF path only) ────────────────────────

class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("resume_sections.id", ondelete="CASCADE"), nullable=True, index=True)
    section_label = Column(String(100), nullable=False)
    raw_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    vector_id = Column(String(255), nullable=True)
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="chunks")
    section = relationship("ResumeSection", back_populates="chunks")

    def __repr__(self):
        return f"<ResumeChunk {self.chunk_index} section={self.section_label} (resume={self.resume_id})>"

# ── ResumeAnalysis (Stores all analysis results) ───────────────────────────────

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    ats_score = Column(Integer, nullable=False, default=0)
    ats_criteria = Column(JSON, nullable=True)
    role_recommendations = Column(JSON, nullable=True)
    project_analysis = Column(JSON, nullable=True)
    link_analysis = Column(JSON, nullable=True)
    standardized_resume = Column(JSON, nullable=True)
    overall_score = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="analysis")

    def __repr__(self):
        return f"<ResumeAnalysis score={self.overall_score} (resume={self.resume_id})>"
