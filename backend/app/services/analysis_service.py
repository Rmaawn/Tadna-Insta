"""Analysis orchestration.

Runs the full pipeline for one account:

    fetch -> deterministic analyzers -> headline scores -> AI report -> persist

It owns its own DB session (it runs inside a background task), updates the
``Analysis`` row's status as it progresses, and degrades gracefully: if the AI
layer is unavailable the deterministic report is still saved in full.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.ai import get_provider
from app.ai.base import LLMError
from app.analyzers import ANALYZER_PIPELINE
from app.analyzers.base import clamp
from app.analyzers.recommendation_engine import RecommendationEngine
from app.config import settings
from app.database import SessionLocal
from app.fetchers import FetchError, InstagramFetcher
from app.models import Analysis, AnalysisStatus, InstagramAccount, Post
from app.schemas.schemas import FetchedProfile

logger = logging.getLogger(__name__)

# Contribution of each sub-score to the overall Growth Score.
GROWTH_WEIGHTS = {
    "engagement": 0.30,
    "content": 0.25,
    "profile": 0.20,
    "visual": 0.15,
    "brand": 0.10,
}


class AnalysisService:
    def __init__(self) -> None:
        self.fetcher = InstagramFetcher()

    async def run(self, analysis_id: str) -> None:
        """Execute the pipeline for an existing (pending) analysis row."""
        async with SessionLocal() as session:
            analysis = await session.get(Analysis, analysis_id)
            if analysis is None:
                logger.error("Analysis %s vanished before it could run", analysis_id)
                return

            analysis.status = AnalysisStatus.RUNNING
            await session.commit()

            try:
                profile = await self.fetcher.fetch(
                    analysis.username, settings.ig_post_limit
                )
                await self._process(session, analysis, profile)
                analysis.status = AnalysisStatus.COMPLETED
            except FetchError as exc:
                analysis.status = AnalysisStatus.FAILED
                analysis.error = str(exc)
                logger.warning("Fetch failed for %s: %s", analysis.username, exc)
            except Exception as exc:  # noqa: BLE001
                analysis.status = AnalysisStatus.FAILED
                analysis.error = f"Unexpected error: {exc}"
                logger.exception("Analysis %s crashed", analysis_id)

            analysis.completed_at = datetime.now(timezone.utc)
            await session.commit()

    # ------------------------------------------------------------------ #
    async def _process(
        self, session, analysis: Analysis, profile: FetchedProfile
    ) -> None:
        # 1) Persist / refresh the account snapshot.
        account = await self._upsert_account(session, profile)
        analysis.account_id = account.id

        # 2) Run the deterministic analyzer pipeline.
        context: dict[str, Any] = {}
        report: dict[str, Any] = {}
        for analyzer_cls in ANALYZER_PIPELINE:
            result = analyzer_cls().analyze(profile, context)
            report[result.key] = result.to_dict()

        # Display-only account header (avatar, name) for the dashboard.
        report["account"] = {
            "username": profile.username,
            "full_name": profile.full_name,
            "profile_pic_url": profile.profile_pic_url,
        }

        # 3) Headline scores.
        scores = {
            "profile": report.get("profile", {}).get("score"),
            "brand": context.get("brand_score"),
            "content": report.get("content", {}).get("score"),
            "engagement": report.get("engagement", {}).get("score"),
            "visual": report.get("visual", {}).get("score"),
        }
        analysis.profile_score = scores["profile"]
        analysis.brand_score = scores["brand"]
        analysis.engagement_score = scores["engagement"]
        analysis.visual_score = scores["visual"]
        analysis.growth_score = self._growth_score(scores)
        scores["growth"] = analysis.growth_score

        # 4) AI growth report (optional — requires OpenAI key).
        report["ai"] = await self._ai_report(profile, scores, report, analysis)

        # 5) Persist posts with their per-post signals.
        await self._save_posts(session, analysis, profile, context)

        analysis.report = report

    async def _upsert_account(
        self, session, profile: FetchedProfile
    ) -> InstagramAccount:
        existing = (
            await session.execute(
                select(InstagramAccount).where(
                    InstagramAccount.username == profile.username
                )
            )
        ).scalar_one_or_none()

        account = existing or InstagramAccount(username=profile.username)
        account.full_name = profile.full_name
        account.biography = profile.biography
        account.external_url = profile.external_url
        account.profile_pic_url = profile.profile_pic_url
        account.followers = profile.followers
        account.following = profile.following
        account.posts_count = profile.posts_count
        account.is_business = profile.is_business
        account.is_verified = profile.is_verified
        account.is_private = profile.is_private
        account.category = profile.category
        if existing is None:
            session.add(account)
        await session.flush()
        return account

    async def _save_posts(
        self, session, analysis: Analysis, profile: FetchedProfile, context: dict
    ) -> None:
        signals = context.get("post_signals", {})
        for p in profile.posts:
            sig = signals.get(p.shortcode, {})
            session.add(
                Post(
                    analysis_id=analysis.id,
                    shortcode=p.shortcode,
                    caption=p.caption,
                    media_type=p.media_type,
                    thumbnail_url=p.thumbnail_url,
                    permalink=p.permalink,
                    likes=p.likes,
                    comments=p.comments,
                    video_views=p.video_views,
                    engagement_rate=sig.get("engagement_rate", 0.0),
                    posted_at=p.posted_at,
                    signals=sig,
                )
            )

    async def _ai_report(
        self,
        profile: FetchedProfile,
        scores: dict,
        report: dict,
        analysis: Analysis,
    ) -> dict[str, Any]:
        engine = RecommendationEngine(get_provider("openai"))
        if not engine.available:
            note = (
                "AI recommendations are disabled. Add a valid OPENAI_API_KEY to "
                "the backend .env to unlock the AI growth strategist."
            )
            analysis.ai_summary = note
            return {"available": False, "note": note}

        try:
            ai = await engine.generate(profile, scores, report, analysis.language)
        except LLMError as exc:
            note = f"AI generation failed: {exc}"
            analysis.ai_summary = note
            logger.warning(note)
            return {"available": False, "note": note}

        analysis.ai_summary = ai["summary"]
        analysis.strengths = ai["strengths"]
        analysis.weaknesses = ai["weaknesses"]
        analysis.recommendations = ai["recommendations"]
        return {"available": True, **ai}

    @staticmethod
    def _growth_score(scores: dict[str, float | None]) -> float:
        total_weight = 0.0
        acc = 0.0
        for key, weight in GROWTH_WEIGHTS.items():
            value = scores.get(key)
            if value is not None:
                acc += value * weight
                total_weight += weight
        return round(clamp(acc / total_weight) if total_weight else 0.0, 1)
