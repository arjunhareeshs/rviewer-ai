import logging
from typing import List, Dict, Any, Optional
from app.core.analysis.schemas import RoleMatch, RoleRecommendationResult
from app.core.analysis.role_taxonomy import ROLE_TAXONOMY
from app.schemas.resume import StandardizedResume

logger = logging.getLogger(__name__)

class RoleRecommender:
    """Engine to recommend best-fit roles based on skills and projects"""

    async def recommend(self, resume: StandardizedResume) -> RoleRecommendationResult:
        """
        Evaluate candidate skills and projects against the Role Taxonomy.
        
        Args:
            resume: The standardized JSON representation of the resume
            
        Returns:
            RoleRecommendationResult containing top 5 matched roles.
        """
        # Lowercase candidate skills for matching
        candidate_skills = [s.lower().strip() for s in resume.skills] if resume.skills else []
        
        # Extract text from projects to find keywords
        project_texts = []
        if resume.projects:
            for proj in resume.projects:
                text = f"{proj.name or ''} {proj.description or ''} {' '.join(proj.technologies or [])}".lower()
                project_texts.append(text)
        candidate_projects_text = " ".join(project_texts)
        
        # If candidate has no skills or projects, we can't recommend much
        if not candidate_skills and not candidate_projects_text:
            return RoleRecommendationResult(recommendations=[], top_role=None)
            
        scored_roles = []
        
        for role_id, role_def in ROLE_TAXONOMY.items():
            req_skills = [s.lower() for s in role_def.get("required_skills", [])]
            pref_skills = [s.lower() for s in role_def.get("preferred_skills", [])]
            proj_keywords = [k.lower() for k in role_def.get("project_keywords", [])]
            
            # 1. Match Required Skills
            req_match = []
            missing_req = []
            for rs in req_skills:
                # Simple exact/substring match logic
                if any(rs in cs or cs in rs for cs in candidate_skills):
                    req_match.append(rs)
                else:
                    missing_req.append(rs)
                    
            req_score = (len(req_match) / len(req_skills)) * 100 if req_skills else 0
            
            # 2. Match Preferred Skills
            pref_match = []
            for ps in pref_skills:
                if any(ps in cs or cs in ps for cs in candidate_skills):
                    pref_match.append(ps)
                    
            pref_score = (len(pref_match) / len(pref_skills)) * 100 if pref_skills else 0
            
            # 3. Match Project Keywords
            proj_match = []
            for pk in proj_keywords:
                if pk in candidate_projects_text:
                    proj_match.append(pk)
                    
            proj_score = (len(proj_match) / len(proj_keywords)) * 100 if proj_keywords else 0
            
            # 4. Final Score (50% Required, 30% Preferred, 20% Project)
            final_score = int((req_score * 0.5) + (pref_score * 0.3) + (proj_score * 0.2))
            
            scored_roles.append(
                RoleMatch(
                    role_name=role_def.get("display_name", role_id),
                    match_percentage=final_score,
                    required_skills_match=req_match,
                    missing_required_skills=missing_req,
                    preferred_skills_match=pref_match,
                    project_evidence=proj_match
                )
            )
            
        # Sort by match percentage descending
        scored_roles.sort(key=lambda x: x.match_percentage, reverse=True)
        
        # Take top 5
        top_5 = scored_roles[:5]
        
        return RoleRecommendationResult(
            recommendations=top_5,
            top_role=top_5[0].role_name if top_5 else None
        )

# Singleton
role_recommender = RoleRecommender()
