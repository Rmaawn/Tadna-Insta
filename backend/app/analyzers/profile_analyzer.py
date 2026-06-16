"""Profile & branding analyzer.

Evaluates the static identity of an account — username, bio, CTA, niche,
follower economics and overall clarity — and produces a Profile Score plus a
Branding Score. Pure heuristics, no network calls, fully deterministic.
"""

from __future__ import annotations

import re
from typing import Any

from app.analyzers.base import AnalyzerResult, BaseAnalyzer, clamp, ins, scale
from app.schemas.schemas import FetchedProfile

# Niche -> signal keywords (English + common Persian terms).
NICHE_KEYWORDS: dict[str, list[str]] = {
    "Fashion & Apparel": ["fashion", "style", "outfit", "boutique", "clothing", "مد", "پوشاک", "لباس"],
    "Beauty & Skincare": ["beauty", "makeup", "skincare", "cosmetic", "salon", "آرایش", "زیبایی", "پوست"],
    "Fitness & Health": ["fitness", "gym", "workout", "coach", "nutrition", "health", "فیتنس", "تناسب", "سلامت"],
    "Food & Restaurant": ["food", "recipe", "restaurant", "cafe", "kitchen", "chef", "غذا", "رستوران", "کافه", "آشپزی"],
    "Travel": ["travel", "wanderlust", "trip", "tour", "explore", "سفر", "گردشگری", "تور"],
    "Tech & SaaS": ["tech", "software", "ai", "startup", "developer", "saas", "app", "فناوری", "نرم‌افزار", "استارتاپ"],
    "Education & Coaching": ["education", "course", "learn", "mentor", "academy", "coaching", "آموزش", "دوره", "مدرس"],
    "Real Estate": ["realestate", "property", "home", "realtor", "املاک", "مسکن", "خانه"],
    "Photography & Art": ["photography", "photographer", "art", "artist", "design", "عکاسی", "هنر", "طراحی"],
    "E-commerce & Shop": ["shop", "store", "online", "ecommerce", "delivery", "فروشگاه", "خرید", "آنلاین"],
}

CTA_KEYWORDS = [
    "dm", "link in bio", "shop now", "order", "buy", "book", "sign up", "subscribe",
    "click", "whatsapp", "contact", "call", "join", "download", "register", "خرید",
    "سفارش", "دایرکت", "تماس", "لینک", "ثبت‌نام", "ثبت نام", "رزرو", "مشاوره",
]

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
)


