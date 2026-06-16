"""Engagement analyzer.

Computes per-post engagement rate, the account average, the trend over time,
top/weak performers and an engagement-consistency score. Per-post signals are
written back to ``context['post_signals']`` so they can be persisted on each
:class:`Post` row.
"""

from __future__ import annotations

import statistics
from typing import Any

from app.analyzers.base import AnalyzerResult, BaseAnalyzer, clamp, ins, scale
from app.schemas.schemas import FetchedProfile

# Rough industry engagement-rate benchmarks (% of followers) by audience size.
def _benchmark(followers: int) -> float:
    if followers < 1_000:
        return 8.0
    if followers < 10_000:
        return 4.0
    if followers < 100_000:
        return 2.0
    if followers < 1_000_000:
        return 1.3
    return 0.8


class EngagementAnalyzer(BaseAnalyzer):
    key = "engagement"
    title = "Engagement"

    def analyze(
        self, profile: FetchedProfile, context: dict[str, Any]
    ) -> AnalyzerResult:
        posts = profile.posts
        followers = max(profile.followers, 1)
        signals: dict[str, dict] = context.setdefault("post_signals", {})

        if not posts:
            return AnalyzerResult(
                key=self.key, title=self.title, score=0.0,
                insights=["No posts available to measure engagement."],
            )

        rates: list[float] = []
        enriched = []
        for p in posts:
            er = (p.likes + p.comments) / followers * 100.0
            rates.append(er)
            signals.setdefault(p.shortcode, {})["engagement_rate"] = round(er, 3)
            enriched.append((p, er))

        avg_er = statistics.mean(rates)
        median_er = statistics.median(rates)
        stdev_er = statistics.pstdev(rates) if len(rates) > 1 else 0.0
        benchmark = _benchmark(profile.followers)

        # Score: how the account's ER compares to its size benchmark (cap at 2x).
        engagement_score = scale(min(avg_er / benchmark, 2.0), 0.2, 1.6)
        consistency = clamp(100 - (stdev_er / avg_er * 70) if avg_er else 0)

        ordered = sorted(enriched, key=lambda x: x[1], reverse=True)
        top = [self._post_brief(p, er) for p, er in ordered[:3]]
        weak = [self._post_brief(p, er) for p, er in ordered[-3:][::-1]]

        # Chronological trend (oldest -> newest) for the line chart.
        chrono = sorted(
            [(p, er) for p, er in enriched if p.posted_at],
            key=lambda x: x[0].posted_at,
        )
        trend = [
            {
                "shortcode": p.shortcode,
                "date": p.posted_at.isoformat() if p.posted_at else None,
                "engagement_rate": round(er, 3),
                "likes": p.likes,
                "comments": p.comments,
            }
            for p, er in chrono
        ]
        direction = self._trend_direction([er for _, er in chrono])

        context["engagement_score"] = engagement_score

        insights: list[dict] = []
        ratio = avg_er / benchmark if benchmark else 0
        er_s, bm_s = f"{avg_er:.1f}", f"{benchmark:.1f}"
        if ratio >= 1.2:
            insights.append(ins("engagement.above_benchmark", f"Engagement ({er_s}%) is above the benchmark for your size — your audience is active.", tone="good", er=er_s))
        elif ratio < 0.7:
            insights.append(ins("engagement.below_benchmark", f"Engagement ({er_s}%) is below the {bm_s}% benchmark for your size.", er=er_s, benchmark=bm_s))
        if direction == "declining":
            insights.append(ins("engagement.declining", "Engagement is trending downward across recent posts."))
        elif direction == "rising":
            insights.append(ins("engagement.rising", "Engagement is trending upward — recent content is resonating.", tone="good"))
        if stdev_er > avg_er:
            insights.append(ins("engagement.inconsistent", "Engagement is highly inconsistent — a few posts carry most of the interaction."))
        if not insights:
            insights.append(ins("engagement.steady", "Engagement is steady and in line with expectations for your audience size.", tone="good"))

        return AnalyzerResult(
            key=self.key,
            title=self.title,
            score=engagement_score,
            metrics={
                "avg_engagement_rate": round(avg_er, 3),
                "median_engagement_rate": round(median_er, 3),
                "benchmark_rate": benchmark,
                "consistency": round(consistency, 1),
                "trend_direction": direction,
                "avg_likes": round(statistics.mean([p.likes for p in posts]), 1),
                "avg_comments": round(statistics.mean([p.comments for p in posts]), 1),
            },
            insights=insights,
            details={"top_posts": top, "weak_posts": weak, "trend": trend},
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def _post_brief(post, er: float) -> dict[str, Any]:
        return {
            "shortcode": post.shortcode,
            "permalink": post.permalink,
            "thumbnail_url": post.thumbnail_url,
            "media_type": post.media_type,
            "likes": post.likes,
            "comments": post.comments,
            "engagement_rate": round(er, 3),
            "caption_preview": (post.caption or "")[:120],
        }

    @staticmethod
    def _trend_direction(rates: list[float]) -> str:
        if len(rates) < 4:
            return "flat"
        half = len(rates) // 2
        first = statistics.mean(rates[:half])
        last = statistics.mean(rates[half:])
        if last > first * 1.12:
            return "rising"
        if last < first * 0.88:
            return "declining"
        return "flat"
