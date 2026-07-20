"""Small deterministic similarity helper for memory triage (#81).

This is intentionally simple: normalized text equality / containment is enough
for Stage 1 and keeps tests offline. It can later be replaced by an embedding
provider behind the same interface.
"""

from __future__ import annotations

import re

_PUNCT_OR_SPACE = re.compile(r"[\s，。、,.!！?？；;：:（）()\[\]【】\"'“”‘’]+")
_LOW_VALUE_CHARS = ("听", "看", "聊", "的", "这件事", "这个事", "事情")

_CONTAINMENT_MIN_RATIO = 0.8


class MemorySimilarityService:
    def normalize(self, text: str) -> str:
        normalized = _PUNCT_OR_SPACE.sub("", text or "")
        for token in _LOW_VALUE_CHARS:
            normalized = normalized.replace(token, "")
        return normalized

    def is_duplicate(self, left: str, right: str) -> bool:
        a = self.normalize(left)
        b = self.normalize(right)
        return bool(a) and a == b

    def is_similar(self, left: str, right: str) -> bool:
        a = self.normalize(left)
        b = self.normalize(right)
        if not a or not b:
            return False
        if a == b:
            return True
        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
        return (
            shorter in longer
            and len(shorter) / len(longer) >= _CONTAINMENT_MIN_RATIO
        )
