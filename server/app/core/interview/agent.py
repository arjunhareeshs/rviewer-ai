import logging
from typing import AsyncIterable
from livekit import rtc
from livekit.agents import JobContext, JobProcess, WorkerOptions, cli, llm
from livekit.agents.voice import Agent as VoicePipelineAgent
from livekit.plugins import silero

from app.config import get_settings
from app.core.interview.session_manager import session_manager
from app.core.interview.flow_manager import flow_manager
from app.models.interview import ChatMessage, InterviewPhase
import datetime
import asyncio
from pathlib import Path


logger = logging.getLogger(__name__)
settings = get_settings()


def _create_stt_plugin():
    """Create STT plugin based on STT_PROVIDER config.  Default: Groq Whisper."""
    provider = settings.STT_PROVIDER.lower()
    api_key = settings.STT_API_KEY

    if not api_key:
        raise ValueError(f"STT_API_KEY not set for provider {provider}. Speech-to-text will not work.")

    if provider == "groq":
        # Groq Whisper uses OpenAI-compatible endpoint
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.STT(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model=settings.STT_MODEL,
        )
    elif provider == "deepgram":
        from livekit.plugins import deepgram
        return deepgram.STT(
            api_key=api_key,
            model=settings.STT_MODEL,
        )
    else:
        raise ValueError(f"Unknown STT_PROVIDER: {provider}")


def _create_tts_plugin():
    """Create TTS plugin based on TTS_PROVIDER config.  Default: Deepgram."""
    provider = settings.TTS_PROVIDER.lower()
    api_key = settings.TTS_API_KEY

    if not api_key:
        raise ValueError(f"TTS_API_KEY not set for provider {provider}. Text-to-speech will not work.")

    if provider == "deepgram":
        from livekit.plugins import deepgram
        return deepgram.TTS(
            api_key=api_key,
            model=settings.TTS_MODEL,
        )
    elif provider == "openai":
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.TTS(
            api_key=api_key,
            model=settings.TTS_MODEL,
        )
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {provider}")


def _create_llm_plugin():
    """Create LLM plugin for the voice agent based on LLM_PROVIDER config."""
    provider = settings.LLM_PROVIDER.lower()
    api_key = settings.LLM_API_KEY

    if not api_key:
        raise ValueError("LLM_API_KEY not set. Cannot create interview agent.")

    if provider == "openrouter":
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.LLM(
            model=settings.LLM_MODEL,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    elif provider == "groq":
        from livekit.plugins import groq
        return groq.LLM(
            model=settings.LLM_MODEL,
            api_key=api_key,
        )
    elif provider == "openai":
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.LLM(
            model=settings.LLM_MODEL,
            api_key=api_key,
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


async def create_interviewer_agent(
    ctx: JobContext, 
    room_name: str, 
    candidate_name: str, 
    resume_context: str
) -> VoicePipelineAgent:
    """Create and configure the Voice Assistant agent."""
    
    session = await session_manager.get_session(room_name)
    if not session:
        logger.warning(f"Session not found for room {room_name}, falling back to default context.")
        
    prompt_path = Path("app/core/interview/prompts/interview.md")
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = "You are a technical interviewer at a top tech company."

    initial_instructions = (
        f"{system_prompt}\n\n"
        f"## Candidate Context:\n"
        f"Candidate Name: {candidate_name}\n"
        f"Resume Summary:\n{resume_context}\n\n"
        f"## Current Phase Instructions:\n"
        f"{flow_manager.get_phase_instructions(session.state.phase if session else InterviewPhase.INTRODUCTION)}"
    )

    vad = ctx.proc.userdata.get("vad")
    if not vad:
        vad = silero.VAD.load(
            min_speech_duration=settings.VAD_MIN_SPEECH_MS / 1000.0,
            min_silence_duration=settings.VAD_MIN_SILENCE_MS / 1000.0,
            activation_threshold=settings.VAD_THRESHOLD
        )

    assistant = VoicePipelineAgent(
        vad=vad,
        stt=_create_stt_plugin(),
        llm=_create_llm_plugin(),
        tts=_create_tts_plugin(),
        chat_ctx=llm.ChatContext().append(
            role="system",
            text=initial_instructions,
        ),
    )

    @assistant.on("user_speech_committed")
    def on_user_speech(msg: llm.ChatMessage):
        if session:
            session.state.history.append(
                ChatMessage(
                    role="user", 
                    content=msg.content or "", 
                    phase=session.state.phase,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
            )
            session.state.exchange_count += 1
            
            # Check phase transition
            if flow_manager.check_phase_transition(session.state):
                logger.info(f"Transitioning to phase {session.state.phase}")
                instructions = flow_manager.get_phase_instructions(session.state.phase)
                assistant.chat_ctx.append(role="system", text=f"PHASE TRANSITION: Transition to {session.state.phase.value} phase. Instructions: {instructions}")
                
            # Asynchronously save state to file
            asyncio.create_task(session_manager.save_session(session))

    @assistant.on("agent_speech_committed")
    def on_agent_speech(msg: llm.ChatMessage):
        if session:
            session.state.history.append(
                ChatMessage(
                    role="assistant", 
                    content=msg.content or "", 
                    phase=session.state.phase,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
            )
            # Asynchronously save state to file
            asyncio.create_task(session_manager.save_session(session))

    return assistant
