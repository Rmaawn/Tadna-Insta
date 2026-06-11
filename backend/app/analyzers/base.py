"""Analyzer contract and shared helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.schemas.schemas import FetchedProfile


def ins(code: str, text: str, **params: Any) -> dict[str, Any]:
    """Build a translatable insight.

    Insights are emitted as ``{code, text, params}`` so the frontend can render
    them in any language (Persian / Arabic / English) from ``code`` + ``params``,
    while ``text`` is the English fallback that also feeds the AI prompt.
    """
    return {"code": code, "text": text, "params": params or {}}


@dataclass
class AnalyzerResult:
    """Structured output of a single analyzer.

    * ``key``      — stable identifier used as the report section name.
    * ``title``    — human-friendly section title for the dashboard.
    * ``score``    — optional headline score in the range 0-100.
    * ``metrics``  — flat numeric/string facts for cards and charts.
    * ``insights`` — list of translatable insights (see :func:`ins`).
    * ``details``  — any richer nested data (palettes, distributions, ...).
    """

    key: str
    title: str
    score: float | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    insights: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "score": round(self.score, 1) if self.score is not None else None,
            "metrics": self.metrics,
            "insights": self.insights,
            "details": self.details,
        }


class BaseAnalyzer(ABC):
    """Every analyzer transforms a fetched profile into an AnalyzerResult."""

    key: str = "base"
    title: str = "Base"

    @abstractmethod
    def analyze(
        self, profile: FetchedProfile, context: dict[str, Any]
    ) -> AnalyzerResult:
        """Run analysis. ``context`` is shared and mutable across the pipeline."""
        raise NotImplementedError


# --------------------------------------------------------------------------- #
#  Scoring helpers                                                            #
# --------------------------------------------------------------------------- #
def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def scale(value: float, lo: float, hi: float) -> float:
    """Map ``value`` from the range [lo, hi] onto [0, 100], clamped."""
    if hi == lo:
        return 0.0
    return clamp((value - lo) / (hi - lo) * 100.0)
