"""Data-collection package.

A single ``BaseFetcher`` contract lets the platform swap data sources (real
Instagram scraping today, an official API later) without touching analyzers.
"""

from app.fetchers.base import BaseFetcher, FetchError
from app.fetchers.instagram_fetcher import InstagramFetcher

__all__ = ["BaseFetcher", "FetchError", "InstagramFetcher"]
