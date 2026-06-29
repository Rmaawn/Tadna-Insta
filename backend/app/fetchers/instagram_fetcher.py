"""Real Instagram data collection via instaloader.

Reliability strategy
--------------------
Anonymous Instagram requests are aggressively rate-limited and frequently
blocked. To get dependable data we support logging in **once** with a real
(ideally secondary) account: the authenticated session is then cached to disk
(``IG_SESSION_DIR``) and reused on every subsequent run, so the password is
only ever needed for the first login.

instaloader is synchronous, so the blocking work runs in a worker thread via
``asyncio.to_thread`` to keep the FastAPI event loop responsive.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timezone
from pathlib import Path

import instaloader
import requests
from instaloader import (
    ConnectionException,
    Post,
    Profile,
    ProfileNotExistsException,
    TwoFactorAuthRequiredException,
)

from app.config import settings
from app.fetchers.base import BaseFetcher, FetchError
from app.schemas.schemas import FetchedPost, FetchedProfile

logger = logging.getLogger(__name__)

_MEDIA_TYPE = {
    "GraphImage": "image",
    "GraphVideo": "video",
    "GraphSidecar": "carousel",
}


class InstagramFetcher(BaseFetcher):
    """Fetch a public profile and its most recent posts."""

    def __init__(self) -> None:
        self._loader: instaloader.Instaloader | None = None

    # --------------------------------------------------------------------- #
    #  Public async API                                                     #
    # --------------------------------------------------------------------- #
    async def fetch(self, username: str, post_limit: int) -> FetchedProfile:
        return await asyncio.to_thread(self._fetch_sync, username, post_limit)

    # --------------------------------------------------------------------- #
    #  Login / session management                                           #
    # --------------------------------------------------------------------- #
    def _get_loader(self) -> instaloader.Instaloader:
        if self._loader is not None:
            return self._loader

        loader = instaloader.Instaloader(
            quiet=True,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=2,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            ),
        )

        # Route through a proxy where instagram.com is network-blocked.
        if settings.proxies:
            loader.context._session.proxies.update(settings.proxies)
            logger.info("Instagram traffic routed through proxy %s", settings.ig_proxy)

        # Authenticate if any method is configured.
        if settings.ig_auth_enabled:
            self._login(loader)

        self._loader = loader
        return loader

    def _login(self, loader: instaloader.Instaloader) -> None:
        session_dir = Path(settings.ig_session_dir)
        session_dir.mkdir(parents=True, exist_ok=True)

        # 0) Best path for local dev: a `sessionid` cookie pasted from Chrome.
        #    No password, no checkpoint — works behind a VPN.
        if settings.ig_sessionid:
            self._login_with_sessionid(loader, session_dir)
            return

        user = settings.ig_username
        session_file = session_dir / f"{user}.session"

        # 1) Reuse a cached session if present (no password required).
        if session_file.exists():
            try:
                loader.load_session_from_file(user, str(session_file))
                logger.info("Loaded cached Instagram session for %s", user)
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Cached session unusable (%s); re-logging in", exc)

        # 2) No usable session — we need a password to log in.
        if not settings.ig_password:
            raise FetchError(
                f"No cached Instagram session for '{user}'. Run the one-time "
                "login helper:  python login_instagram.py  (or set IG_PASSWORD "
                "in backend/.env)."
            )

        # 3) Fresh login, then persist the session for next time.
        try:
            loader.login(user, settings.ig_password)
            loader.save_session_to_file(str(session_file))
            logger.info("Logged in to Instagram and cached session for %s", user)
        except TwoFactorAuthRequiredException as exc:
            raise FetchError(
                "This account has 2FA enabled. Run  python login_instagram.py  "
                "once to complete the two-factor login interactively."
            ) from exc
        except Exception as exc:  # noqa: BLE001
            if self._looks_like_network_block(exc):
                raise FetchError(self._connection_hint(exc)) from exc
            raise FetchError(f"Instagram login failed: {exc}") from exc

    def _login_with_sessionid(
        self, loader: instaloader.Instaloader, session_dir: Path
    ) -> None:
        """Authenticate using a `sessionid` cookie copied from Chrome DevTools.

        ``instaloader.test_login()`` pings a legacy GraphQL endpoint that
        Instagram now throttles/blocks (it answers ``401 "Please wait a few
        minutes…"``), so it returns ``None`` even for a perfectly valid
        session. We therefore treat the check as *best-effort*: if it confirms
        a username we use it, otherwise we keep the session cookie and let the
        real profile fetch be the source of truth — that endpoint
        (``web_profile_info``) works fine and will surface any genuine auth
        failure with a clearer, page-specific message. This avoids aborting a
        valid session with a misleading "IG_SESSIONID is invalid or expired".
        """
        sess = loader.context._session
        sessionid = settings.ig_sessionid
        sess.cookies.set("sessionid", sessionid, domain=".instagram.com")

        # The Instagram user id is the leading part of the sessionid
        # ("<ds_user_id>:<token>:…", URL-encoded as "%3A"). Set the ds_user_id
        # cookie from it so requests are treated as authenticated even when no
        # explicit IG_DS_USER_ID is configured.
        ds_user_id = settings.ig_ds_user_id or self._ds_user_id_from_sessionid(sessionid)
        if ds_user_id:
            sess.cookies.set("ds_user_id", ds_user_id, domain=".instagram.com")

        username = None
        try:
            username = loader.test_login()
        except Exception as exc:  # noqa: BLE001
            if self._looks_like_network_block(exc):
                raise FetchError(self._connection_hint(exc)) from exc
            logger.warning("Could not verify Instagram session: %s", exc)

        loader.context.user_id = ds_user_id

        if username:
            loader.context.username = username
            try:
                loader.save_session_to_file(str(session_dir / f"{username}.session"))
            except Exception:  # noqa: BLE001
                pass  # session caching is best-effort
            logger.info(
                "Authenticated to Instagram as %s via sessionid cookie", username
            )
            return

        # test_login() couldn't confirm the session — almost always because
        # Instagram throttled its legacy check endpoint, not because the cookie
        # is bad. Proceed with the sessionid cookie set; the fetch will report a
        # real auth problem if one exists.
        logger.warning(
            "Instagram session not confirmed by test_login (the legacy check "
            "endpoint is throttled); proceeding with the sessionid cookie. If "
            "fetches fail with an auth error, refresh IG_SESSIONID in backend/.env."
        )

    @staticmethod
    def _ds_user_id_from_sessionid(sessionid: str | None) -> str | None:
        """Extract the numeric Instagram user id embedded in a sessionid cookie."""
        if not sessionid:
            return None
        from urllib.parse import unquote

        head = unquote(sessionid).split(":", 1)[0]
        return head if head.isdigit() else None

    @staticmethod
    def _looks_like_network_block(exc: Exception) -> bool:
        text = str(exc).lower()
        return any(
            s in text
            for s in ("refused", "max retries", "timed out", "newconnectionerror",
                      "failed to establish", "connection aborted", "10061", "10060")
        )

    @staticmethod
    def _connection_hint(exc: Exception) -> str:
        if InstagramFetcher._looks_like_network_block(exc) and not settings.proxies:
            return (
                "Cannot reach instagram.com — it appears to be network-blocked. "
                "Set IG_PROXY in backend/.env to route through your VPN/proxy "
                "(e.g. http://127.0.0.1:10809 or socks5h://127.0.0.1:1080), then "
                "retry."
            )
        if settings.proxies:
            return (
                f"Could not reach Instagram via proxy {settings.ig_proxy}. Check "
                "that the proxy/VPN is running and the address is correct."
            )
        return (
            "Instagram blocked the request. Log in once with "
            "`python login_instagram.py`, then retry."
        )

    # --------------------------------------------------------------------- #
    #  Synchronous fetch (runs in a worker thread)                          #
    # --------------------------------------------------------------------- #
    def _fetch_sync(self, username: str, post_limit: int) -> FetchedProfile:
        loader = self._get_loader()

        try:
            profile = Profile.from_username(loader.context, username)
        except ProfileNotExistsException as exc:
            raise FetchError(f"Profile @{username} does not exist.") from exc
        except ConnectionException as exc:
            raise FetchError(self._connection_hint(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise FetchError(f"Could not load @{username}: {exc}") from exc

        fetched = FetchedProfile(
            username=profile.username,
            full_name=profile.full_name,
            biography=profile.biography,
            external_url=profile.external_url,
            profile_pic_url=profile.profile_pic_url,
            followers=profile.followers,
            following=profile.followees,
            posts_count=profile.mediacount,
            is_business=bool(getattr(profile, "is_business_account", False)),
            is_verified=bool(profile.is_verified),
            is_private=bool(profile.is_private),
            category=getattr(profile, "business_category_name", None),
        )

        if profile.is_private:
            raise FetchError(
                f"@{username} is private. Only public profiles can be analyzed."
            )

        fetched.posts = self._fetch_posts(profile, post_limit)
        return fetched

    def _fetch_posts(self, profile: Profile, limit: int) -> list[FetchedPost]:
        posts: list[FetchedPost] = []
        try:
            for post in profile.get_posts():
                if len(posts) >= limit:
                    break
                posts.append(self._map_post(post))
        except Exception as exc:  # noqa: BLE001
            # Partial data is still useful; log and continue with what we have.
            logger.warning("Stopped fetching posts early for %s: %s", profile.username, exc)
        return posts

    def _map_post(self, post: Post) -> FetchedPost:
        thumb = post.url
        fetched = FetchedPost(
            shortcode=post.shortcode,
            caption=post.caption,
            media_type=_MEDIA_TYPE.get(post.typename, "image"),
            thumbnail_url=thumb,
            permalink=f"https://www.instagram.com/p/{post.shortcode}/",
            likes=post.likes or 0,
            comments=post.comments or 0,
            video_views=getattr(post, "video_view_count", 0) or 0,
            posted_at=(
                post.date_utc.replace(tzinfo=timezone.utc) if post.date_utc else None
            ),
            accessibility_caption=getattr(post, "accessibility_caption", None),
        )
        fetched.image_bytes = self._download_thumbnail(thumb)
        return fetched

    @staticmethod
    def _download_thumbnail(url: str | None) -> bytes | None:
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=12, proxies=settings.proxies)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:  # noqa: BLE001
            logger.debug("Thumbnail download failed: %s", exc)
            return None
