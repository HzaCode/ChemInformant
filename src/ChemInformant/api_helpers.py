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
from typing import Any
from urllib.parse import quote

import requests
import requests_cache

# --- Module Constants ---
PUBCHEM_API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUG_VIEW_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data"
REQUEST_TIMEOUT = 15

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
        cache_name=cache_name,
        backend=backend,
        expire_after=expire_after,
        allowable_codes=[
            200,
            404,
            503,
        ],  # Cache "not found" and "server busy" responses
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
    assert _session is not None  # Type narrowing for mypy
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


def _fetch_with_ratelimit_and_retry(
    url: str,
) -> dict[str, Any] | list[Any] | str | None:
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

    retries = 0
    backoff = float(INITIAL_BACKOFF)
    while retries < MAX_RETRIES:
        try:
            resp = _execute_fetch(url)

            # Bust cache for stale 503 errors. If a "server busy" response
            # came from the cache, delete it and try a live request.
            if getattr(resp, "from_cache", False) and resp.status_code == 503:
                session = get_session()
                key = session.cache.create_key(resp.request)
                session.cache.delete(key)
                # Directly fetch without cache
                resp = session.get(url, timeout=REQUEST_TIMEOUT)

            if resp.status_code == 200:
                ctype = resp.headers.get("Content-Type", "").lower()
                return resp.json() if "application/json" in ctype else resp.text

            if resp.status_code == 404:
                return None  # Resource not found is a valid, final state.

            if resp.status_code == 503:
                print(
                    f"[ChemInformant] 503 Server Busy -> retry in {backoff:.1f}s",
                    file=sys.stderr,
                )
            else:
                resp.raise_for_status()  # Trigger for other 4xx/5xx errors

        except requests.exceptions.RequestException as e:
            print(
                f"[ChemInformant] Network error {e} -> retry in {backoff:.1f}s",
                file=sys.stderr,
            )

        time.sleep(backoff)
        # Note: random.uniform is safe here as it's only used for jitter in retry delays
        backoff = min(MAX_BACKOFF, backoff * 2) + random.uniform(
            0.0, 1.0
        )  # Exponential backoff with jitter
        retries += 1

    print(
        f"[ChemInformant] Giving up after {MAX_RETRIES} retries for URL: {url}",
        file=sys.stderr,
    )
    return None


# --- Public-Facing Helper Functions ---


def get_cids_by_name(name: str) -> list[int] | None:
    """
    Fetches PubChem Compound IDs (CIDs) for a given chemical name.

    This function searches PubChem's database for compounds matching the provided
    chemical name. It can return multiple CIDs if the name matches multiple compounds.

    Args:
        name: The chemical name to search for (e.g., "aspirin", "acetylsalicylic acid")

    Returns:
        List of integer CIDs matching the name, or None if not found

    Examples:
        >>> get_cids_by_name("aspirin")
        [2244]
        >>> get_cids_by_name("glucose")
        [5793, 64689, ...]  # Multiple isomers/forms

    Note:
        This function is used internally by get_properties() for name-to-CID resolution.
        End users should typically use get_properties() instead.
    """
    url = f"{PUBCHEM_API_BASE}/compound/name/{quote(name)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None


def get_cids_by_smiles(smiles: str) -> list[int] | None:
    """
    Fetches PubChem Compound IDs (CIDs) for a given SMILES string.

    This function searches PubChem for compounds with structures matching the
    provided SMILES representation. May return multiple CIDs for stereoisomers
    or different representations of the same molecule.

    Args:
        smiles: The SMILES string representing the molecule
                (e.g., "CC(=O)OC1=CC=CC=C1C(=O)O" for aspirin)

    Returns:
        List of integer CIDs matching the SMILES, or None if not found

    Examples:
        >>> get_cids_by_smiles("CC(=O)OC1=CC=CC=C1C(=O)O")
        [2244]
        >>> get_cids_by_smiles("CCO")  # Ethanol
        [702]

    Note:
        This function is used internally by get_properties() for SMILES-to-CID resolution.
        End users should typically use get_properties() instead.
    """
    url = f"{PUBCHEM_API_BASE}/compound/smiles/{quote(smiles)}/cids/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    return data.get("IdentifierList", {}).get("CID") if isinstance(data, dict) else None


