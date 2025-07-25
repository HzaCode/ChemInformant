"""Internal helper module for handling direct communication with the PubChem API.

This module manages the HTTP session, caching, rate-limiting, and retry logic,
and provides low-level functions that wrap specific PubChem PUG-REST endpoints.
These functions are not intended for direct use by end-users, but are consumed
by the main API interface.
"""
from __future__ import annotations

import random
import sys
import time
from typing import List, Dict, Any
from urllib.parse import quote

import requests
import requests_cache

# --- Module Constants ---
PUBCHEM_API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUG_VIEW_BASE    = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data"
REQUEST_TIMEOUT  = 15

MAX_RETRIES, INITIAL_BACKOFF, MAX_BACKOFF = 5, 1, 16
REQUEST_RATE_LIMIT = 5  # Requests per second
MIN_REQUEST_INTERVAL = 1.0 / REQUEST_RATE_LIMIT

# --- Module Globals ---
last_api_call_time: float = 0.0
_session: requests_cache.CachedSession | None = None


# --- Session & Caching ---

def setup_cache(
    cache_name: str = "pubchem_cache",
    backend: str = "sqlite",
    expire_after: int = 7 * 24 * 3600,
    **kw: Any,
) -> None:
    """
    Configures and initializes the persistent cache for API requests.

    This function sets up a ``requests_cache`` session that will store API
    responses on disk, significantly speeding up repeated queries and reducing
    network traffic.

    :param cache_name: The name of the cache file (without extension).
    :type cache_name: str
    :param backend: The cache backend to use (e.g., 'sqlite', 'redis').
    :type backend: str
    :param expire_after: Cache expiration time in seconds. Defaults to one week.
    :type expire_after: int
    :param kw: Additional keyword arguments passed directly to the
               ``requests_cache.CachedSession`` constructor.
    """
    global _session
    _session = requests_cache.CachedSession(
        cache_name     = cache_name,
        backend        = backend,
        expire_after   = expire_after,
        allowable_codes= [200, 404, 503],  # Cache "not found" and "server busy" responses
        **kw,
    )

def get_session() -> requests_cache.CachedSession:
    """
    Gets the current cached session, initializing it with defaults if necessary.

    This ensures a single, consistent session is used for all API calls.

    :return: The active ``requests_cache.CachedSession`` instance.
    :rtype: requests_cache.CachedSession
    """
    global _session
    if _session is None:
        setup_cache()
    return _session


# --- Core Fetching Logic ---

def _execute_fetch(url: str) -> requests.Response:
    """
    Executes a single GET request using the global session.

    :param url: The URL to fetch.
    :type url: str
    :return: The server's response.
    :rtype: requests.Response
    """
    return get_session().get(url, timeout=REQUEST_TIMEOUT)

def _fetch_with_ratelimit_and_retry(url: str) -> Dict[str, Any] | List[Any] | str | None:
    """
    Performs a GET request with rate-limiting and exponential backoff retry logic.

    This is the core network function that ensures robust communication with the
    PubChem API by respecting its rate limits and handling transient network
    or server errors gracefully.

    :param url: The URL to fetch data from.
    :type url: str
    :return: The parsed JSON data (as a dict or list), raw text data (as a str),
             or ``None`` if the request ultimately fails after all retries or
             if a 404 Not Found status is received.
    :rtype: Dict[str, Any] | List[Any] | str | None
    """
    global last_api_call_time

    # Enforce rate limit to avoid being blocked by the API
    elapsed = time.time() - last_api_call_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    last_api_call_time = time.time()

    retries, backoff = 0, INITIAL_BACKOFF
    while retries < MAX_RETRIES:
        try:
            resp = _execute_fetch(url)

            # Bust cache for stale 503 errors. If a "server busy" response
            # came from the cache, delete it and try a live request.
            if getattr(resp, "from_cache", False) and resp.status_code == 503:
                key = get_session().cache.create_key(resp.request)
                get_session().cache.delete(key)
                with get_session().cache.disabled():
                    resp = _execute_fetch(url)

            if resp.status_code == 200:
                ctype = resp.headers.get("Content-Type", "").lower()
                return resp.json() if "application/json" in ctype else resp.text
            
            if resp.status_code == 404:
                return None  # Resource not found is a valid, final state.

            if resp.status_code == 503:
                print(f"[ChemInformant] 503 Server Busy -> retry in {backoff:.1f}s", file=sys.stderr)
            else:
                resp.raise_for_status()  # Trigger for other 4xx/5xx errors

        except requests.exceptions.RequestException as e:
            print(f"[ChemInformant] Network error {e} -> retry in {backoff:.1f}s", file=sys.stderr)

        time.sleep(backoff)
        backoff = min(MAX_BACKOFF, backoff * 2) + random.uniform(0, 1) # Exponential backoff with jitter
        retries += 1

    print(f"[ChemInformant] Giving up after {MAX_RETRIES} retries for URL: {url}", file=sys.stderr)
    return None


