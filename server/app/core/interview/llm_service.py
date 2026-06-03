import json
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.models.interview import EvaluationScore
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMService:
    """
    Interview evaluation LLM.
    Uses the central LLM_PROVIDER / LLM_API_KEY from config.
    """
    def __init__(self):
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        provider = settings.LLM_PROVIDER.lower()
        api_key = settings.LLM_API_KEY
        model = settings.LLM_MODEL

        if not api_key:
            logger.warning("LLM_API_KEY not set. Interview evaluation will fail.")
            return

        if provider == "openrouter":
            logger.info(f"Interview LLM → OpenRouter ({model})")
            self.llm = ChatOpenAI(
                temperature=0.1,
                model=model,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                max_tokens=2048,
                default_headers={
                    "HTTP-Referer": settings.FRONTEND_URL,
                    "X-Title": settings.PROJECT_NAME,
                },
            )
        elif provider == "groq":
            from langchain_groq import ChatGroq
            logger.info(f"Interview LLM → Groq ({model})")
            self.llm = ChatGroq(
                temperature=0.1,
                model_name=model,
                groq_api_key=api_key,
                max_tokens=2048,
            )
        elif provider == "openai":
            logger.info(f"Interview LLM → OpenAI ({model})")
            self.llm = ChatOpenAI(
                temperature=0.1,
                model=model,
                api_key=api_key,
                max_tokens=2048,
            )
        else:
            logger.error(f"Unknown LLM_PROVIDER: {provider}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def evaluate_interview(self, transcript_text: str, evaluation_prompt_template: str) -> EvaluationScore:
        """Evaluate the interview transcript and return a structured score."""
        if not self.llm:
            raise ValueError("LLM is not initialized (missing LLM_API_KEY)")

        prompt = evaluation_prompt_template.replace("{transcript}", transcript_text)
        
        try:
            response = await self.llm.ainvoke(
                [
                    SystemMessage(content="You are an AI assistant that evaluates technical interviews and outputs ONLY valid JSON matching the requested schema. No markdown wrapping."),
                    HumanMessage(content=prompt)
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
            return EvaluationScore(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM evaluation JSON: {e}\nResponse content: {response.content}")
            raise
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            raise

llm_service = LLMService()
