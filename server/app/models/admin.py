from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.database import Base

class Shortlist(Base):
    """
    Tracks candidates shortlisted by specific admins.
    """
    __tablename__ = "shortlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    admin = relationship("User", backref="shortlisted_candidates")
    resume = relationship("Resume", backref="shortlisted_by")

class RecruiterNote(Base):
    """
    Private notes attached to a candidate by an admin.
    """
    __tablename__ = "recruiter_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    admin = relationship("User", backref="candidate_notes")
    resume = relationship("Resume", backref="recruiter_notes")
