"""
VLM (Vision Language Model) extractor — Image-only resume extraction path.

Provider: NVIDIA NIM (Llama 3.2 Vision) by default.
Supports: nvidia, openai, gemini via VLM_PROVIDER config.

Sends the resume image to a VLM with a structured prompt that
forces section-wise JSON output.
"""

import json
import logging
import base64
from pathlib import Path
from typing import Dict, List

from app.core.extraction import ExtractionResult
from app.core.extraction.text_cleaner import clean_text
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── VLM Prompt ─────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expert resume parser. Analyze this resume image and extract ALL content into structured sections.

Return a JSON object with these exact keys. If a section is not present in the resume, use an empty string "".

{
  "summary": "Professional summary or objective statement",
  "education": "All education entries with degree, institution, CGPA/GPA, dates",
  "skills": "All technical and soft skills, categorized if visible (languages, frameworks, tools, soft skills)",
  "experience": "All work experience and internship entries with company, role, dates, and bullet points",
  "projects": "All projects with name, description, tech stack used, and outcomes/results",
  "certifications": "All certifications with name, issuer, and date",
  "achievements": "Awards, honors, competitions, hackathons",
  "publications": "Research papers, articles, blog posts",
  "community": "Open source contributions, volunteering, community involvement",
  "languages": "Spoken/written languages and proficiency levels",
  "contact": "Name, email, phone, location, LinkedIn, GitHub, portfolio URLs"
}

