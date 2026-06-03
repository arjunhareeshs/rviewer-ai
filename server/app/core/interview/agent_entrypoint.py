import logging
from livekit.agents import AutoSubscribe, JobContext, JobProcess
from app.core.interview.agent import create_interviewer_agent
from app.core.interview.resume_service import resume_service

logger = logging.getLogger(__name__)

async def entrypoint(ctx: JobContext):
    """LiveKit agent entrypoint."""
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    room_name = ctx.room.name

    # Wait for the human participant to actually join the room
    logger.info("Waiting for participant to join...")
    participant = await ctx.wait_for_participant()
    candidate_name = participant.identity or "Candidate"

    # Build resume context: try FAISS index first, fall back to raw parsed text
    resume_context = ""
    index = resume_service.load_index(room_name)
    if index:
        try:
            resume_context = resume_service.query_resume(
                index, "Summarize experience, education, and skills."
            )
        except Exception as e:
            logger.warning(f"FAISS query failed: {e}")

    # Fallback: load raw text from session file
    if not resume_context:
        from app.core.interview.session_manager import session_manager
        session = await session_manager.get_session(room_name)
        if session and session.resume_parsed_text:
            # Truncate to avoid blowing up context window
            resume_context = session.resume_parsed_text[:3000]
            logger.info("Using raw resume text from session as context fallback.")

    agent = await create_interviewer_agent(ctx, room_name, candidate_name, resume_context)

    # Start agent with the verified participant
    agent.start(ctx.room, participant)
    logger.info(f"Agent started for participant: {candidate_name}")

    # Send personalized greeting
    await agent.say(
        f"Hello {candidate_name}, welcome to your technical interview. Are you ready to begin?",
        allow_interruptions=True
    )

def prewarm(proc: JobProcess):
    """Pre-warm models before the agent starts."""
    try:
        from livekit.plugins import silero
        from app.config import get_settings
        settings = get_settings()
        proc.userdata["vad"] = silero.VAD.load(
            min_speech_duration=settings.VAD_MIN_SPEECH_MS / 1000.0,
            min_silence_duration=settings.VAD_MIN_SILENCE_MS / 1000.0,
            activation_threshold=settings.VAD_THRESHOLD
        )
        logger.info("Silero VAD model prewarmed successfully.")
    except Exception as e:
        logger.warning(f"Failed to prewarm models: {e}")