# --- Public-Facing Helper Functions ---

def get_cids_by_name(name: str) -> List[int] | None:
    """
    Fetches PubChem Compound IDs (CIDs) for a given chemical name.

    :param name: The chemical name to search for (e.g., "aspirin").
    :type name: str
    :return: A list of integer CIDs matching the name, or ``None`` if not found.
    :rtype: List[int] | None
    """
    url  = f"{PUBCHEM_API_BASE}/compound/name/{quote(name)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None

def get_cids_by_smiles(smiles: str) -> List[int] | None:
    """
    Fetches PubChem Compound IDs (CIDs) for a given SMILES string.

    :param smiles: The SMILES string representing the molecule.
    :type smiles: str
    :return: A list of integer CIDs matching the SMILES, or ``None`` if not found.
    :rtype: List[int] | None
    """
    url  = f"{PUBCHEM_API_BASE}/compound/smiles/{quote(smiles)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None

def get_batch_properties(cids: List[int], props: List[str]) -> Dict[int, Dict[str, Any]]:
    """
    Fetches multiple properties for a batch of CIDs in a single request.

    :param cids: A list of CIDs to query.
    :type cids: List[int]
    :param props: A list of property names to retrieve (e.g., "MolecularWeight", "XLogP").
    :type props: List[str]
    :return: A dictionary mapping each requested CID to its properties. If a CID
             was not found or had no properties, it will map to an empty dict.
    :rtype: Dict[int, Dict[str, Any]]
    """
    if not cids or not props:
        return {}
        
    url = (
        f"{PUBCHEM_API_BASE}/compound/cid/{','.join(map(str, cids))}"
        f"/property/{','.join(props)}/JSON"
    )
    data = _fetch_with_ratelimit_and_retry(url)

    # The API might not return all results in one go and may use a listkey for pagination.
    # This loop is currently not fully implemented to handle pagination but sets the foundation.
    if isinstance(data, dict):
        all_props = data.get("PropertyTable", {}).get("Properties", [])
        res = {int(p["CID"]): p for p in all_props if "CID" in p}
        # Ensure every requested CID has an entry in the result for consistency.
        return {cid: res.get(cid, {}) for cid in cids}
    
    return {cid: {} for cid in cids} # Return empty dict for each CID on failure

def get_cas_for_cid(cid: int) -> str | None:
    """
    Fetches the primary CAS number for a single CID using the PUG-View endpoint.

    This function parses the detailed "Names and Identifiers" section of the
    full data record for a compound.

    :param cid: The compound ID to look up.
    :type cid: int
    :return: The first found CAS number as a string, or ``None`` if none is found.
    :rtype: str | None
    """
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
                                    if markup and isinstance(markup, list) and markup:
                                        return markup[0].get("String")
    return None

def get_synonyms_for_cid(cid: int) -> List[str]:
    """
    Fetches all synonyms for a given CID.

    :param cid: The compound ID to look up.
    :type cid: int
    :return: A list of synonym strings. Returns an empty list if no synonyms are found.
    :rtype: List[str]
    """
    url  = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/synonyms/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    if isinstance(data, dict):
        info_list = data.get("InformationList", {}).get("Information", [])
        if info_list and isinstance(info_list[0].get("Synonym"), list):
            return info_list[0]["Synonym"]
    return []