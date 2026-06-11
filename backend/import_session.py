"""Import a logged-in Instagram session from your web browser.

This is the most reliable way to authenticate when a direct login hits a
"Checkpoint required" challenge: instead of logging in through the script, you
log in normally at https://www.instagram.com in your browser (with your VPN on,
completing any verification there), and this tool copies that already-verified
session into a file the analyzer can use.

Steps:
  1) In Chrome / Edge / Firefox, open instagram.com and make sure you are
     logged in (complete any "Was this you?" checkpoint in the browser).
  2) Run:  python import_session.py
  3) Set IG_USERNAME in backend/.env to that account.

No password is ever entered here — only the browser's session cookie is read.
"""

from __future__ import annotations

import sys
from pathlib import Path

import instaloader

from app.config import settings

BROWSERS = ["chrome", "edge", "firefox", "brave", "chromium", "opera"]


def _load_cookies(browser: str | None):
    import browser_cookie3 as bc

    if browser:
        loader = getattr(bc, browser, None)
        if loader is None:
            raise ValueError(f"Unknown browser '{browser}'.")
        return loader(domain_name="instagram.com")

    # Try every supported browser until one yields Instagram cookies.
    last_exc: Exception | None = None
    for name in BROWSERS:
        loader = getattr(bc, name, None)
        if loader is None:
            continue
        try:
            jar = loader(domain_name="instagram.com")
            if any(c.name == "sessionid" for c in jar):
                print(f"[i] Using cookies from: {name}")
                return jar
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError("No Instagram cookies found in any browser.")


def main() -> int:
    print("=" * 60)
    print("  Tadna Insta — import Instagram session from browser")
    print("=" * 60)

    browser = (
        input(f"Browser {BROWSERS} (Enter = auto-detect): ").strip().lower() or None
    )

    try:
        cookies = _load_cookies(browser)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[x] Could not read browser cookies: {exc}")
        print("    Make sure you are logged into instagram.com in that browser.")
        return 1

    loader = instaloader.Instaloader(quiet=True)
    if settings.proxies:
        loader.context._session.proxies.update(settings.proxies)
        print(f"[i] Routing through proxy: {settings.ig_proxy}")

    loader.context._session.cookies.update(cookies)

    username = loader.test_login()
    if not username:
        print("\n[x] The imported cookies are not logged in.")
        print("    Open instagram.com in your browser, log in, then retry.")
        return 1

    loader.context.username = username
    session_dir = Path(settings.ig_session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{username}.session"
    loader.save_session_to_file(str(session_file))

    print(f"\n[ok] Imported session for @{username}.")
    print(f"[ok] Saved to: {session_file.resolve()}")
    print(f"\nNow set  IG_USERNAME={username}  in backend/.env and restart.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
