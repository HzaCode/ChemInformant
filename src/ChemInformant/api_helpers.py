# src/ChemInformant/api_helpers.py
import requests
import requests_cache # Import requests_cache here
import sys
import time
from urllib.parse import quote
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, List, Dict, Any, Union

# --- Constants ---
PUBCHEM_API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUG_VIEW_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data"
REQUEST_TIMEOUT = 15

# --- Caching Setup (Moved from __init__.py) ---
DEFAULT_CACHE_NAME = 'pubchem_cache'
DEFAULT_CACHE_BACKEND = 'sqlite'
DEFAULT_CACHE_EXPIRE_AFTER = 60 * 60 * 24 * 7 # 7 days in seconds

_session = None # Module-level session variable within api_helpers

def setup_cache(cache_name=DEFAULT_CACHE_NAME, backend=DEFAULT_CACHE_BACKEND, expire_after=DEFAULT_CACHE_EXPIRE_AFTER, **kwargs):
    """
    Configures the cache used for PubChem API requests.

    Call this function *before* making any ChemInformant API calls if you
    want to use non-default cache settings. This function should be imported
    from the ChemInformant package level (e.g., `ChemInformant.setup_cache(...)`).

    Args:
        cache_name (str): Name of the cache file/db.
        backend (str): Cache backend ('sqlite', 'memory', etc.).
        expire_after (int | float | None | timedelta): Expiration time in seconds.
        **kwargs: Additional backend arguments for requests_cache.CachedSession.
    """
    global _session
    # Create a new session each time setup_cache is called
    _session = requests_cache.CachedSession(
        cache_name=cache_name,
        backend=backend,
        expire_after=expire_after,
        allowable_codes=[200, 404],
        match_headers=False,
        **kwargs
    )
    # print(f"ChemInformant cache setup: name='{cache_name}', backend='{backend}', expire_after={expire_after}s") # Optional print

def get_session():
    """Internal function to get the current session (cached or default)."""
    global _session
    if _session is None:
       # Initialize with defaults if setup_cache wasn't called explicitly
       # print("ChemInformant: Initializing default cache...") # Optional print
       setup_cache() # Call setup_cache with defaults
       if _session is None: # Safeguard
            raise RuntimeError("Failed to initialize requests session.")
    return _session

# --- Core Fetch Function (uses session defined above) ---
def _fetch_data(url: str, identifier_type: str = "CID", identifier: Any = None) -> Optional[Any]:
    """Fetches data using the configured session. Returns parsed content or None."""
    session = get_session() # Calls internal get_session
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        # was_cached = getattr(response, 'from_cache', False) # Debugging
        # print(f"DEBUG: Cache hit={was_cached} for URL: {url}", file=sys.stderr)

        if response.status_code == 404:
            return None
        response.raise_for_status() # Raise for other 4xx/5xx errors

        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/json' in content_type:
            return response.json()
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            # Decode XML content assuming UTF-8, handle potential errors
            try:
                return response.content.decode('utf-8')
            except UnicodeDecodeError:
                 print(f"Warning: Could not decode XML as UTF-8 from {url}. Returning raw bytes.", file=sys.stderr)
                 return response.content # Fallback to bytes
        else:
             # print(f"Warning: Unexpected content type '{content_type}' from {url}", file=sys.stderr)
            return response.text # Fallback to text

    except requests.exceptions.RequestException as e:
        # Avoid excessive warnings for expected 404s (which are handled above)
        if not (hasattr(e, 'response') and e.response is not None and e.response.status_code == 404):
             print(f"Warning: API request failed for URL {url} ({identifier_type}: {identifier}): {e}", file=sys.stderr)
        return None
    except Exception as e: # Catch other potential errors
        print(f"Warning: An unexpected error occurred processing URL {url}: {e}", file=sys.stderr)
        return None

# --- Identifier Resolution ---
def get_cids_by_name(compound_name: str) -> Optional[List[int]]:
    """Get a list of PubChem CIDs matching a name. Returns None if none found."""
    safe_name = quote(compound_name)
    url = f"{PUBCHEM_API_BASE}/compound/name/{safe_name}/cids/JSON"
    data = _fetch_data(url, identifier_type="Name", identifier=compound_name)
    if data and isinstance(data, dict) and 'IdentifierList' in data:
        cids = data['IdentifierList'].get('CID')
        # Ensure cids is a list and contains integers
        if cids and isinstance(cids, list) and all(isinstance(x, int) for x in cids):
            return cids # Return the full list
    return None

