from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base

class Roadmap(Base):
    """
    Persists the full JSON schema of a generated roadmap for a specific resume/user.
    This enables versioning and loading past states.
    """
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    # Target role input that was used for this generation
    target_role = Column(String, nullable=False)
    
    # The full JSON tree mapping tracks, nodes, resources, and milestones
    schema_json = Column(JSON, nullable=False)
    
    # Store any state (e.g. which nodes are checked off)
    progress_json = Column(JSON, nullable=False, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", backref="roadmaps")
