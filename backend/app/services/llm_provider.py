"""LLM provider interface and selection.

External providers sit behind this interface so the demo runs in
``DEMO_MODE=true`` without paid APIs (AGENTS.md §7). Slice 1 ships only the fake
provider; real providers (#5/#6 and later) implement the same interface. In
demo mode, an unimplemented provider name falls back to the fake provider.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.config import Settings
from app.core.constants import CompanionMode
from app.schemas.conversation import ConversationMessage

logger = logging.getLogger(__name__)

_FAKE_PROVIDER_NAMES = {"fake", "mock"}
# Names that select the real xiaomimimo LLM (#6 real). DEMO_MODE stays fake.
_XIAOMIMIMO_PROVIDER_NAMES = {"xiaomimimo", "mimo"}


@dataclass
class CompanionReplyInput:
    """Everything the provider needs to draft a companion reply.

    ``system_prompt`` is the persona prompt rendered by ``CompanionAgent`` (#6).
    Real providers use it as the system message; the fake provider ignores it
    and returns a deterministic template.
    """

    message: str
    mode: CompanionMode
    companion_display_name: str
    system_prompt: Optional[str] = None
    # External fact from InfoRetrievalTool (#13) to weave into the reply.
    retrieval_context: Optional[str] = None
    # Short-term, in-process history (#82). Real providers include this as
    # bounded chat messages before the current user turn; fake provider may use
    # it only for deterministic offline continuity checks.
    conversation_history: list[ConversationMessage] = field(default_factory=list)


class LLMProvider(ABC):
    """Minimal provider contract for Slice 1.

    The companion persona will move into ``CompanionAgent`` (#6); for now the
    provider returns a safe, warm baseline reply.
    """

    name: str = "base"

    @abstractmethod
    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        """Return a companion reply. Must never produce medical/dosage advice."""

    @property
    def generation_info(self) -> dict[str, Any]:
        """Metadata about the most recent generation, safe to expose in trace."""

        return {"provider": self.name, "used_fallback": False}


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Select an LLM provider.

    ``DEMO_MODE`` always uses the fake provider (so the demo needs no key and
    replies stay deterministic); only ``DEMO_MODE=false`` with a named real
    provider hits the live API (#6).
    """
    # Imported here to avoid a circular import at module load.
    from app.services.fake_llm_provider import FakeLLMProvider

    provider = (settings.llm_provider or "").strip().lower()
    if provider in _FAKE_PROVIDER_NAMES:
        return FakeLLMProvider()

    if settings.demo_mode:
        logger.info(
            "DEMO_MODE=true: using the fake LLM provider regardless of "
            "LLM_PROVIDER=%r.",
            provider,
        )
        return FakeLLMProvider()

    if provider in _XIAOMIMIMO_PROVIDER_NAMES:
        from app.services.xiaomimimo_llm_provider import XiaomiMiMoLLMProvider

        if not settings.openai_api_key:
            raise RuntimeError(
                f"LLM_PROVIDER={provider!r} needs OPENAI_API_KEY (set it in .env)."
            )
        return XiaomiMiMoLLMProvider(settings)

    raise RuntimeError(
        f"LLM provider {provider!r} is not available. Set LLM_PROVIDER to "
        "fake | xiaomimimo, or DEMO_MODE=true."
    )
