"""Image proxy.

Instagram serves avatars and post thumbnails from its CDN (cdninstagram.com /
fbcdn.net), which the browser frequently cannot load directly — the URLs are
hotlink-restricted and the CDN is often unreachable on networks where Instagram
is filtered. The backend already authenticates to Instagram and reaches the CDN
(optionally via IG_PROXY), so it proxies the image bytes to the client. This
keeps avatars working regardless of the browser's own connectivity.
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, HTTPException, Query, Response

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["media"])

# Only proxy Instagram's own CDN hosts so this can't be abused as an open proxy.
_ALLOWED_HOST_SUFFIXES = (".cdninstagram.com", ".fbcdn.net")


def _fetch(url: str) -> requests.Response:
    return requests.get(
        url,
        timeout=12,
        proxies=settings.proxies,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.instagram.com/",
        },
    )


@router.get("/image")
async def proxy_image(url: str = Query(..., max_length=2048)) -> Response:
    host = (urlparse(url).hostname or "").lower()
    if not host.endswith(_ALLOWED_HOST_SUFFIXES):
        raise HTTPException(status_code=400, detail="Only Instagram CDN URLs allowed.")

    try:
        # requests is synchronous; run it off the event loop.
        resp = await asyncio.to_thread(_fetch, url)
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Image proxy failed for %s: %s", url, exc)
        raise HTTPException(status_code=502, detail="Could not fetch image.") from exc

    return Response(
        content=resp.content,
        media_type=resp.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )
