"""CompanionAgent — relationship-first, user-named persona (issue #6).

Responsibilities (and only these): pick the mode prompt, read the
``companion_display_name`` (from the profile, passed in) into that prompt, and
produce a reply via the LLM provider. It does **not** own onboarding, renaming,
or profile CRUD (that is #21), and it does not route or run safety (#5/#8).

In ``DEMO_MODE`` the provider is the fake one, so the reply text is a
deterministic role-first / neutral template; the rendered persona prompt (with
the name filled in) is still produced and surfaced in the trace, which is what a
real LLM would consume.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.constants import DEFAULT_COMPANION_DISPLAY_NAME, CompanionMode
from app.services.llm_provider import CompanionReplyInput, LLMProvider

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
_PROMPT_FILES = {
    CompanionMode.role_first: "companion_role_first.md",
    CompanionMode.neutral_assistant: "companion_neutral_assistant.md",
}
_PROMPT_VERSION = "v1"
_NAME_PLACEHOLDER = "{companion_display_name}"


@lru_cache(maxsize=None)
def _load_prompt_template(mode: CompanionMode) -> str:
    return (_PROMPT_DIR / _PROMPT_FILES[mode]).read_text(encoding="utf-8")


@dataclass
class CompanionResult:
    reply_text: str
    mode: CompanionMode
    companion_display_name: str
    named_by_user: bool
    rendered_prompt: str

    def trace_summary(self) -> str:
        source = "用户命名" if self.named_by_user else "默认称呼"
        style = "情绪承接优先" if self.mode == CompanionMode.role_first else "中性助理对照"
        return f"{style}；称呼「{self.companion_display_name}」（{source}）"


class CompanionAgent:
    name = "CompanionAgent"

    def __init__(self, llm_provider: LLMProvider):
        self._llm = llm_provider

    def respond(
        self,
        *,
        message: str,
        mode: CompanionMode,
        companion_display_name: str | None,
    ) -> CompanionResult:
        named_by_user = bool(companion_display_name and companion_display_name.strip())
        display_name = (
            companion_display_name.strip()
            if named_by_user
            else DEFAULT_COMPANION_DISPLAY_NAME
        )

        rendered_prompt = _load_prompt_template(mode).replace(
            _NAME_PLACEHOLDER, display_name
        )

        reply_text = self._llm.generate_companion_reply(
            CompanionReplyInput(
                message=message,
                mode=mode,
                companion_display_name=display_name,
                system_prompt=rendered_prompt,
            )
        )

        return CompanionResult(
            reply_text=reply_text,
            mode=mode,
            companion_display_name=display_name,
            named_by_user=named_by_user,
            rendered_prompt=rendered_prompt,
        )

    @property
    def prompt_version(self) -> str:
        return _PROMPT_VERSION
