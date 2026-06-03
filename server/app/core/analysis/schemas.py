from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# ── ATS Analyzer Schemas ──────────────────────────────────────────────

class ATSCriterionScore(BaseModel):
    name: str
    score: int
    passed: bool
    details: str

class ATSGap(BaseModel):
    criterion: str
    severity: str  # critical, major, minor
    description: str
    recommendation: str

class ATSResult(BaseModel):
    overall_score: int
    criteria_scores: List[ATSCriterionScore]
    gaps: List[ATSGap]
    recommendations: List[str]

# ── Role Recommender Schemas ──────────────────────────────────────────

class RoleMatch(BaseModel):
    role_name: str
    match_percentage: int
    required_skills_match: List[str]
    missing_required_skills: List[str]
    preferred_skills_match: List[str]
    project_evidence: List[str]

class RoleRecommendationResult(BaseModel):
    recommendations: List[RoleMatch]
    top_role: Optional[str] = None

# ── Project Analyzer Schemas ──────────────────────────────────────────

class ProjectScore(BaseModel):
    project_name: str
    tech_score: int
    complexity_score: int
    impact_score: int
    total_score: int
    strengths: List[str]
    areas_for_improvement: List[str]

class ProjectAnalysisResult(BaseModel):
    overall_project_score: int
    projects: List[ProjectScore]
    roadmap: Optional[Dict[str, Any]] = None

# ── Link Analysis Schemas ─────────────────────────────────────────────

class LinkPlatformData(BaseModel):
    platform: str
    username: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    activity_data: Optional[Dict[str, Any]] = None  # For heatmaps, timelines
    valid_link: bool
    error: Optional[str] = None

class LinkAnalysisResult(BaseModel):
    platforms: List[LinkPlatformData]
    overall_presence_score: int

# ── Combined DB/Response Schema ───────────────────────────────────────

class FullAnalysisResponse(BaseModel):
    resume_id: str
    ats_score: int
    ats_result: ATSResult
    role_recommendations: RoleRecommendationResult
    project_analysis: ProjectAnalysisResult
    link_analysis: LinkAnalysisResult
    standardized_resume: Optional[Dict[str, Any]] = None
    overall_score: int
