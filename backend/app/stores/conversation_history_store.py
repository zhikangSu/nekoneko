"""In-process short-term conversation history for chat continuity (#82).

This is intentionally not a durable memory store. It keeps only a bounded recent
window per user so the next LLM call can resolve follow-up turns like "接着刚才"
without silently saving sensitive content to long-term memory.
"""

from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock

from app.schemas.conversation import ConversationMessage

DEFAULT_HISTORY_LIMIT = 10
MAX_CONTENT_CHARS = 1200


class ConversationHistoryStore:
    """Demo-scale, per-process short-term chat history keyed by user id."""

    def __init__(self, max_messages: int = DEFAULT_HISTORY_LIMIT) -> None:
        self._max_messages = max(2, max_messages)
        self._messages: dict[str, deque[ConversationMessage]] = defaultdict(
            lambda: deque(maxlen=self._max_messages)
        )
        self._lock = RLock()

    def recent(
        self,
        user_id: str,
        limit: int = DEFAULT_HISTORY_LIMIT,
    ) -> list[ConversationMessage]:
        """Return the newest bounded window without exposing internal storage."""

        safe_limit = max(0, min(limit, self._max_messages))
        if safe_limit == 0:
            return []
        with self._lock:
            return list(self._messages[user_id])[-safe_limit:]

    def append_turn(self, user_id: str, user_text: str, assistant_text: str) -> None:
        """Append one completed user/assistant turn to short-term history."""

        user_text = _trim(user_text)
        assistant_text = _trim(assistant_text)
        if not user_text or not assistant_text:
            return
        with self._lock:
            bucket = self._messages[user_id]
            bucket.append(ConversationMessage(role="user", content=user_text))
            bucket.append(ConversationMessage(role="assistant", content=assistant_text))

    def clear(self, user_id: str) -> None:
        """Clear one user's in-process history; mainly useful for tests."""

        with self._lock:
            self._messages.pop(user_id, None)


def _trim(value: str) -> str:
    return value.strip()[:MAX_CONTENT_CHARS]
