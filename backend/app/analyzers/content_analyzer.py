"""Content analyzer.

Looks across the recent posts to characterize *what* and *when* the account
publishes: caption quality, content-type mix (image / carousel / reel),
posting cadence/consistency and a posting-time heatmap.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Any

from app.analyzers.base import AnalyzerResult, BaseAnalyzer, clamp, ins, scale
from app.analyzers.profile_analyzer import CTA_KEYWORDS, EMOJI_RE
from app.schemas.schemas import FetchedProfile

HASHTAG_RE = re.compile(r"#\w+")
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class ContentAnalyzer(BaseAnalyzer):
    key = "content"
    title = "Content Analytics"

    def analyze(
        self, profile: FetchedProfile, context: dict[str, Any]
    ) -> AnalyzerResult:
        posts = profile.posts
        if not posts:
            return AnalyzerResult(
                key=self.key,
                title=self.title,
                score=0.0,
                insights=["No public posts were available to analyze."],
            )

        caption_score, caption_stats = self._caption_quality(posts)
        distribution = self._type_distribution(posts)
        cadence_score, cadence = self._cadence(posts)
        heatmap, best_slot = self._heatmap(posts)

        content_score = clamp(0.55 * caption_score + 0.45 * cadence_score)
        context["content_score"] = content_score
        context["posting_cadence_days"] = cadence.get("avg_gap_days")

        total = len(posts)
        reels = distribution.get("video", 0)
        carousels = distribution.get("carousel", 0)
        images = distribution.get("image", 0)

        insights: list[dict] = []
        if caption_stats["avg_length"] < 80:
            insights.append(ins("content.captions_short", "Captions are short — you're underusing them as a storytelling and SEO surface."))
        if caption_stats["cta_ratio"] < 0.3:
            insights.append(ins("content.low_cta", "Fewer than a third of posts include a call-to-action."))
        if carousels == 0 and total >= 6:
            insights.append(ins("content.no_carousels", "No carousels in recent posts — carousels typically drive higher reach and saves."))
        if cadence.get("avg_gap_days") and cadence["avg_gap_days"] > 4:
            insights.append(ins("content.slow_cadence", "Posting cadence is slow; the algorithm rewards consistency."))
        if cadence.get("consistency_label") == "irregular":
            insights.append(ins("content.irregular", "Posting schedule is irregular — gaps between posts vary widely."))
        if best_slot:
            insights.append(ins("content.best_window", f"Your strongest publishing window is {best_slot}.", slot=best_slot))
        if not insights:
            insights.append(ins("content.healthy", "Content mix and cadence look healthy — keep the momentum."))

        return AnalyzerResult(
            key=self.key,
            title=self.title,
            score=content_score,
            metrics={
                "total_analyzed": total,
                "images": images,
                "carousels": carousels,
                "reels": reels,
                "avg_caption_length": round(caption_stats["avg_length"], 1),
                "caption_cta_ratio": round(caption_stats["cta_ratio"], 2),
                "avg_hashtags": round(caption_stats["avg_hashtags"], 1),
                "avg_gap_days": cadence.get("avg_gap_days"),
                "consistency": cadence.get("consistency_label"),
                "best_slot": best_slot,
            },
            insights=insights,
            details={
                "type_distribution": distribution,
                "caption_stats": caption_stats,
                "cadence": cadence,
                "heatmap": heatmap,  # 7x24 matrix of post counts
                "weekdays": WEEKDAYS,
            },
        )

    # ------------------------------------------------------------------ #
    def _caption_quality(self, posts) -> tuple[float, dict[str, float]]:
        lengths, hashtags, cta_hits, emoji_hits, question_hits = [], [], 0, 0, 0
        for p in posts:
            cap = (p.caption or "").strip()
            lengths.append(len(cap))
            hashtags.append(len(HASHTAG_RE.findall(cap)))
            low = cap.lower()
            if any(kw in low for kw in CTA_KEYWORDS):
                cta_hits += 1
            if EMOJI_RE.search(cap):
                emoji_hits += 1
            if "?" in cap or "؟" in cap:
                question_hits += 1

        n = len(posts)
        avg_length = statistics.mean(lengths) if lengths else 0
        avg_hashtags = statistics.mean(hashtags) if hashtags else 0
        cta_ratio = cta_hits / n
        emoji_ratio = emoji_hits / n
        question_ratio = question_hits / n

        score = clamp(
            0.40 * scale(min(avg_length, 220), 20, 220)
            + 0.25 * (cta_ratio * 100)
            + 0.15 * (emoji_ratio * 100)
            + 0.10 * (question_ratio * 100)
            + 0.10 * scale(min(avg_hashtags, 12), 1, 12)
        )
        return score, {
            "avg_length": avg_length,
            "avg_hashtags": avg_hashtags,
            "cta_ratio": cta_ratio,
            "emoji_ratio": emoji_ratio,
            "question_ratio": question_ratio,
        }

    @staticmethod
    def _type_distribution(posts) -> dict[str, int]:
        counter = Counter(p.media_type for p in posts)
        return {"image": counter.get("image", 0), "carousel": counter.get("carousel", 0), "video": counter.get("video", 0)}

    @staticmethod
    def _cadence(posts) -> tuple[float, dict[str, Any]]:
        dates = sorted([p.posted_at for p in posts if p.posted_at])
        if len(dates) < 2:
            return 50.0, {"avg_gap_days": None, "consistency_label": "unknown"}

        gaps = [
            (dates[i] - dates[i - 1]).total_seconds() / 86400.0
            for i in range(1, len(dates))
        ]
        avg_gap = statistics.mean(gaps)
        stdev = statistics.pstdev(gaps) if len(gaps) > 1 else 0.0
        cv = stdev / avg_gap if avg_gap else 1.0

        # Reward frequent (low gap) and regular (low variation) posting.
        frequency_score = scale(7 - min(avg_gap, 7), 0, 6)  # daily -> high
        regularity_score = clamp(100 - cv * 80)
        score = clamp(0.6 * frequency_score + 0.4 * regularity_score)

        label = "consistent" if cv < 0.5 else "moderate" if cv < 1.0 else "irregular"
        return score, {
            "avg_gap_days": round(avg_gap, 2),
            "stdev_days": round(stdev, 2),
            "cv": round(cv, 2),
            "consistency_label": label,
            "posts_per_week": round(7 / avg_gap, 2) if avg_gap else None,
        }

    @staticmethod
    def _heatmap(posts) -> tuple[list[list[int]], str | None]:
        matrix = [[0] * 24 for _ in range(7)]
        slot_counter: Counter = Counter()
        for p in posts:
            if not p.posted_at:
                continue
            wd = p.posted_at.weekday()
            hr = p.posted_at.hour
            matrix[wd][hr] += 1
            slot_counter[(wd, hr)] += 1

        best_slot = None
        if slot_counter:
            (wd, hr), _ = slot_counter.most_common(1)[0]
            best_slot = f"{WEEKDAYS[wd]} ~{hr:02d}:00"
        return matrix, best_slot
