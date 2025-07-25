"""
ChemInformant – low‑level helper functions for PubChem PUG‑REST.

• Manages HTTP session, persistent caching, rate‑limit, retries.  
• Since v2.3.0 the cache path is resolved via PyStow:
  ~/.data/cheminformant/cache/pubchem_cache.sqlite (overridable via env vars).
"""

from __future__ import annotations

import secrets
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests
import requests_cache

# ──────────────────────────────────────────────────────────────────────────────
#  Cache path resolution (PyStow-aware; fallback supported)
# ──────────────────────────────────────────────────────────────────────────────
try:
    import pystow
except ImportError:
    pystow = None


def _resolve_cache_path(cache_name: str) -> str | Path:
    if pystow is not None:
        module = pystow.module("cheminformant")
        return module.join("cache", name=f"{cache_name}.sqlite")
    return cache_name


# ──────────────────────────────────────────────────────────────────────────────
#  Constants
# ──────────────────────────────────────────────────────────────────────────────
PUBCHEM_API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUG_VIEW_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data"
REQUEST_TIMEOUT = 15

MAX_RETRIES = 5
INITIAL_BACKOFF = 1
MAX_BACKOFF = 16
REQUEST_RATE_LIMIT = 5
MIN_REQUEST_INTERVAL = 1.0 / REQUEST_RATE_LIMIT

last_api_call_time: float = 0.0
_session: requests_cache.CachedSession | None = None


# ──────────────────────────────────────────────────────────────────────────────
#  Session & caching
# ──────────────────────────────────────────────────────────────────────────────
def setup_cache(
    cache_name: str = "pubchem_cache",
    backend: str = "sqlite",
    expire_after: int | float | str | timedelta = 7 * 24 * 3600,
    **kw: Any,
) -> None:
    """Configure the global CachedSession."""
    global _session
    cache_path = _resolve_cache_path(cache_name)
    _session = requests_cache.CachedSession(
        cache_name=str(cache_path),
        backend=backend,
        expire_after=expire_after,
        allowable_codes=[200, 400, 404, 503],
        **kw,
    )


def get_session() -> requests_cache.CachedSession:
    """Return the global CachedSession, initializing if necessary."""
    global _session
    if _session is None:
        setup_cache()
    return _session  # type: ignore


# ──────────────────────────────────────────────────────────────────────────────
#  HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────
def _execute_fetch(url: str) -> requests.Response:
    return get_session().get(url, timeout=REQUEST_TIMEOUT)


def _fetch_with_ratelimit_and_retry(url: str) -> Dict[str, Any] | List[Any] | str | None:
    """
    Perform GET request with client-side rate limiting and exponential backoff.
    """
    global last_api_call_time

    elapsed = time.time() - last_api_call_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    last_api_call_time = time.time()

    retries, backoff = 0, INITIAL_BACKOFF
    while retries < MAX_RETRIES:
        try:
            resp = _execute_fetch(url)

            if resp.status_code == 200:
                ctype = resp.headers.get("Content-Type", "").lower()
                return resp.json() if "application/json" in ctype else resp.text

            if 400 <= resp.status_code < 500:
                return None

            if resp.status_code >= 500:
                if resp.from_cache and resp.status_code == 503:
                    session = get_session()
                    key = session.cache.create_key(resp.request)
                    session.cache.delete(key)
                    with session.cache.disabled():
                        fresh = _execute_fetch(url)
                        if fresh.status_code == 200:
                            ctype = fresh.headers.get("Content-Type", "").lower()
                            return fresh.json() if "application/json" in ctype else fresh.text
        except requests.exceptions.RequestException as exc:
            print(f"[ChemInformant] network error: {exc}", file=sys.stderr)

        time.sleep(backoff)
        backoff = min(MAX_BACKOFF, backoff * 2) + secrets.randbelow(1000) / 1000
        retries += 1

    print(f"[ChemInformant] failed after {MAX_RETRIES} retries", file=sys.stderr)
    return None


# ──────────────────────────────────────────────────────────────────────────────
#  Low‑level PubChem helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_cids_by_name(name: str) -> List[int] | None:
    url = f"{PUBCHEM_API_BASE}/compound/name/{requests.utils.quote(name)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None


def get_cids_by_smiles(smiles: str) -> List[int] | None:
    url = f"{PUBCHEM_API_BASE}/compound/smiles/{requests.utils.quote(smiles)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None


def get_batch_properties(
    cids: List[int],
    props: List[str],
) -> Dict[int, Dict[str, Any]]:
    if not cids or not props:
        return {}

    props_str = ",".join(props)
    current_url = f"{PUBCHEM_API_BASE}/compound/cid/{','.join(map(str, cids))}/property/{props_str}/JSON"
    all_props_data: List[Dict[str, Any]] = []

    while current_url:
        data = _fetch_with_ratelimit_and_retry(current_url)
        next_url = None

        if isinstance(data, dict):
            all_props_data.extend(data.get("PropertyTable", {}).get("Properties", []))

            list_key = data.get("ListKey") or data.get("Waiting", {}).get("ListKey")
            if list_key:
                next_url = f"{PUBCHEM_API_BASE}/compound/listkey/{list_key}/property/{props_str}/JSON"

        current_url = next_url

    return {int(p["CID"]): p for p in all_props_data if "CID" in p}


def get_cas_for_cid(cid: int) -> str | None:
    url = f"{PUG_VIEW_BASE}/compound/{cid}/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    if isinstance(data, dict):
        for sec in data.get("Record", {}).get("Section", []):
            if sec.get("TOCHeading") == "Names and Identifiers":
                for sub in sec.get("Section", []):
                    if sub.get("TOCHeading") == "Other Identifiers":
                        for cas_sec in sub.get("Section", []):
                            if cas_sec.get("TOCHeading") == "CAS":
                                for info in cas_sec.get("Information", []):
                                    markup = info.get("Value", {}).get("StringWithMarkup")
                                    if markup and isinstance(markup, list) and markup:
                                        return markup[0].get("String")
    return None


def get_synonyms_for_cid(cid: int) -> List[str]:
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/synonyms/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    if isinstance(data, dict):
        info_list = data.get("InformationList", {}).get("Information", [])
        if info_list and isinstance(info_list[0].get("Synonym"), list):
            return info_list[0]["Synonym"]
    return []
