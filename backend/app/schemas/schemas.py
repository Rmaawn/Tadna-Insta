"""Pydantic schemas.

Two families live here:

* ``Fetched*`` — the internal domain objects produced by the Instagram fetcher
  and consumed by analyzers. They are the contract between data collection and
  analysis, keeping analyzers independent of instaloader specifics.
* API request/response models used by the FastAPI routes.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --------------------------------------------------------------------------- #
#  Internal domain objects (fetcher -> analyzers)                             #
# --------------------------------------------------------------------------- #
class FetchedPost(BaseModel):
    shortcode: str
    caption: str | None = None
    media_type: str = "image"  # image | video | carousel
    thumbnail_url: str | None = None
    permalink: str | None = None
    likes: int = 0
    comments: int = 0
    video_views: int = 0
    posted_at: datetime | None = None
    accessibility_caption: str | None = None
    # Raw thumbnail bytes (not serialized) used by the visual analyzer.
    image_bytes: bytes | None = Field(default=None, exclude=True, repr=False)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FetchedProfile(BaseModel):
    username: str
    full_name: str | None = None
    biography: str | None = None
    external_url: str | None = None
    profile_pic_url: str | None = None
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    is_business: bool = False
    is_verified: bool = False
    is_private: bool = False
    category: str | None = None
    posts: list[FetchedPost] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
#  API request / response models                                              #
# --------------------------------------------------------------------------- #
class AnalyzeRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    # UI language the AI report should be written in.
    language: str = Field(default="fa", pattern="^(fa|ar|en)$")

    @field_validator("username")
    @classmethod
    def _clean(cls, v: str) -> str:
        v = v.strip().lstrip("@")
        # Accept a pasted profile URL too.
        if "instagram.com" in v:
            v = v.rstrip("/").split("/")[-1].split("?")[0]
        return v.lower()


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    shortcode: str
    caption: str | None
    media_type: str
    thumbnail_url: str | None
    permalink: str | None
    likes: int
    comments: int
    video_views: int
    engagement_rate: float
    posted_at: datetime | None
    signals: dict


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    status: str
    growth_score: float | None
    brand_score: float | None
    engagement_score: float | None
    visual_score: float | None
    profile_score: float | None
    created_at: datetime
    completed_at: datetime | None


class AnalysisDetail(AnalysisSummary):
    error: str | None = None
    ai_summary: str | None = None
    strengths: list = Field(default_factory=list)
    weaknesses: list = Field(default_factory=list)
    recommendations: list = Field(default_factory=list)
    report: dict = Field(default_factory=dict)
    posts: list[PostOut] = Field(default_factory=list)
