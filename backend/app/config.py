"""Application configuration.

All settings are loaded from environment variables (or a local ``.env`` file)
via pydantic-settings. This keeps secrets out of the codebase and makes the
app trivially configurable across environments.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Tadna Insta"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./tadna.db"

    # --- OpenAI ---
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # --- Instagram ---
    ig_username: str | None = None
    ig_password: str | None = None
    ig_post_limit: int = Field(default=20, ge=1, le=50)
    ig_session_dir: str = "./.ig_sessions"
    # Route Instagram traffic through a proxy (needed where instagram.com is
    # network-blocked). Examples:
    #   http://127.0.0.1:10809   (V2Ray/Xray HTTP inbound)
    #   socks5h://127.0.0.1:1080 (SOCKS5; 'h' resolves DNS through the proxy)
    ig_proxy: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def ig_login_enabled(self) -> bool:
        return bool(self.ig_username and self.ig_password)

    @property
    def proxies(self) -> dict[str, str] | None:
        """requests-style proxy mapping, or None when no proxy is configured."""
        if not self.ig_proxy:
            return None
        return {"http": self.ig_proxy, "https": self.ig_proxy}


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor (single instance per process)."""
    return Settings()


settings = get_settings()
