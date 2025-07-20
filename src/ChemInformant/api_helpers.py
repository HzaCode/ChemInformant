"""
Internal helper module for handling direct communication with the PubChem API.

This module manages the HTTP session, caching, rate-limiting, and retry logic,
and provides low-level functions that wrap specific PubChem PUG-REST endpoints.
These functions are not intended for direct use by end-users.
"""
from __future__ import annotations

import random
import sys
import time
from typing import List, Dict, Any
from urllib.parse import quote

import requests
import requests_cache

# Config
PUBCHEM_API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUG_VIEW_BASE    = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data"
REQUEST_TIMEOUT  = 15

MAX_RETRIES, INITIAL_BACKOFF, MAX_BACKOFF = 5, 1, 16
REQUEST_RATE_LIMIT = 5
MIN_REQUEST_INTERVAL = 1.0 / REQUEST_RATE_LIMIT

last_api_call_time = 0.0
_session: requests_cache.CachedSession | None = None

# Session & caching
def setup_cache(
    cache_name: str = "pubchem_cache",
    backend: str = "sqlite",
    expire_after: int = 7 * 24 * 3600,
    **kw: Any,
) -> None:
    """
    Configures and initializes the persistent cache for API requests.

    This function sets up a `requests_cache` session that will store API
    responses on disk, significantly speeding up repeated queries.

    Args:
        cache_name: The name of the cache file (without extension).
        backend: The cache backend to use (e.g., 'sqlite', 'redis').
        expire_after: The cache expiration time in seconds. Defaults to one week.
        **kw: Additional keyword arguments passed to `requests_cache.CachedSession`.
    """
    global _session
    _session = requests_cache.CachedSession(
        cache_name     = cache_name,
        backend        = backend,
        expire_after   = expire_after,
        allowable_codes= [200, 404, 503],
        **kw,
    )

def get_session() -> requests_cache.CachedSession:
    """Gets the current cached session, initializing it if necessary."""
    global _session
    if _session is None:
        setup_cache()
    return _session

# Unified fetch with retry and rate-limit
def _execute_fetch(url: str) -> requests.Response:
    """Executes a single GET request using the global session."""
    return get_session().get(url, timeout=REQUEST_TIMEOUT)

def _fetch_with_ratelimit_and_retry(url: str) -> Dict[str, Any] | List[Any] | str | None:
    """
    Performs a GET request with rate-limiting and exponential backoff retry logic.
    This is the core network function that ensures robustness.
    """
    global last_api_call_time

    # Enforce rate limit
    elapsed = time.time() - last_api_call_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    last_api_call_time = time.time()

    retries, backoff = 0, INITIAL_BACKOFF
    while retries < MAX_RETRIES:
        try:
            resp = _execute_fetch(url)

            # Bust cache for stale 503 errors
            if getattr(resp, "from_cache", False) and resp.status_code == 503:
                key = get_session().cache.create_key(resp.request)
                get_session().cache.delete(key)
                with get_session().