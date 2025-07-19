
from __future__ import annotations

import random
import sys
import time
from typing import List
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
    **kw,
) -> None:
    global _session
    _session = requests_cache.CachedSession(
        cache_name     = cache_name,
        backend        = backend,
        expire_after   = expire_after,
        allowable_codes= [200, 404, 503],
        **kw,
    )

def get_session() -> requests_cache.CachedSession:
    global _session
    if _session is None:
        setup_cache()
    return _session

# Unified fetch with retry and rate-limit
def _execute_fetch(url: str) -> requests.Response:
    return get_session().get(url, timeout=REQUEST_TIMEOUT)

def _fetch_with_ratelimit_and_retry(url: str):
    global last_api_call_time

    elapsed = time.time() - last_api_call_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    last_api_call_time = time.time()

    retries, backoff = 0, INITIAL_BACKOFF
    while retries < MAX_RETRIES:
        try:
            resp = _execute_fetch(url)

            if getattr(resp, "from_cache", False) and resp.status_code == 503:
                key = get_session().cache.create_key(resp.request)
                get_session().cache.delete(key)
                with get_session().cache.disabled():
                    resp = _execute_fetch(url)

            if resp.status_code in (200, 404):
                if resp.status_code == 404:
                    return None
                ctype = resp.headers.get("Content-Type", "").lower()
                return resp.json() if "application/json" in ctype else resp.text

            if resp.status_code == 503:
                print(f"[ChemInformant] 503 → retry in {backoff:.1f}s", file=sys.stderr)
            else:
                resp.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"[ChemInformant] network error {e} → retry in {backoff:.1f}s", file=sys.stderr)

        time.sleep(backoff)
        backoff = min(MAX_BACKOFF, backoff * 2) + random.uniform(0, 1)
        retries += 1

    print(f"[ChemInformant] giving up after {MAX_RETRIES} retries: {url}", file=sys.stderr)
    return None

# Thin wrappers around PUG-REST
def get_cids_by_name(name: str):
    url  = f"{PUBCHEM_API_BASE}/compound/name/{quote(name)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None

def get_cids_by_smiles(smiles: str):
    url  = f"{PUBCHEM_API_BASE}/compound/smiles/{quote(smiles)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None

def get_batch_properties(cids: List[int], props: List[str]):
    if not cids or not props:
        return {}
    url = (
        f"{PUBCHEM_API_BASE}/compound/cid/{','.join(map(str, cids))}"
        f"/property/{','.join(props)}/JSON"
    )

    all_props, list_key = [], None
    while True:
        if list_key:
            url = (
                f"{PUBCHEM_API_BASE}/compound/listkey/{list_key}"
                f"/property/{','.join(props)}/JSON"
            )
        data = _fetch_with_ratelimit_and_retry(url)
        if not isinstance(data, dict):
            break
        all_props += data.get("PropertyTable", {}).get("Properties", [])
        list_key = data.get("ListKey")
        if not list_key:
            break

    res = {int(p["CID"]): p for p in all_props if "CID" in p}
    return {cid: res.get(cid, {}) for cid in cids}

def get_cas_for_cid(cid: int):
    url  = f"{PUG_VIEW_BASE}/compound/{cid}/JSON"
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
                                    if markup:
                                        return markup[0]["String"]
    return None

def get_synonyms_for_cid(cid: int):
    url  = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/synonyms/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    if isinstance(data, dict):
        info = data.get("InformationList", {}).get("Information", [])
        if info and isinstance(info[0].get("Synonym"), list):
            return info[0]["Synonym"]
    return []
