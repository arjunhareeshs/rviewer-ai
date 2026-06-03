import json
import logging
from typing import Dict, Any

from app.core.rag.synthesizer import synthesizer
from app.core.roadmap.link_fetcher import attach_links_to_roadmap

logger = logging.getLogger(__name__)

ROADMAP_PROMPT = """
You are an expert technical career coach and technical architect.
You will receive a candidate's parsed resume and their target role.
You must perform a deep gap analysis and generate a personalized, structured learning roadmap.

The output MUST be a valid JSON object following this EXACT schema, no prose, no markdown formatting outside of the JSON structure itself (return ONLY the raw JSON string):

{
  "candidate": "Candidate Name",
  "target_role": "Target Role",
  "total_duration": "Total estimated time (e.g., '6 months')",
  "current_state": {
    "label": "Current Profile",
    "strengths": ["List of 3-5 key existing skills matching the role"],
    "score": "Numeric score 0-100"
  },
  "tracks": [
    {
      "track_id": "unique_track_id",
      "track_name": "Name of the learning track (e.g., 'ML Core')",
      "color": "Hex color code for this track",
      "nodes": [
        {
          "id": "n1",
          "label": "Actionable skill or project to learn/build (e.g., 'Master PyTorch')",
          "type": "skill|project|certification",
          "priority": "critical|high|medium|low",
          "duration": "Estimated time (e.g., '3 weeks')",
          "depends_on": ["List of node IDs that must be completed before this"],
          "milestone": false
        }
      ]
    }
  ],
  "milestones": [
    {
      "id": "m1",
      "label": "Name of milestone (e.g., 'Internship Ready')",
      "at_week": 6,
      "requires": ["List of node IDs required to unlock this"]
    }
  ]
}

Instructions:
1. Identify what the candidate already knows (Current State).
2. Identify what is missing for the Target Role.
3. Group the gaps into parallel tracks (e.g., Core Track, DevOps Track, Cloud Track, Soft Skills). Provide 3-5 tracks.
4. Provide actionable nodes (skills, projects). Assign realistic durations.
5. Create dependencies (`depends_on`) so the mindmap graphs logically.
6. Define 2-4 milestones that converge branches.
7. Return ONLY valid JSON.
"""

async def generate_skill_roadmap(resume_content: Dict[str, Any], target_role: str, analysis_scores: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generates a structured roadmap JSON using the LLM and attaches live links to the nodes.
    Uses synthesizer.chat() which routes through the configured LLM provider.
    """
    input_data = {
        "resume": resume_content,
        "target_role": target_role,
        "analysis_scores": analysis_scores or {}
    }
    
    messages = [
        {"role": "system", "content": ROADMAP_PROMPT},
        {"role": "user", "content": f"Candidate Profile & Target:\n{json.dumps(input_data, indent=2)}"}
    ]
    
    try:
        raw_json_str = await synthesizer.chat(messages, temperature=0.4)
        
        # Clean up any potential markdown block wrappers
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.startswith("```"):
            raw_json_str = raw_json_str[3:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
            
        roadmap_json = json.loads(raw_json_str.strip())
        
        # Attach live links to the generated nodes via DDGS
        enriched_roadmap = await attach_links_to_roadmap(roadmap_json)
        
        return enriched_roadmap
        
    except Exception as e:
        logger.error(f"Failed to generate roadmap: {e}")
        raise ValueError("LLM Roadmap generation failed.") from e
