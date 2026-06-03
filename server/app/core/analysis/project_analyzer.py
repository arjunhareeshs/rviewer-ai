import re
import logging
from typing import List, Dict
from app.core.analysis.schemas import ProjectScore, ProjectAnalysisResult
from app.core.analysis.tech_tier import calculate_tech_score
from app.schemas.resume import ProjectEntry

logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    """Analyzes projects for strength based on tech stack, complexity, and impact"""

    async def analyze(self, projects: List[ProjectEntry]) -> ProjectAnalysisResult:
        if not projects:
            return ProjectAnalysisResult(overall_project_score=0, projects=[])
            
        project_scores = []
        total_score_sum = 0
        
        for project in projects:
            name = project.name or "Unnamed Project"
            desc = project.description or ""
            techs = project.technologies or []
            
            strengths = []
            areas_for_improvement = []
            
            # 1. Tech Score (40%)
            tech_score_raw = calculate_tech_score(techs)
            
            if tech_score_raw >= 80:
                strengths.append("Uses highly relevant/modern tech stack")
            elif tech_score_raw < 40 and techs:
                areas_for_improvement.append("Consider upgrading legacy tech stack")
            elif not techs:
                areas_for_improvement.append("Missing technology stack details")
                
            tech_weighted = tech_score_raw * 0.40
            
            # 2. Complexity Score (30%)
            complexity_raw = 0
            desc_length = len(desc.split())
            
            if desc_length > 50:
                complexity_raw += 50
            elif desc_length > 20:
                complexity_raw += 30
            else:
                areas_for_improvement.append("Project description is too brief")
                
            complexity_keywords = ["implemented", "designed", "architected", "built", "developed", "deployed", "scaled"]
            found_keywords = sum(1 for kw in complexity_keywords if kw in desc.lower())
            
            if found_keywords >= 2:
                complexity_raw += 50
                strengths.append("Clear demonstration of engineering complexity")
            elif found_keywords == 1:
                complexity_raw += 25
                
            complexity_raw = min(100, complexity_raw)
            complexity_weighted = complexity_raw * 0.30
            
            # 3. Impact Score (30%)
            impact_raw = 0
            # Look for numbers, percentages, dollar amounts, or "users"
            if re.search(r'\d+[%$]', desc) or re.search(r'\b\d+\s*(users?|customers?|requests?|transactions?)\b', desc.lower()):
                impact_raw = 100
                strengths.append("Quantified impact and metrics provided")
            else:
                areas_for_improvement.append("Lacks quantified impact or business metrics")
                
            impact_weighted = impact_raw * 0.30
            
            # Total Score
            total_project_score = int(tech_weighted + complexity_weighted + impact_weighted)
            total_score_sum += total_project_score
            
            project_scores.append(
                ProjectScore(
                    project_name=name,
                    tech_score=tech_score_raw,
                    complexity_score=complexity_raw,
                    impact_score=impact_raw,
                    total_score=total_project_score,
                    strengths=strengths,
                    areas_for_improvement=areas_for_improvement
                )
            )
            
        overall = int(total_score_sum / len(projects)) if projects else 0
        
        return ProjectAnalysisResult(
            overall_project_score=overall,
            projects=project_scores
        )

# Singleton
project_analyzer = ProjectAnalyzer()
