import re
from pathlib import Path

def sanitize_filename(name: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove any path separators
    name = Path(name).name
    # Keep only alphanumeric, dash, underscore, and dot
    name = re.sub(r'[^a-zA-Z0-9_.-]', '', name)
    return name

def sanitize_room_name(name: str) -> str:
    """Sanitize room name (alphanumeric, hyphen, underscore only)"""
    return re.sub(r'[^a-zA-Z0-9_-]', '', name)

def validate_candidate_name(name: str) -> str:
    """Validate and sanitize candidate name"""
    # Keep only alphanumeric, spaces, dashes, apostrophes
    return re.sub(r"[^a-zA-Z0-9 \-']", '', name).strip()

def sanitize_for_prompt(text: str) -> str:
    """Basic protection against prompt injection in parsed text"""
    if not text:
        return ""
    # Remove XML/HTML-like tags to prevent prompt injection 
    # (since many system prompts use <instruction> blocks)
    text = re.sub(r'<[^>]*>', '', text)
    # Remove common system prompt overrides
    text = re.sub(r'(?i)(ignore previous instructions|system prompt|you are a)', '', text)
    return text