def get_batch_properties(
    cids: list[int], props: list[str]
) -> dict[int, dict[str, Any]]:
    """
    Fetches multiple properties for a batch of CIDs in a single request,
    handling API pagination automatically.

    This is the core function for efficient bulk property retrieval from PubChem.
    It automatically handles API pagination when dealing with large batches and
    includes rate limiting and retry logic for reliable data fetching.

    Args:
        cids: List of compound IDs to query
        props: List of property names in CamelCase format
               (e.g., ["MolecularWeight", "XLogP", "CanonicalSMILES"])
               Must use exact PubChem API property names

    Returns:
        Dictionary mapping each CID to its properties. CIDs with no data
        or failed lookups map to empty dictionaries. Properties are returned
        using the original CamelCase names from PubChem.

    Examples:
        >>> get_batch_properties([2244, 702], ["MolecularWeight", "XLogP"])
        {2244: {"CID": 2244, "MolecularWeight": 180.16, "XLogP": 1.2},
         702: {"CID": 702, "MolecularWeight": 46.07, "XLogP": -0.31}}

    Note:
        - This function is used internally by get_properties()
        - Uses PubChem's CamelCase property names, not snake_case
        - Automatically handles pagination for requests with >1000 compounds
        - End users should use get_properties() which provides snake_case output
    """
    if not cids or not props:
        return {}

    # Build the initial URL
    initial_url = (
        f"{PUBCHEM_API_BASE}/compound/cid/{','.join(map(str, cids))}"
        f"/property/{','.join(props)}/JSON"
    )
    data = _fetch_with_ratelimit_and_retry(initial_url)

    if not isinstance(data, dict):
        return {cid: {} for cid in cids}

    # Extract properties from the first page and check for a pagination key
    all_props = data.get("PropertyTable", {}).get("Properties", [])
    list_key = data.get("ListKey")

    # Loop as long as the API provides a ListKey for the next page
    while list_key:
        print(
            f"[ChemInformant] Pagination detected, fetching next page with ListKey: {list_key}",
            file=sys.stderr,
        )
        paginated_url = (
            f"{PUBCHEM_API_BASE}/compound/listkey/{list_key}"
            f"/property/{','.join(props)}/JSON"
        )
        data = _fetch_with_ratelimit_and_retry(paginated_url)

        if isinstance(data, dict):
            # Add properties from the new page to our list
            all_props.extend(data.get("PropertyTable", {}).get("Properties", []))
            # Get the next ListKey, or None if this is the last page
            list_key = data.get("ListKey")
        else:
            # If a paginated request fails, stop looping
            list_key = None

    # Organize all collected properties by CID
    res = {int(p["CID"]): p for p in all_props if "CID" in p}

    # Ensure every originally requested CID has an entry in the final dictionary
    return {cid: res.get(cid, {}) for cid in cids}


def get_cas_for_cid(cid: int) -> str | None:
    """
    Fetches the primary CAS Registry Number for a single CID using the PUG-View endpoint.

    This function accesses PubChem's detailed compound records to extract CAS numbers,
    which are unique chemical identifiers assigned by the Chemical Abstracts Service.
    Uses the PUG-View API to parse the "Names and Identifiers" section.

    Args:
        cid: The PubChem compound ID to look up

    Returns:
        The first found CAS Registry Number as a string (e.g., "50-78-2"),
        or None if no CAS number is found

    Examples:
        >>> get_cas_for_cid(2244)  # Aspirin
        '50-78-2'
        >>> get_cas_for_cid(702)   # Ethanol
        '64-17-5'

    Note:
        This function is used internally by get_properties() and get_cas().
        It may be slower than standard property queries as it accesses
        detailed compound records rather than the property API.
    """
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
                                    markup = info.get("Value", {}).get(
                                        "StringWithMarkup"
                                    )
                                    if markup and isinstance(markup, list) and markup:
                                        string_val = markup[0].get("String")
                                        return (
                                            string_val
                                            if isinstance(string_val, str)
                                            else None
                                        )
    return None


def get_synonyms_for_cid(cid: int) -> list[str]:
    """
    Fetches all known synonyms (alternative names) for a given CID.

    This function retrieves the comprehensive list of names associated with a compound,
    including common names, systematic names, brand names, and other identifiers
    from PubChem's synonyms database.

    Args:
        cid: The PubChem compound ID to look up

    Returns:
        List of synonym strings in order of preference/frequency.
        Returns empty list if no synonyms are found.

    Examples:
        >>> get_synonyms_for_cid(2244)  # Aspirin
        ['aspirin', 'acetylsalicylic acid', '2-acetyloxybenzoic acid', ...]
        >>> get_synonyms_for_cid(702)   # Ethanol
        ['ethanol', 'ethyl alcohol', 'grain alcohol', ...]

    Note:
        This function is used internally by get_properties() and get_synonyms().
        The first synonym in the list is typically the preferred/most common name.
    """
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/synonyms/JSON"
    data = _fetch_with_ratelimit_and_retry(url)
    if isinstance(data, dict):
        info_list = data.get("InformationList", {}).get("Information", [])
        if info_list and isinstance(info_list[0].get("Synonym"), list):
            synonyms = info_list[0]["Synonym"]
            return synonyms if isinstance(synonyms, list) else []
    return []
