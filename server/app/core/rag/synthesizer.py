import json
import logging
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas.resume import StandardizedResume
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ResumeSynthesizer:
    """
    Central LLM wrapper used across the platform.
    All text-generation tasks (synthesis, roadmap, NL filter, etc.) route through this.
    
    Provider: OpenRouter (default) — compatible with OpenAI SDK via base_url swap.
    """
    def __init__(self):
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        provider = settings.LLM_PROVIDER.lower()
        api_key = settings.LLM_API_KEY
        model = settings.LLM_MODEL

        if not api_key:
            logger.warning("LLM_API_KEY is not set. All LLM operations will fail.")
            return

        if provider == "openrouter":
            logger.info(f"Initializing LLM with OpenRouter → {model}")
            self.llm = ChatOpenAI(
                temperature=0.0,
                model=model,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                max_tokens=4000,
                default_headers={
                    "HTTP-Referer": settings.FRONTEND_URL,
                    "X-Title": settings.PROJECT_NAME,
                },
            )
        elif provider == "groq":
            logger.info(f"Initializing LLM with Groq → {model}")
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                temperature=0.0,
                model_name=model,
                groq_api_key=api_key,
                max_tokens=4000,
            )
        elif provider == "openai":
            logger.info(f"Initializing LLM with OpenAI → {model}")
            self.llm = ChatOpenAI(
                temperature=0.0,
                model=model,
                api_key=api_key,
                max_tokens=4000,
            )
        else:
            logger.error(f"Unknown LLM_PROVIDER: {provider}")

    async def synthesize(self, raw_sections: Dict[str, str]) -> StandardizedResume:
        """
        Takes raw extracted sections and standardizes them into the StandardizedResume schema.
        """
        if not self.llm:
            raise ValueError("LLM is not initialized (missing LLM_API_KEY)")

        prompt_text = (
            "You are an expert resume parser. I will provide you with raw text sections extracted from a candidate's resume. "
            "Your task is to analyze this content and structure it EXACTLY into the required JSON format. "
            "Do not hallucinate any information. If a field is not present in the resume, leave it as null or an empty list. "
            "Here is the raw extracted content (represented as a dictionary of visual sections):\n\n"
            f"{json.dumps(raw_sections, indent=2)}\n\n"
            "Please output a valid JSON strictly matching the requested structure."
        )

        try:
            structured_llm = self.llm.with_structured_output(StandardizedResume)
            
            response = await structured_llm.ainvoke(
                [
                    SystemMessage(content="You are an expert resume data extraction AI. You only output structured JSON."),
                    HumanMessage(content=prompt_text)
                ]
            )
            
            # Check for silent empty/blank output failure
            if not response or (not response.name and not response.skills and not response.experience):
                logger.warning("Structured LLM output is empty, falling back to manual parsing.")
                return await self._fallback_synthesize(prompt_text)
            
            return response
            
        except Exception as e:
            logger.error(f"Structured LLM synthesis failed, falling back to manual parsing: {e}")
            return await self._fallback_synthesize(prompt_text)

    async def _fallback_synthesize(self, prompt_text: str) -> StandardizedResume:
        schema_json = StandardizedResume.schema_json()
        fallback_prompt = (
            prompt_text + 
            f"\n\nYou MUST output raw JSON that conforms to this JSON Schema:\n{schema_json}\n"
            "DO NOT wrap in ```json markdown, just raw JSON."
        )
        
        response = await self.llm.ainvoke(
            [
                SystemMessage(content="You are an AI assistant that outputs ONLY valid JSON matching the requested schema. No markdown wrapping."),
                HumanMessage(content=fallback_prompt)
            ]
        )
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        data = json.loads(content)
        return StandardizedResume(**data)

    async def chat(self, messages: list, temperature: float = 0.0) -> str:
        """
        Generic LLM chat method used by roadmap generator, NL filter, etc.
        Accepts list of dicts [{'role': 'system'|'user', 'content': '...'}]
        Returns the raw string response.
        """
        if not self.llm:
            raise ValueError("LLM is not initialized (missing LLM_API_KEY)")

        langchain_messages = []
        for msg in messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            else:
                langchain_messages.append(HumanMessage(content=msg["content"]))

        response = await self.llm.ainvoke(langchain_messages)
        return response.content.strip()

synthesizer = ResumeSynthesizer()
