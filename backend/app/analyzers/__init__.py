"""Modular analyzers.

Every analyzer is an isolated unit implementing :class:`BaseAnalyzer`. The
orchestration service runs them in sequence, feeding each one a shared mutable
``context`` so later analyzers (e.g. the recommendation engine) can build on the
output of earlier ones. New analyzers can be added without modifying existing
code — just register them in :data:`ANALYZER_PIPELINE`.
"""

from app.analyzers.base import AnalyzerResult, BaseAnalyzer
from app.analyzers.content_analyzer import ContentAnalyzer
from app.analyzers.engagement_analyzer import EngagementAnalyzer
from app.analyzers.profile_analyzer import ProfileAnalyzer
from app.analyzers.visual_analyzer import VisualAnalyzer

# Order matters: each analyzer can read what previous ones wrote to ``context``.
ANALYZER_PIPELINE: list[type[BaseAnalyzer]] = [
    ProfileAnalyzer,
    ContentAnalyzer,
    EngagementAnalyzer,
    VisualAnalyzer,
]

__all__ = [
    "ANALYZER_PIPELINE",
    "AnalyzerResult",
    "BaseAnalyzer",
    "ContentAnalyzer",
    "EngagementAnalyzer",
    "ProfileAnalyzer",
    "VisualAnalyzer",
]
