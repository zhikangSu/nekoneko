"""Small deterministic similarity helper for memory triage (#81).

This is intentionally simple: normalized text equality / containment is enough
for Stage 1 and keeps tests offline. It can later be replaced by an embedding
provider behind the same interface.
"""

from __future__ import annotations

import re

_PUNCT_OR_SPACE = re.compile(r"[\s，。、,.!！?？；;：:（）()\[\]【】\"'“”‘’]+")
_LOW_VALUE_CHARS = ("听", "看", "聊", "的", "这件事", "这个事", "事情")


class MemorySimilarityService:
    def normalize(self, text: str) -> str:
        normalized = _PUNCT_OR_SPACE.sub("", text or "")
        for token in _LOW_VALUE_CHARS:
            normalized = normalized.replace(token, "")
        return normalized

    def is_similar(self, left: str, right: str) -> bool:
        a = self.normalize(left)
        b = self.normalize(right)
        if not a or not b:
            return False
        return a == b or a in b or b in a
