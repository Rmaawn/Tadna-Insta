"""OpenAI implementation of :class:`LLMProvider`.

Uses the official async OpenAI SDK with JSON-mode responses so the model is
forced to return a parseable object.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.base import LLMError, LLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        self._client = None
        self._model = settings.openai_model

    @property
    def available(self) -> bool:
        return bool(settings.openai_api_key)

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def generate_json(
        self, system: str, user: str, *, temperature: float = 0.4
    ) -> dict[str, Any]:
        if not self.available:
            raise LLMError("OPENAI_API_KEY is not configured.")

        client = self._get_client()
        try:
            resp = await client.chat.completions.create(
                model=self._model,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("OpenAI request failed: %s", exc)
            raise LLMError(f"OpenAI request failed: {exc}") from exc

        content = resp.choices[0].message.content or "{}"
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError("Model returned invalid JSON.") from exc
