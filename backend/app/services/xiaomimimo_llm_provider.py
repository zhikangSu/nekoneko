"""Real companion-reply LLM via the xiaomimimo OpenAI-compatible API (#6 real).

Implements the same ``LLMProvider`` contract as the fake provider, so it is
selected only with ``DEMO_MODE=false`` + ``LLM_PROVIDER=xiaomimimo`` + a key;
``DEMO_MODE`` always stays on the fake provider (offline demo needs no key).

It uses the persona ``system_prompt`` that ``CompanionAgent`` renders (persona +
the user's name + memory/retrieval blocks already delimited and labeled as
untrusted reference data, so the model rewrites them rather than obeying them).
On any API failure it falls back to the fake reply so a turn never breaks — and
either way the reply still passes ``OutputRuleGuard``. The key is read from the
gitignored ``.env`` and never logged.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.core.config import Settings
from app.services.llm_provider import CompanionReplyInput, LLMProvider

logger = logging.getLogger(__name__)

_RETRY_ON = {429, 500, 502, 503, 504}


class XiaomiMiMoLLMProvider(LLMProvider):
    name = "xiaomimimo"

    def __init__(self, settings: Settings) -> None:
        self._url = settings.openai_base_url.rstrip("/") + "/chat/completions"
        self._key = settings.openai_api_key
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._timeout = settings.llm_timeout_seconds
        self._generation_info: dict[str, Any] = {
            "provider": self.name,
            "model": self._model,
            "used_fallback": False,
        }

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        messages: list[dict[str, str]] = []
        if payload.system_prompt:
            messages.append({"role": "system", "content": payload.system_prompt})
        for history_message in payload.conversation_history:
            messages.append(
                {
                    "role": history_message.role,
                    "content": history_message.content,
                }
            )
        messages.append({"role": "user", "content": payload.message})
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        try:
            data = self._post(body)
            text = (data["choices"][0]["message"].get("content") or "").strip()
            if not text:
                raise ValueError("empty reply from provider")
            self._generation_info = {
                "provider": self.name,
                "model": self._model,
                "used_fallback": False,
            }
            return text
        except Exception as exc:
            # Never break a turn on a live-API hiccup — fall back to the safe,
            # deterministic reply (still passes OutputRuleGuard downstream).
            logger.warning(
                "LLM provider %r failed; falling back to the fake reply.", self.name
            )
            from app.services.fake_llm_provider import FakeLLMProvider

            self._generation_info = {
                "provider": self.name,
                "model": self._model,
                "used_fallback": True,
                "fallback_provider": "fake",
                "error_type": type(exc).__name__,
            }
            return FakeLLMProvider().generate_companion_reply(payload)

    @property
    def generation_info(self) -> dict[str, Any]:
        return dict(self._generation_info)

    def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }
        for attempt in range(2):
            response = httpx.post(
                self._url, headers=headers, json=body, timeout=self._timeout
            )
            if response.status_code in _RETRY_ON and attempt == 0:
                logger.warning("LLM API %s; retrying once.", response.status_code)
                time.sleep(1.0)
                continue
            response.raise_for_status()
            return response.json()
        response.raise_for_status()
        return response.json()
