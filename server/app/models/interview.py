from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class InterviewPhase(str, Enum):
    INTRODUCTION = "introduction"
    TECHNICAL = "technical"
    CRITICAL = "critical"
    CLOSING = "closing"

class ChatMessage(BaseModel):
    role: str
    content: str
    phase: InterviewPhase
    timestamp: datetime

class EvaluationScore(BaseModel):
    answer_quality: float
    technical_correctness: float
    communication: float
    problem_solving: float
    attitude_confidence: float
    overall_recommendation: float
    feedback_details: Dict[str, str]
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]

class InterviewState(BaseModel):
    phase: InterviewPhase = InterviewPhase.INTRODUCTION
    exchange_count: int = 0
    history: List[ChatMessage] = []
    resume_context: str = ""
    evaluation: Optional[EvaluationScore] = None

class InterviewSession(BaseModel):
    room_name: str
    candidate_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    state: InterviewState = InterviewState()
    resume_path: Optional[str] = None
    resume_parsed_text: Optional[str] = None
    report_pdf_path: Optional[str] = None
    vector_index: Any = None