# --- Single CID Lookups ---
def get_cas_unii(cid: int) -> Tuple[Optional[str], Optional[str]]:
    """Get CAS and UNII for a single CID using PUG View."""
    url = f"{PUG_VIEW_BASE}/compound/{cid}/JSON"
    cas: Optional[str] = None
    unii: Optional[str] = None
    data = _fetch_data(url, identifier_type="CID", identifier=cid)
    if isinstance(data, dict) and 'Record' in data:
        record = data.get('Record', {})
        references = record.get('Reference', [])
        if isinstance(references, list):
            for ref in references:
                 if isinstance(ref, dict):
                    source_name = ref.get('SourceName')
                    source_id = ref.get('SourceID')
                    # Check for non-empty source_id
                    if source_name == 'CAS Common Chemistry' and source_id:
                        cas = str(source_id) # Ensure string
                    if source_name == 'FDA Global Substance Registration System (GSRS)' and source_id:
                        unii = str(source_id) # Ensure string
    return cas, unii

def get_additional_properties(cid: int) -> Dict[str, Any]:
    """Get additional chemical properties for single CID."""
    properties_list = "MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName"
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/property/{properties_list}/JSON"
    details: Dict[str, Any] = {'MolecularFormula': None, 'MolecularWeight': None, 'CanonicalSMILES': None, 'IUPACName': None}
    data = _fetch_data(url, identifier_type="CID", identifier=cid)
    if data and isinstance(data, dict) and 'PropertyTable' in data:
        properties_list_data = data['PropertyTable'].get('Properties')
        if properties_list_data and isinstance(properties_list_data, list) and len(properties_list_data) > 0:
            props = properties_list_data[0]
            if isinstance(props, dict):
                for key in details:
                    # Only update if key exists and value is not explicitly missing/null in source?
                    # Pydantic handles None conversion later, so just get what's there.
                    if key in props and props[key] is not None:
                         details[key] = props[key]
    return details

def get_compound_description(cid: int) -> Optional[str]:
    """Get the description for a single CID."""
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/description/XML"
    description: Optional[str] = None
    xml_content = _fetch_data(url, identifier_type="CID", identifier=cid)
    # Use string content directly if _fetch_data decoded it
    if xml_content and isinstance(xml_content, str):
        try:
            # Note: ET.fromstring works on strings too
            ns = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}
            root = ET.fromstring(xml_content)
            desc_element = root.find('.//pug:Information/pug:Description', ns)
            if desc_element is not None and desc_element.text:
                description = desc_element.text.strip()
        except ET.ParseError as e:
            print(f"Warning: Failed to parse XML description string for CID {cid}: {e}", file=sys.stderr)
        except Exception as e:
             print(f"Warning: Unexpected error parsing description XML string for CID {cid}: {e}", file=sys.stderr)
    # Handle case where raw bytes were returned (fallback)
    elif xml_content and isinstance(xml_content, bytes):
         try:
            ns = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}
            root = ET.fromstring(xml_content) # Handles bytes
            desc_element = root.find('.//pug:Information/pug:Description', ns)
            if desc_element is not None and desc_element.text:
                description = desc_element.text.strip()
         except Exception as e:
              print(f"Warning: Failed processing description bytes for CID {cid}: {e}", file=sys.stderr)

    return description

def get_all_synonyms(cid: int) -> List[str]:
    """Get synonyms for a single CID."""
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cid}/synonyms/JSON"
    synonyms: List[str] = []
    data = _fetch_data(url, identifier_type="CID", identifier=cid)
    if data and isinstance(data, dict) and 'InformationList' in data:
        info_list = data['InformationList'].get('Information')
        if info_list and isinstance(info_list, list) and len(info_list) > 0:
            syns = info_list[0].get('Synonym')
            # Ensure it's a list of strings
            if syns and isinstance(syns, list) and all(isinstance(s, str) for s in syns):
               synonyms = syns
    return synonyms


