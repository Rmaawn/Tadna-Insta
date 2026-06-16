"""AI recommendation engine.

Turns the deterministic analyzer output into a strategic narrative: an
executive summary, strengths, weaknesses and a prioritized set of growth
recommendations. Runs through the :class:`LLMProvider` abstraction so it is not
coupled to any single vendor.

The prompt is engineered to make the model sound like a senior Instagram growth
strategist — concise, analytical, business-focused — and to return strict JSON.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.base import LLMError, LLMProvider
from app.schemas.schemas import FetchedProfile

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "fa": "Persian (فارسی)",
    "ar": "Arabic (العربية)",
    "en": "English",
}

SYSTEM_PROMPT = """You are a senior Instagram growth strategist who has scaled \
dozens of brand and creator accounts. You think in terms of positioning, \
content systems, audience psychology and conversion. Your advice is concise, \
analytical, specific and premium — never generic motivational filler, never \
robotic. You speak the language of a high-end growth consultant.

Write ALL natural-language values (summary, strengths, weaknesses, every \
recommendation title/impact/detail) in {language}. Keep the JSON keys and the \
``category``/``priority`` enum values in English exactly as specified.

You will be given a structured analysis of one Instagram account. Respond with \
a single JSON object, no prose outside it, matching exactly this shape:

{
  "summary": "2-3 sentence executive summary of the account's growth situation",
  "strengths": ["3-5 concrete strengths"],
  "weaknesses": ["3-5 concrete weaknesses / risks"],
  "recommendations": [
    {
      "title": "short imperative title",
      "category": "Profile|Content|Engagement|Visual|Strategy",
      "priority": "high|medium|low",
      "impact": "one line on the expected growth impact",
      "detail": "1-2 sentences of specific, actionable guidance"
    }
  ]
}

Return 5-7 recommendations, ordered by priority (high first). Ground every \
point in the data you are given. Do not invent metrics."""


class RecommendationEngine:
    """Generates the AI growth report. Requires a working LLM provider."""

    key = "recommendations"
    title = "AI Growth Recommendations"

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @property
    def available(self) -> bool:
        return self.provider.available

    async def generate(
        self,
        profile: FetchedProfile,
        scores: dict[str, float | None],
        report: dict[str, Any],
        language: str = "fa",
    ) -> dict[str, Any]:
        if not self.available:
            raise LLMError("AI recommendations require a configured OpenAI API key.")

        language_name = LANGUAGE_NAMES.get(language, LANGUAGE_NAMES["en"])
        # Use replace (not str.format) because the prompt contains a literal JSON
        # example with `{`/`}` braces that str.format would mis-parse as fields.
        system = SYSTEM_PROMPT.replace("{language}", language_name)
        user_payload = self._build_payload(profile, scores, report)
        data = await self.provider.generate_json(
            system,
            json.dumps(user_payload, ensure_ascii=False),
            temperature=0.5,
        )
        return self._normalize(data)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_payload(
        profile: FetchedProfile,
        scores: dict[str, float | None],
        report: dict[str, Any],
    ) -> dict[str, Any]:
        """Compact, token-efficient view of the analysis for the model."""
        sections = {
            name: {
                "score": section.get("score"),
                "metrics": section.get("metrics", {}),
                # Insights are {code, text, params}; the model only needs the text.
                "insights": [
                    i.get("text") if isinstance(i, dict) else i
                    for i in section.get("insights", [])
                ],
            }
            for name, section in report.items()
        }
        return {
            "account": {
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "followers": profile.followers,
                "following": profile.following,
                "posts_count": profile.posts_count,
                "is_business": profile.is_business,
                "external_url": profile.external_url,
            },
            "scores": scores,
            "analysis": sections,
        }

    @staticmethod
    def _normalize(data: dict[str, Any]) -> dict[str, Any]:
        recs = []
        for r in data.get("recommendations", []) or []:
            if not isinstance(r, dict):
                continue
            recs.append(
                {
                    "title": str(r.get("title", "")).strip(),
                    "category": str(r.get("category", "Strategy")).strip(),
                    "priority": str(r.get("priority", "medium")).lower().strip(),
                    "impact": str(r.get("impact", "")).strip(),
                    "detail": str(r.get("detail", "")).strip(),
                }
            )
        order = {"high": 0, "medium": 1, "low": 2}
        recs.sort(key=lambda r: order.get(r["priority"], 1))
        return {
            "summary": str(data.get("summary", "")).strip(),
            "strengths": [str(s).strip() for s in data.get("strengths", []) or []],
            "weaknesses": [str(w).strip() for w in data.get("weaknesses", []) or []],
            "recommendations": recs,
        }
