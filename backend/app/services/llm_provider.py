"""LLM provider interface and selection.

External providers sit behind this interface so the demo runs in
``DEMO_MODE=true`` without paid APIs (AGENTS.md §7). Slice 1 ships only the fake
provider; real providers (#5/#6 and later) implement the same interface. In
demo mode, an unimplemented provider name falls back to the fake provider.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import Settings
from app.core.constants import CompanionMode

logger = logging.getLogger(__name__)

_FAKE_PROVIDER_NAMES = {"fake", "mock"}


@dataclass
class CompanionReplyInput:
    """Everything the provider needs to draft a baseline companion reply."""

    message: str
    mode: CompanionMode
    companion_display_name: str


class LLMProvider(ABC):
    """Minimal provider contract for Slice 1.

    The companion persona will move into ``CompanionAgent`` (#6); for now the
    provider returns a safe, warm baseline reply.
    """

    name: str = "base"

    @abstractmethod
    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        """Return a companion reply. Must never produce medical/dosage advice."""


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Select a provider from settings, with a demo-mode fallback to fake."""
    # Imported here to avoid a circular import at module load.
    from app.services.fake_llm_provider import FakeLLMProvider

    provider = (settings.llm_provider or "").strip().lower()
    if provider in _FAKE_PROVIDER_NAMES:
        return FakeLLMProvider()

    if settings.demo_mode:
        logger.warning(
            "LLM_PROVIDER=%r is not implemented yet; falling back to the fake "
            "provider because DEMO_MODE=true.",
            provider,
        )
        return FakeLLMProvider()

    raise RuntimeError(
        f"LLM provider {provider!r} is not available. Slice 1 only implements the "
        "fake provider. Set LLM_PROVIDER=fake or DEMO_MODE=true."
    )
