"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import update

from app.api.routes import analysis_router, media_router
from app.config import settings
from app.database import SessionLocal, init_db
from app.models import Analysis, AnalysisStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

logger = logging.getLogger("tadna")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Mark any analyses that were interrupted by a previous restart as failed.
    async with SessionLocal() as session:
        result = await session.execute(
            update(Analysis)
            .where(Analysis.status.in_([AnalysisStatus.PENDING, AnalysisStatus.RUNNING]))
            .values(status=AnalysisStatus.FAILED, error="Server restarted while analysis was in progress.")
        )
        stuck = result.rowcount
        await session.commit()
    if stuck:
        logger.warning("Marked %d interrupted analysis/analyses as failed on startup.", stuck)

    logger.info(
        "Tadna Insta API ready | AI=%s | IG-login=%s",
        settings.ai_enabled,
        settings.ig_login_enabled,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI Instagram Growth Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(media_router)


@app.get("/")
async def root() -> dict:
    return {"name": settings.app_name, "docs": "/docs", "health": "/api/health"}
