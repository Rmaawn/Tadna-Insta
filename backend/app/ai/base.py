"""LLM provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMError(Exception):
    """Raised when the language model call fails."""


class LLMProvider(ABC):
    """Vendor-agnostic interface for structured LLM generation."""

    name: str = "base"

    @property
    @abstractmethod
    def available(self) -> bool:
        """Whether the provider is configured and ready to use."""

    @abstractmethod
    async def generate_json(
        self, system: str, user: str, *, temperature: float = 0.4
    ) -> dict[str, Any]:
        """Return a parsed JSON object from the model, or raise LLMError."""
        raise NotImplementedError
