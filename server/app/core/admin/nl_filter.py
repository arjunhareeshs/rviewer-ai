import json
import logging
from typing import Dict, Any, List

from app.core.rag.synthesizer import synthesizer

logger = logging.getLogger(__name__)

NL_FILTER_PROMPT = """
You are an AI assistant helping a recruiter search and filter a database of job candidates.
The recruiter will provide a natural language query (e.g., "show me candidates with python and docker", or "only those with ATS score above 70").
You have access to a conversation history containing previous queries and the active JSON filter state.

Your goal is to parse the user's latest query, merge it with the active filter state, and output a NEW valid JSON filter object that represents the updated query.
You must ALSO output a brief, professional natural language response summarizing what filters were applied and what the recruiter should expect to see.

The output MUST be a valid JSON object matching this schema:
{
  "filters": {
    "skills": ["list of exact skills to match, e.g. python, docker"],
    "ats_score_min": null or integer (0-100),
    "ats_score_max": null or integer (0-100),
    "interview_score_min": null or integer (0-100),
    "interview_completed": null or boolean,
    "role_match": null or string (e.g. "ML Engineer"),
    "institutions": ["list of college/university strings to match partially"],
    "has_internship": null or boolean,
    "has_certifications": null or boolean,
    "sort_by": "overall_score" | "ats_score" | "interview_score" | "recent",
    "sort_order": "asc" | "desc"
  },
  "ai_response": "Natural language summary of the action taken (e.g. 'Found candidates with Python and Docker. Showing those with ATS score > 70.')"
}

Instructions:
1. Extract any new filtering constraints from the user's message.
2. If the user asks to "remove" a filter (e.g., "ignore the ATS score requirement"), set that filter to null in the output.
3. If the user asks for a completely new search (e.g., "Start over. Show me Java devs"), ignore the previous active state and output fresh filters.
4. If it's a refinement (e.g., "and sort by score"), merge the new constraint with the `active_filters` provided.
5. Provide ONLY the JSON. No markdown wrappers.
"""

async def translate_nl_query_to_filter(user_message: str, chat_history: List[Dict[str, str]], active_filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes the recruiter's natural language message and current filter state,
    and returns a structured JSON object containing the updated SQL-compatible filters and the AI response string.
    
    Uses synthesizer.chat() which routes through the configured LLM provider.
    """
    
    messages = [
        {"role": "system", "content": NL_FILTER_PROMPT},
    ]
    
    # Append limited chat history for context
    for msg in chat_history[-5:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Append the current request containing the active state and new message
    current_request = {
        "active_filters": active_filters,
        "latest_user_message": user_message
    }
    messages.append({"role": "user", "content": json.dumps(current_request)})

    try:
        raw_json_str = await synthesizer.chat(messages, temperature=0.0)
        
        # Clean markdown
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.startswith("```"):
            raw_json_str = raw_json_str[3:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]
            
        parsed_result = json.loads(raw_json_str.strip())
        
        return {
            "filters": parsed_result.get("filters", {}),
            "ai_response": parsed_result.get("ai_response", "Filters updated.")
        }
        
    except Exception as e:
        logger.error(f"Failed to parse NL query to filter: {e}")
        return {
            "filters": active_filters,
            "ai_response": f"Sorry, I couldn't understand that filter request. Please try rephrasing."
        }
