"""One-time interactive Instagram login.

Run this once to create a cached session so the analyzer can fetch real data
reliably (anonymous requests get blocked by Instagram):

    python login_instagram.py

It asks for your username, password and (if needed) a 2FA code, then saves an
authenticated session to the directory configured by IG_SESSION_DIR. Your
password is never stored — only the session token is cached. After this, set
just ``IG_USERNAME`` in backend/.env (no password required).

Tip: use a secondary / throwaway account, not your main one.
"""

from __future__ import annotations

import sys
from getpass import getpass
from pathlib import Path

import instaloader
from instaloader import (
    BadCredentialsException,
    ConnectionException,
    TwoFactorAuthRequiredException,
)

from app.config import settings


def main() -> int:
    print("=" * 60)
    print("  Tadna Insta — Instagram login helper")
    print("=" * 60)

    default_user = settings.ig_username or ""
    prompt = f"Instagram username{f' [{default_user}]' if default_user else ''}: "
    username = input(prompt).strip() or default_user
    if not username:
        print("No username provided. Aborting.")
        return 1

    password = getpass("Password (hidden): ")
    if not password:
        print("No password provided. Aborting.")
        return 1

    loader = instaloader.Instaloader(quiet=True)
    if settings.proxies:
        loader.context._session.proxies.update(settings.proxies)
        print(f"[i] Routing through proxy: {settings.ig_proxy}")

    try:
        loader.login(username, password)
    except TwoFactorAuthRequiredException:
        code = input("Two-factor code: ").strip()
        try:
            loader.two_factor_login(code)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[x] Two-factor login failed: {exc}")
            return 1
    except BadCredentialsException:
        print("\n[x] Wrong username or password.")
        return 1
    except ConnectionException as exc:
        print(f"\n[x] Instagram refused the login (rate-limit / checkpoint): {exc}")
        print("    Wait a few minutes, or confirm the login in the Instagram app, "
              "then retry.")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\n[x] Login failed: {exc}")
        return 1

    session_dir = Path(settings.ig_session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / f"{username}.session"
    loader.save_session_to_file(str(session_file))

    print("\n[ok] Logged in successfully.")
    print(f"[ok] Session cached at: {session_file.resolve()}")
    print("\nNext steps:")
    print(f"  1) In backend/.env set:  IG_USERNAME={username}")
    print("     (you do NOT need to set IG_PASSWORD — the session is cached)")
    print("  2) Restart the backend. Real fetching is now enabled.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
