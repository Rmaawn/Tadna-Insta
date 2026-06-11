"""Fetcher contract shared by every data source."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.schemas import FetchedProfile


class FetchError(Exception):
    """Raised when a profile cannot be fetched (private, missing, blocked...)."""


class BaseFetcher(ABC):
    """Abstract data source for a single Instagram profile."""

    @abstractmethod
    async def fetch(self, username: str, post_limit: int) -> FetchedProfile:
        """Return a fully-populated :class:`FetchedProfile` or raise FetchError."""
        raise NotImplementedError
