"""Analysis API endpoints.

The analyze endpoint creates a row immediately and runs the (potentially slow)
fetch + analysis in a background task, so the client can poll for progress —
a lightweight stand-in for a Celery worker that keeps the MVP infra-free.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_session
from app.models import Analysis
from app.schemas.schemas import (
    AnalysisDetail,
    AnalysisSummary,
    AnalyzeRequest,
)
from app.services import AnalysisService

router = APIRouter(prefix="/api", tags=["analysis"])

# A single service instance reuses the authenticated Instagram session.
_service = AnalysisService()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "ai_enabled": settings.ai_enabled,
        "ig_login_enabled": settings.ig_auth_enabled,
        "ai_model": settings.openai_model if settings.ai_enabled else None,
    }


@router.post("/analyze", response_model=AnalysisSummary, status_code=202)
async def analyze(
    payload: AnalyzeRequest,
    background: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> Analysis:
    analysis = Analysis(username=payload.username, language=payload.language)
    session.add(analysis)
    await session.commit()
    await session.refresh(analysis)

    background.add_task(_service.run, analysis.id)
    return analysis


@router.get("/analyses", response_model=list[AnalysisSummary])
async def list_analyses(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
) -> list[Analysis]:
    result = await session.execute(
        select(Analysis).order_by(Analysis.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
) -> Analysis:
    result = await session.execute(
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(selectinload(Analysis.posts))
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
