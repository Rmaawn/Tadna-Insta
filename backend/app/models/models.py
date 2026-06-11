"""Database models.

The schema is intentionally compact for the MVP but mirrors the product's
conceptual entities (accounts, posts, analyses/reports, recommendations).
Rich, evolving analyzer output is stored in JSON columns so new analyzers can
extend reports without migrations, while the headline scores are first-class
columns for fast querying and charting.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InstagramAccount(Base):
    """A snapshot of a public Instagram profile at fetch time."""

    __tablename__ = "instagram_accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    biography: Mapped[str | None] = mapped_column(Text)
    external_url: Mapped[str | None] = mapped_column(String(512))
    profile_pic_url: Mapped[str | None] = mapped_column(String(1024))

    followers: Mapped[int] = mapped_column(Integer, default=0)
    following: Mapped[int] = mapped_column(Integer, default=0)
    posts_count: Mapped[int] = mapped_column(Integer, default=0)

    is_business: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_private: Mapped[bool] = mapped_column(default=False)
    category: Mapped[str | None] = mapped_column(String(128))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Post(Base):
    """A single analyzed post belonging to an analysis run."""

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    analysis_id: Mapped[str] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), index=True
    )

    shortcode: Mapped[str] = mapped_column(String(64))
    caption: Mapped[str | None] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(32))  # image | video | carousel
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024))
    permalink: Mapped[str | None] = mapped_column(String(512))

    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    video_views: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)

    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Per-post analyzer signals (colors, has_face, caption metrics, ...).
    signals: Mapped[dict] = mapped_column(JSON, default=dict)

    analysis: Mapped["Analysis"] = relationship(back_populates="posts")


class Analysis(Base):
    """A full growth-intelligence report for one account."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    account_id: Mapped[str | None] = mapped_column(
        ForeignKey("instagram_accounts.id", ondelete="SET NULL")
    )
    username: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8), default="fa")

    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus), default=AnalysisStatus.PENDING, index=True
    )
    error: Mapped[str | None] = mapped_column(Text)

    # --- Headline scores (0-100) ---
    growth_score: Mapped[float | None] = mapped_column(Float)
    brand_score: Mapped[float | None] = mapped_column(Float)
    engagement_score: Mapped[float | None] = mapped_column(Float)
    visual_score: Mapped[float | None] = mapped_column(Float)
    profile_score: Mapped[float | None] = mapped_column(Float)

    # --- AI narrative ---
    ai_summary: Mapped[str | None] = mapped_column(Text)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, default=list)

    # --- Full structured report from every analyzer ---
    report: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    account: Mapped["InstagramAccount | None"] = relationship(
        back_populates="analyses"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
