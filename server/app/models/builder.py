from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base

class ResumeTemplate(Base):
    """
    Stores the layout schema extracted by Gemini Vision for custom templates.
    """
    __tablename__ = "resume_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    is_premium = Column(Boolean, default=False)
    
    # The JSON schema detailing columns, font sizes, layouts, colors, etc.
    schema_json = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ResumeTemplate {self.name}>"

class BuilderDraft(Base):
    """
    Stores the current state of a user's resume being built in the builder.
    """
    __tablename__ = "builder_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("resume_templates.id"), nullable=True)
    
    # This stores the populated content and the overridden style configurations
    # from the builder state (Zustand store snapshot).
    state_json = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    template = relationship("ResumeTemplate")

    def __repr__(self):
        return f"<BuilderDraft {self.id}>"