CRITICAL RULES:
1. Extract EVERY piece of text from the image — do not skip or summarize anything
2. Preserve exact wording, numbers, dates, and formatting from the resume
3. For bullet points, keep them as separate lines prefixed with "- "
4. If multiple entries exist in a section (e.g., multiple jobs), separate them with a blank line
5. Return ONLY the JSON object — no markdown, no explanation, no code fences
6. If you cannot read certain text clearly, include it with [unclear] marker"""


# ── Main Extraction ────────────────────────────────────────────────────────────

async def extract_image(file_path: str) -> ExtractionResult:
    """
    Legacy wrapper for image extraction. Routes to unified VLM pipeline.
    """
    return await extract_resume_vlm(file_path)


async def extract_resume_vlm(file_path: str) -> ExtractionResult:
    """
    Send resume PDF or image to VLM and parse section-wise structured output.
    """
    try:
        file_ext = Path(file_path).suffix.lower()

        if file_ext == ".pdf":
            from app.core.extraction.pdf_to_images import pdf_to_base64_images
            logger.info(f"Converting PDF to images for VLM: {file_path}")
            image_b64s = pdf_to_base64_images(file_path, dpi=100)  # 100 DPI keeps quality while reducing payload ~2.25x vs 150 DPI
            media_type = "image/png"
        else:
            logger.info(f"Reading image for VLM: {file_path}")
            image_b64s = [_encode_image(file_path)]
            media_type = _get_media_type(file_ext)

        if not image_b64s:
            raise ValueError(f"No pages/images extracted from: {file_path}")

        provider = settings.VLM_PROVIDER.lower()

        if provider == "nvidia":
            sections = await _call_nvidia_vlm(image_b64s, media_type)
        elif provider == "openai":
            sections = await _call_openai_vlm(image_b64s, media_type)
        elif provider == "gemini":
            sections = await _call_gemini_vlm(image_b64s, media_type)
        else:
            raise ValueError(f"Unknown VLM_PROVIDER: {provider}")

        # Clean all section texts
        cleaned_sections: Dict[str, str] = {}
        for key, value in sections.items():
            cleaned = clean_text(str(value)) if value else ""
            if cleaned:
                cleaned_sections[key] = cleaned

        # Build full raw text from sections
        raw_text_parts = []
        for label, content in cleaned_sections.items():
            raw_text_parts.append(f"[{label.upper()}]")
            raw_text_parts.append(content)
            raw_text_parts.append("")
        raw_text = "\n".join(raw_text_parts)

        logger.info(
            f"VLM extraction complete ({provider}): {len(cleaned_sections)} sections, "
            f"{len(raw_text)} chars"
        )

        return ExtractionResult(
            method="vlm",
            raw_text=raw_text,
            content_blocks=None,
            sections=cleaned_sections,
            metadata={
                "vlm_provider": provider,
                "model": settings.VLM_MODEL,
                "sections_found": list(cleaned_sections.keys()),
                "total_chars": len(raw_text),
                "pages_converted": len(image_b64s) if file_ext == ".pdf" else 1,
            }
        )

    except Exception as e:
        logger.error(f"VLM extraction failed for {file_path}: {e}")
        raise


# ── NVIDIA NIM API Call ────────────────────────────────────────────────────────

async def _call_nvidia_vlm(image_b64s: List[str], media_type: str) -> Dict[str, str]:
    """Call NVIDIA NIM API with Llama 3.2 Vision for one or more pages."""
    import httpx

    api_key = settings.VLM_API_KEY
    # Force use of 11b model as 90b has a known truncation issue with large images
    model = "meta/llama-3.2-11b-vision-instruct"
    if not api_key:
        raise ValueError("VLM_API_KEY is not set. Required for NVIDIA VLM extraction.")

    if len(image_b64s) > 1:
        logger.warning("NVIDIA NIM (Llama 3.2 Vision) only supports 1 image per request by default. The extraction might fail.")
        
    content_list = [{"type": "text", "text": EXTRACTION_PROMPT}]
    for img_b64 in image_b64s:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{img_b64}",
            },
        })

    import asyncio
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a JSON-only resume parser. "
                                    "You MUST output a single valid JSON object and nothing else. "
                                    "No markdown, no explanation, no code fences, no prose. "
                                    "Output ONLY the raw JSON object starting with { and ending with }."
                                ),
                            },
                            {
                                "role": "user",
                                "content": content_list,
                            },
                        ],
                        "max_tokens": 4096,
                        "temperature": 0.1,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return _parse_vlm_response(data)
                
        except httpx.HTTPError as e:
            error_details = ""
            if hasattr(e, "response") and e.response:
                error_details = f" - Status: {e.response.status_code} - {e.response.text}"
                
            logger.warning(f"NVIDIA NIM API Error (attempt {attempt + 1}/{max_retries}): {e}{error_details}")
            if attempt == max_retries - 1:
                logger.error(f"NVIDIA NIM API failed completely after {max_retries} attempts.")
                raise
            await asyncio.sleep(2 ** attempt)


# ── OpenAI Vision API Call ─────────────────────────────────────────────────────

async def _call_openai_vlm(image_b64s: List[str], media_type: str) -> Dict[str, str]:
    """Call OpenAI GPT-4o vision API for one or more pages."""
    import httpx

    api_key = settings.VLM_API_KEY
    if not api_key:
        raise ValueError("VLM_API_KEY is not set. Required for OpenAI VLM extraction.")

    model_name = settings.VLM_MODEL
    if not (model_name.startswith("gpt") or model_name.startswith("o1") or model_name.startswith("o3")):
        model_name = "gpt-4o"

    content_list = [{"type": "text", "text": EXTRACTION_PROMPT}]
    for img_b64 in image_b64s:
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{media_type};base64,{img_b64}",
                "detail": "high",
            },
        })

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": content_list,
                    }
                ],
                "max_tokens": 4096,
                "temperature": 0.1,
            },
        )
        response.raise_for_status()
        data = response.json()

    return _parse_vlm_response(data)


# ── Gemini Vision API Call ─────────────────────────────────────────────────────

async def _call_gemini_vlm(image_b64s: List[str], media_type: str) -> Dict[str, str]:
    """Call Google Gemini Vision API for one or more pages."""
    import google.generativeai as genai

    api_key = settings.VLM_API_KEY
    if not api_key:
        raise ValueError("VLM_API_KEY is not set. Required for Gemini VLM extraction.")

    model_name = settings.VLM_MODEL
    if not model_name.startswith("gemini"):
        model_name = "gemini-1.5-flash"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    contents = [EXTRACTION_PROMPT]
    for img_b64 in image_b64s:
        contents.append({"mime_type": media_type, "data": img_b64})

    response = await model.generate_content_async(contents)

    content = response.text.strip()
    return _clean_and_parse_json(content)


# ── Shared Helpers ─────────────────────────────────────────────────────────────

def _parse_vlm_response(data: dict) -> Dict[str, str]:
    """Parse OpenAI-compatible chat completion response."""
    choice = data["choices"][0]
    finish_reason = choice.get("finish_reason", "unknown")
    content = choice["message"]["content"] or ""

    # Log the raw response so we can debug unexpected outputs
    logger.info(f"VLM finish_reason: {finish_reason}")
    logger.info(f"VLM raw content (first 500 chars): {repr(content[:500])}")

    if finish_reason == "length":
        logger.warning(
            "VLM response was truncated (finish_reason=length). "
            "The resume may be too long for max_tokens=4096. "
            "Attempting to parse partial JSON..."
        )

    if not content.strip():
        raise ValueError(
            f"VLM returned empty content (finish_reason={finish_reason}). "
            "The model may have refused to process the image or the payload was too large."
        )

    return _clean_and_parse_json(content)


def _clean_and_parse_json(content: str) -> Dict[str, str]:
    """Strip markdown fences and parse JSON, with robust fallback handling."""
    import re
    content = content.strip()

    # Strip opening code fence
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    # Strip closing code fence
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    # Strip 'json' language identifier after fence
    if content.startswith("json"):
        content = content[4:].strip()

    if not content:
        raise ValueError("VLM response content is empty after stripping markdown fences.")

    # First attempt: direct JSON parse
    try:
        sections = json.loads(content)
        if not isinstance(sections, dict):
            raise ValueError(f"VLM returned non-dict: {type(sections)}")
        return sections
    except json.JSONDecodeError:
        pass

    # BUG-02 FALLBACK: model returned Markdown prose wrapping the JSON
    # Extract the first complete {...} JSON object from arbitrary text
    match = re.search(r'\{[\s\S]+\}', content)
    if match:
        try:
            extracted = match.group(0)
            sections = json.loads(extracted)
            if isinstance(sections, dict):
                logger.warning(
                    "VLM returned Markdown prose instead of raw JSON. "
                    "Extracted JSON object via regex fallback. "
                    "Add stronger system prompt to fix this."
                )
                return sections
        except json.JSONDecodeError:
            pass

    # Attempt to close truncated JSON (finish_reason=length edge case)
    last_brace = content.rfind(',"')
    if last_brace > 0:
        truncated = content[:last_brace] + "}"
        try:
            sections = json.loads(truncated)
            if isinstance(sections, dict):
                logger.warning("Parsed truncated JSON by stripping last incomplete field.")
                return sections
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"VLM JSON parse failed after all fallbacks.\n"
        f"Raw content (first 500 chars): {content[:500]}"
    )


def _encode_image(file_path: str) -> str:
    """Read image file, resize if needed (max 1120px for NVIDIA NIM), and encode as base64 string."""
    try:
        from PIL import Image
        import io
        
        with Image.open(file_path) as img:
            # Convert RGBA to RGB for JPEG compatibility just in case
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # NVIDIA NIM max dimension is 1120
            MAX_DIM = 1120
            if img.width > MAX_DIM or img.height > MAX_DIM:
                # Calculate new size preserving aspect ratio
                ratio = min(MAX_DIM / img.width, MAX_DIM / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            buffer = io.BytesIO()
            # Save as PNG to maintain quality
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except ImportError:
        # Fallback if Pillow is not available
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


def _get_media_type(extension: str) -> str:
    """Map file extension to MIME type."""
    types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    return types.get(extension, "image/jpeg")
