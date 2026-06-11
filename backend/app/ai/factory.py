"""Provider selection.

A single switch chooses the active LLM provider. Extend ``_PROVIDERS`` to make
new backends selectable via configuration.
"""

from __future__ import annotations

from functools import lru_cache

from app.ai.base import LLMProvider
from app.ai.openai_provider import OpenAIProvider

_PROVIDERS = {
    "openai": OpenAIProvider,
}


@lru_cache
def get_provider(name: str = "openai") -> LLMProvider:
    provider_cls = _PROVIDERS.get(name, OpenAIProvider)
    return provider_cls()