# --- Batch CID Lookups ---

def _get_batch_data_for_cids(cids: List[int], endpoint_segment: str, result_key: str, id_key: str = 'CID') -> Dict[int, Any]:
    """Helper to fetch batch data (JSON) from PubChem for a list of CIDs."""
    if not cids: return {}
    # PubChem list POST limit might be around 500 CIDs, GET limit on URL length
    # Simple comma-separated GET for smaller batches is easier
    cids_str = ",".join(map(str, cids))
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cids_str}/{endpoint_segment}/JSON"
    # TODO: Handle URL length limit for GET requests, potentially switch to POST for large lists
    # if len(cids_str) > SOME_LIMIT: use POST method

    data = _fetch_data(url, identifier_type="Batch CID", identifier=f"{endpoint_segment} for {len(cids)} CIDs")
    results = {}
    if data and isinstance(data, dict) and result_key in data:
        # Determine the key containing the list of results based on endpoint
        items_list_key = 'Properties' if result_key == 'PropertyTable' else 'Information'
        items = data[result_key].get(items_list_key, [])

        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and id_key in item:
                    try: # Ensure CID is int for key
                        item_cid = int(item[id_key])
                        results[item_cid] = item # Store the whole item dict for this CID
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid CID '{item.get(id_key)}' found in batch response for {endpoint_segment}.", file=sys.stderr)
                        continue
    return results

def get_batch_properties(cids: List[int], properties: List[str]) -> Dict[int, Dict[str, Any]]:
    """Get multiple properties for a list of CIDs in one request."""
    if not properties: return {cid: {} for cid in cids} # Return empty dicts if no properties requested
    properties_str = ",".join(properties)
    raw_results = _get_batch_data_for_cids(cids, f"property/{properties_str}", "PropertyTable", 'CID')
    # Ensure all requested CIDs are keys in the final dict, even if missing from response
    final_results = {cid: raw_results.get(cid, {}) for cid in cids}
    return final_results


def get_batch_synonyms(cids: List[int]) -> Dict[int, List[str]]:
    """Get synonyms for a list of CIDs in one request."""
    raw_results = _get_batch_data_for_cids(cids, "synonyms", "InformationList", 'CID')
    synonym_results = {}
    for cid_key, data in raw_results.items():
        # Ensure synonym value is a list of strings
        synonyms_raw = data.get('Synonym', [])
        if isinstance(synonyms_raw, list) and all(isinstance(s, str) for s in synonyms_raw):
             synonym_results[cid_key] = synonyms_raw
        else:
             synonym_results[cid_key] = [] # Default to empty list if format is wrong
    # Ensure all requested CIDs are keys
    final_results = {cid: synonym_results.get(cid, []) for cid in cids}
    return final_results

def get_batch_descriptions(cids: List[int]) -> Dict[int, Optional[str]]:
    """Get descriptions for a list of CIDs in one request (uses XML batch)."""
    if not cids: return {}
    cids_str = ",".join(map(str, cids))
    url = f"{PUBCHEM_API_BASE}/compound/cid/{cids_str}/description/XML"
    xml_content = _fetch_data(url, identifier_type="Batch CID", identifier=f"description for {len(cids)} CIDs")
    results = {}
    # Process XML string if decoded, otherwise try bytes
    content_to_parse = xml_content if isinstance(xml_content, (str, bytes)) else None

    if content_to_parse:
        try:
            ns = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}
            root = ET.fromstring(content_to_parse) # Works for str and bytes
            for info_element in root.findall('.//pug:Information', ns):
                cid_element = info_element.find('pug:CID', ns)
                desc_element = info_element.find('pug:Description', ns)
                if cid_element is not None and cid_element.text and desc_element is not None and desc_element.text:
                    try:
                        cid_val = int(cid_element.text)
                        results[cid_val] = desc_element.text.strip()
                    except (ValueError, TypeError):
                        continue # Skip if CID is not an integer
        except ET.ParseError as e:
            print(f"Warning: Failed to parse batch XML description: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Unexpected error parsing batch description XML: {e}", file=sys.stderr)

    # Ensure all requested CIDs have an entry, defaulting to None if not found in response
    final_results = {cid_req: results.get(cid_req) for cid_req in cids}
    return final_results