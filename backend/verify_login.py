"""Quick check that Instagram authentication is working.

Run this after configuring auth in backend/.env to confirm everything is wired
up before using the app:

    python verify_login.py

It uses the exact same fetcher the app uses, so a success here means the
dashboard will work too.
"""

from __future__ import annotations

import asyncio
import sys

from app.config import settings
from app.fetchers import FetchError, InstagramFetcher


async def main() -> int:
    print("=" * 60)
    print("  Tadna Insta — verify Instagram access")
    print("=" * 60)
    print(f"  proxy      : {settings.ig_proxy or '(none)'}")
    print(f"  sessionid  : {'set' if settings.ig_sessionid else '(none)'}")
    print(f"  username   : {settings.ig_username or '(none)'}")
    print("-" * 60)

    target = (sys.argv[1] if len(sys.argv) > 1 else "instagram").lstrip("@")
    print(f"Fetching a sample profile: @{target} ...\n")

    fetcher = InstagramFetcher()
    try:
        profile = await fetcher.fetch(target, post_limit=3)
    except FetchError as exc:
        print(f"[x] {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[x] Unexpected error: {exc}")
        return 1

    print("[ok] Instagram access works!")
    print(f"     @{profile.username} — {profile.followers:,} followers, "
          f"{len(profile.posts)} posts fetched.")
    print("\nYou're ready: start the backend and analyze any public profile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