class ProfileAnalyzer(BaseAnalyzer):
    key = "profile"
    title = "Profile & Branding"

    def analyze(
        self, profile: FetchedProfile, context: dict[str, Any]
    ) -> AnalyzerResult:
        bio = (profile.biography or "").strip()
        bio_lower = bio.lower()

        username_score = self._username_quality(profile.username)
        bio_score = self._bio_quality(bio)
        has_cta = self._has_cta(bio_lower, profile.external_url)
        cta_score = 100.0 if has_cta else 25.0
        niche, niche_conf = self._detect_niche(bio_lower, profile.full_name or "")
        ratio_score, ratio = self._ratio_quality(profile.followers, profile.following)
        clarity_score = self._clarity(profile)

        profile_score = clamp(
            0.22 * username_score
            + 0.30 * bio_score
            + 0.18 * cta_score
            + 0.15 * clarity_score
            + 0.15 * ratio_score
        )

        # Branding leans on identity clarity, niche confidence and bio strength.
        brand_score = clamp(
            0.35 * clarity_score
            + 0.25 * bio_score
            + 0.25 * (niche_conf * 100.0)
            + 0.15 * (100.0 if profile.full_name else 30.0)
        )

        insights: list[dict] = []
        if not has_cta:
            insights.append(ins("profile.no_cta", "Bio has no clear call-to-action — visitors don't know what to do next."))
        if not profile.external_url:
            insights.append(ins("profile.no_link", "No link in bio: you're leaving conversions on the table."))
        if len(bio) < 30:
            insights.append(ins("profile.bio_short", "Bio is too short to communicate your value proposition."))
        if niche_conf < 0.4:
            insights.append(ins("profile.niche_unclear", "Your niche is unclear from the bio — positioning feels generic."))
        if ratio < 1 and profile.following > 1500:
            insights.append(ins("profile.low_ratio", "Following far more than your followers signals low authority."))
        if not insights:
            insights.append(ins("profile.solid", "Profile fundamentals are solid; focus on content and consistency next.", tone="good"))

        # Expose branding so the orchestrator can surface it as a headline score.
        context["brand_score"] = brand_score
        context["niche"] = niche

        return AnalyzerResult(
            key=self.key,
            title=self.title,
            score=profile_score,
            metrics={
                "brand_score": round(brand_score, 1),
                "followers": profile.followers,
                "following": profile.following,
                "posts_count": profile.posts_count,
                "follower_ratio": round(ratio, 2),
                "has_cta": has_cta,
                "has_link": bool(profile.external_url),
                "is_business": profile.is_business,
                "is_verified": profile.is_verified,
                "niche": niche,
                "niche_confidence": round(niche_conf, 2),
            },
            insights=insights,
            details={
                "scores": {
                    "username": round(username_score, 1),
                    "bio": round(bio_score, 1),
                    "cta": round(cta_score, 1),
                    "clarity": round(clarity_score, 1),
                    "ratio": round(ratio_score, 1),
                },
                "bio_length": len(bio),
                "bio_has_emoji": bool(EMOJI_RE.search(bio)),
            },
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def _username_quality(username: str) -> float:
        u = username or ""
        score = 100.0
        digits = sum(c.isdigit() for c in u)
        if digits >= 4:
            score -= 35
        elif digits >= 2:
            score -= 15
        underscores = u.count("_") + u.count(".")
        if underscores >= 3:
            score -= 25
        elif underscores == 2:
            score -= 10
        if len(u) > 22:
            score -= 15
        if len(u) < 3:
            score -= 20
        return clamp(score)

    def _bio_quality(self, bio: str) -> float:
        if not bio:
            return 10.0
        score = 0.0
        length = len(bio)
        score += scale(min(length, 150), 0, 150) * 0.5  # up to 50
        if EMOJI_RE.search(bio):
            score += 12
        if "\n" in bio:  # structured, multi-line bios read better
            score += 12
        if self._has_cta(bio.lower(), None):
            score += 14
        if any(ch.isdigit() for ch in bio):  # concrete proof / numbers
            score += 6
        if length > 600:  # bios are capped at 150 chars; long => odd
            score -= 10
        return clamp(score, 10, 100)

    @staticmethod
    def _has_cta(bio_lower: str, external_url: str | None) -> bool:
        if external_url:
            return True
        return any(kw in bio_lower for kw in CTA_KEYWORDS)

    @staticmethod
    def _detect_niche(bio_lower: str, full_name: str) -> tuple[str, float]:
        haystack = f"{bio_lower} {full_name.lower()}"
        best_niche, best_hits = "General / Lifestyle", 0
        for niche, kws in NICHE_KEYWORDS.items():
            hits = sum(1 for kw in kws if kw in haystack)
            if hits > best_hits:
                best_niche, best_hits = niche, hits
        confidence = clamp(best_hits * 40, 0, 100) / 100.0
        return best_niche, confidence

    @staticmethod
    def _ratio_quality(followers: int, following: int) -> tuple[float, float]:
        ratio = followers / following if following else float(followers or 0)
        # A healthy ratio is >= ~1.5; saturates well above that.
        score = scale(min(ratio, 5.0), 0.3, 3.0)
        return score, ratio

    @staticmethod
    def _clarity(profile: FetchedProfile) -> float:
        score = 0.0
        if profile.full_name:
            score += 30
        if profile.profile_pic_url:
            score += 20
        if profile.biography and len(profile.biography) >= 30:
            score += 25
        if profile.category or profile.is_business:
            score += 15
        if profile.external_url:
            score += 10
        return clamp(score)
