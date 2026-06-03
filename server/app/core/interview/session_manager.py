import asyncio
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.models.interview import InterviewSession, InterviewState, InterviewPhase

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.data_dir = Path("data/sessions")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()
        self._cleanup_task = None
        
    async def start_cleanup_task(self):
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_stale_sessions())

    async def stop_cleanup_task(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    def _get_path(self, room_name: str) -> Path:
        # Sanitize room_name to prevent path traversal
        clean_name = "".join(c for c in room_name if c.isalnum() or c in ("-", "_"))
        return self.data_dir / f"{clean_name}.json"

    async def save_session(self, session: InterviewSession):
        path = self._get_path(session.room_name)
        try:
            # Pydantic v2 model_dump_json properly handles serialization of datetimes
            data = session.model_dump_json(indent=2)
            # Sync write is fast for small JSONs; run in a executor if you want, but direct is fine
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            logger.info(f"Saved session state to {path}")
        except Exception as e:
            logger.error(f"Failed to save session {session.room_name}: {e}")

    async def create_session(self, room_name: str, candidate_name: str) -> InterviewSession:
        async with self._lock:
            session = InterviewSession(
                room_name=room_name,
                candidate_name=candidate_name,
                start_time=datetime.now(timezone.utc),
                state=InterviewState(phase=InterviewPhase.INTRODUCTION)
            )
            await self.save_session(session)
            return session

    async def get_or_create_session(self, room_name: str, candidate_name: str) -> InterviewSession:
        async with self._lock:
            session = await self.get_session(room_name)
            if session is not None:
                return session
            session = InterviewSession(
                room_name=room_name,
                candidate_name=candidate_name,
                start_time=datetime.now(timezone.utc),
                state=InterviewState(phase=InterviewPhase.INTRODUCTION)
            )
            await self.save_session(session)
            return session

    async def get_session(self, room_name: str) -> Optional[InterviewSession]:
        path = self._get_path(room_name)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            return InterviewSession.model_validate_json(data)
        except Exception as e:
            logger.error(f"Error loading session {room_name} from {path}: {e}")
            return None

    async def update_session(self, room_name: str, **kwargs):
        async with self._lock:
            session = await self.get_session(room_name)
            if session is not None:
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                await self.save_session(session)

    async def _cleanup_stale_sessions(self):
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                now = datetime.now(timezone.utc)
                stale_threshold = timedelta(hours=2)
                async with self._lock:
                    if self.data_dir.exists():
                        for path in self.data_dir.glob("*.json"):
                            try:
                                with open(path, "r", encoding="utf-8") as f:
                                    data = f.read()
                                session = InterviewSession.model_validate_json(data)
                                if (now - session.start_time) > stale_threshold:
                                    path.unlink(missing_ok=True)
                                    logger.info(f"Cleaned up stale session file {path}")
                            except Exception as e:
                                logger.error(f"Error checking stale session file {path}: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")

# Global instance
session_manager = SessionManager()
