"""
memory/session_store.py
Redis-backed conversation session memory.
Falls back to in-process dict if Redis is unavailable (useful for local dev without Redis).
"""

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

MAX_HISTORY = 20          # messages kept per session
TTL_SECONDS = 60 * 60 * 8  # 8-hour session TTL


class SessionStore:
    def __init__(self, redis_url: Optional[str] = None):
        self._fallback: dict[str, list] = {}
        self._redis = None

        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import redis
            self._redis = redis.Redis.from_url(url, decode_responses=True)
            self._redis.ping()
            logger.info("SessionStore connected to Redis at %s", url)
        except Exception as exc:
            logger.warning("Redis unavailable (%s). Using in-memory fallback.", exc)
            self._redis = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_history(self, session_id: str) -> list[dict]:
        """Return the conversation history as a list of {role, content} dicts."""
        if self._redis:
            raw = self._redis.get(self._key(session_id))
            if raw:
                return json.loads(raw)
            return []
        return list(self._fallback.get(session_id, []))

    def append(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        """Append a user/assistant exchange to the session history."""
        history = self.get_history(session_id)
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": assistant_msg})

        # Keep only the last MAX_HISTORY messages
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        self._save(session_id, history)

    def clear(self, session_id: str) -> None:
        """Delete a session."""
        if self._redis:
            self._redis.delete(self._key(session_id))
        else:
            self._fallback.pop(session_id, None)

    def all_sessions(self) -> list[str]:
        """List all active session IDs (Redis only)."""
        if self._redis:
            keys = self._redis.keys("hr_session:*")
            return [k.replace("hr_session:", "") for k in keys]
        return list(self._fallback.keys())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key(session_id: str) -> str:
        return f"hr_session:{session_id}"

    def _save(self, session_id: str, history: list[dict]) -> None:
        if self._redis:
            self._redis.setex(self._key(session_id), TTL_SECONDS, json.dumps(history))
        else:
            self._fallback[session_id] = history
