from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RViewer AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "dev"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rviewer"
    
    # Security / JWT
    SECRET_KEY: str = "super-secret-key-replace-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ── AI: LLM (Text Generation) — OpenRouter ───────────────
    LLM_PROVIDER: str = "openrouter"          # openrouter | groq | openai
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "meta-llama/llama-3.3-70b-instruct"
    
    # ── AI: VLM (Vision Language Model) — NVIDIA NIM ─────────
    VLM_PROVIDER: str = "nvidia"              # nvidia | openai | gemini
    VLM_API_KEY: Optional[str] = None
    VLM_MODEL: str = "meta/llama-3.2-90b-vision-instruct"
    EXTRACTION_METHOD: str = "auto"            # auto | vlm | docling
    
    # ── AI: STT (Speech-to-Text) — Groq Whisper ─────────────
    STT_PROVIDER: str = "groq"
    STT_API_KEY: Optional[str] = None
    STT_MODEL: str = "whisper-large-v3"
    
    # ── AI: TTS (Text-to-Speech) — Deepgram ──────────────────
    TTS_PROVIDER: str = "deepgram"
    TTS_API_KEY: Optional[str] = None
    TTS_MODEL: str = "aura-helios-en"
    
    # ── Link Analysis ────────────────────────────────────────
    GITHUB_TOKEN: Optional[str] = None
    KAGGLE_USERNAME: Optional[str] = None
    KAGGLE_KEY: Optional[str] = None
    STACKOVERFLOW_KEY: Optional[str] = None
    GITLAB_TOKEN: Optional[str] = None
    
    # ── LiveKit (Interview Infrastructure) ───────────────────
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"
    
    # ── Interview settings ───────────────────────────────────
    MAX_FILE_SIZE_MB: int = 10
    JWT_TOKEN_EXPIRY_MINUTES: int = 60
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # ── VAD settings ─────────────────────────────────────────
    VAD_THRESHOLD: float = 0.5
    VAD_MIN_SPEECH_MS: int = 150
    VAD_MIN_SILENCE_MS: int = 200
    
    # ── Legacy compat (kept for any code still referencing them) ──
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        if self.LLM_PROVIDER == "openai":
            return self.LLM_API_KEY
        if self.VLM_PROVIDER == "openai":
            return self.VLM_API_KEY
        return None
    
    @property
    def GROQ_API_KEY(self) -> Optional[str]:
        if self.LLM_PROVIDER == "groq":
            return self.LLM_API_KEY
        if self.STT_PROVIDER == "groq":
            return self.STT_API_KEY
        return None
    
    @property
    def DEEPGRAM_API_KEY(self) -> Optional[str]:
        return self.TTS_API_KEY
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
