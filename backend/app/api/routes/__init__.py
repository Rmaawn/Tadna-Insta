"""API routes."""

from app.api.routes.analysis import router as analysis_router
from app.api.routes.media import router as media_router

__all__ = ["analysis_router", "media_router"]
