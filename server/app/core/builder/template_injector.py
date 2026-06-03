import base64
import json
import logging
import os
from typing import Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Fallback JSON structure if API fails
DEFAULT_TEMPLATE_SCHEMA = {
    "layout_type": "single_column",
    "column_ratio": [1.0, 0.0],
    "header": {
        "alignment": "center",
        "name_size": "large",
        "name_weight": "bold",
        "contact_layout": "inline",
        "has_photo": False,
        "has_accent_bar": False
    },
    "sections": [
        {
            "name": "Summary",
            "column": "full",
            "heading_style": "uppercase",
            "heading_underline": True,
            "heading_accent_color": False,
            "item_layout": "stacked",
            "has_bullets": False
        },
        {
            "name": "Experience",
            "column": "full",
            "heading_style": "uppercase",
            "heading_underline": True,
            "heading_accent_color": False,
            "item_layout": "inline_date_right",
            "has_bullets": True
        }
    ],
    "typography": {
        "primary_font": "Inter",
        "section_title_size": 12,
        "body_size": 10,
        "name_size": 24
    },
    "colors": {
        "accent": "#000000",
        "sidebar_bg": "none",
        "header_bg": "none"
    },
    "dividers": "line",
    "bullet_style": "dot"
}

class TemplateInjector:
    """
    Handles reverse-engineering a resume template from an image using Gemini Vision.
    """
    
    def __init__(self):
        # We will use the Google GenAI SDK if available, or fallback to OpenAI vision if preferred.
        # Based on instructions, we should use Gemini Vision (gemini-1.5-pro or gemini-2.0-flash).
        try:
            import google.generativeai as genai
            self.genai = genai
        except ImportError:
            self.genai = None
            logger.warning("google.generativeai not installed. TemplateInjector might not work if configured for gemini")
        
    async def extract_template_schema(self, base64_image: str) -> Dict[str, Any]:
        """
        Sends the base64 image of a resume template to VLM to extract
        the exact layout specification as JSON.
        
        Uses VLM_PROVIDER from settings (nvidia, openai, or gemini).
        """
        from app.config import get_settings
        settings = get_settings()
        
        api_key = settings.VLM_API_KEY
        if not api_key:
            logger.warning("No VLM_API_KEY found, returning default schema.")
            return DEFAULT_TEMPLATE_SCHEMA

        prompt = """
        Analyse this resume template image and extract the exact layout specification as JSON.
        Return ONLY raw JSON, with no markdown formatting or backticks.
        
        Structure required:
        {
          "layout_type": "single_column | two_column_sidebar_left | two_column_sidebar_right | two_column_equal",
          "column_ratio": [float, float],
          "header": {
            "alignment": "left | center | right",
            "name_size": "large | xlarge",
            "name_weight": "bold | extrabold",
            "contact_layout": "inline | stacked | icon_inline",
            "has_photo": boolean,
            "has_accent_bar": boolean
          },
          "sections": [
            {
              "name": "string (e.g. Education, Experience)",
              "column": "left | right | full",
              "heading_style": "uppercase | titlecase",
              "heading_underline": boolean,
              "heading_accent_color": boolean,
              "item_layout": "stacked | inline_date_right",
              "has_bullets": boolean
            }
          ],
          "typography": {
            "primary_font": "string",
            "section_title_size": int,
            "body_size": int,
            "name_size": int
          },
          "colors": {
            "accent": "hex string",
            "sidebar_bg": "hex string | none",
            "header_bg": "hex string | none"
          },
          "dividers": "line | space | none",
          "bullet_style": "dot | dash | none"
        }
        """

        try:
            provider = settings.VLM_PROVIDER.lower()
            
            if provider in ("nvidia", "openai"):
                import httpx
                base_url = "https://integrate.api.nvidia.com/v1/chat/completions" if provider == "nvidia" else "https://api.openai.com/v1/chat/completions"
                
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        base_url,
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={
                            "model": settings.VLM_MODEL,
                            "messages": [{"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]}],
                            "max_tokens": 4096, "temperature": 0.1, "stream": False,
                        },
                    )
                    response.raise_for_status()
                    text_response = response.json()["choices"][0]["message"]["content"]
            
            elif provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(settings.VLM_MODEL)
                image_parts = [{"mime_type": "image/jpeg", "data": base64_image}]
                resp = await model.generate_content_async([prompt, image_parts[0]])
                text_response = resp.text
            else:
                logger.error(f"Unknown VLM_PROVIDER: {provider}")
                return DEFAULT_TEMPLATE_SCHEMA

            # Clean markdown
            text_response = text_response.strip()
            if text_response.startswith("```json"): text_response = text_response[7:]
            if text_response.startswith("```"): text_response = text_response[3:]
            if text_response.endswith("```"): text_response = text_response[:-3]
                
            schema = json.loads(text_response.strip())
            return schema
            
        except Exception as e:
            logger.error(f"Failed to extract template schema: {e}")
            return DEFAULT_TEMPLATE_SCHEMA

template_injector = TemplateInjector()
