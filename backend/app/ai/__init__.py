"""LLM provider abstraction.

The platform talks to language models through :class:`LLMProvider`, never to a
vendor SDK directly. Today the only implementation is OpenAI; adding Anthropic,
a local model, etc. later is a matter of dropping in a new provider class.
"""

from app.ai.base import LLMError, LLMProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.factory import get_provider

__all__ = ["LLMError", "LLMProvider", "OpenAIProvider", "get_provider"]
