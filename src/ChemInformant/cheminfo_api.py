"""
This module contains the high-level, user-facing API for ChemInformant.
These functions are designed for ease of use and to support common
cheminformatics workflows.
"""
from __future__ import annotations

import re
from typing import Iterable, List, Union, Dict, Any

import pandas as pd

from . import api_helpers
from .models import Compound, NotFoundError, AmbiguousIdentifierError

# --- Internal Helper Functions ---

# SMILES pattern tokens
_SMILES_TOKENS = re.compile(r"[=#\[\]\(\)]|\d|Br|Cl|Si", re.I)

def _looks_like_smiles(s: str) -> bool:
    """Checks if a string contains characters typical of SMILES."""
    return bool(_SMILES_TOKENS.search(s))

def _resolve_to_single_cid(identifier: Union[str, int]) -> int:
    """
    Resolves a given identifier (name, CID, or SMILES) to a single,
    unambiguous PubChem CID.
    """
    if isinstance(identifier, int):
        if identifier > 0:
            return identifier
        raise ValueError(f"Invalid CID: {identifier}")
    if isinstance(identifier, str) and identifier.isdigit():
        return int(identifier)

    if isinstance(identifier, str):
        cids = api_helpers.get_cids_by_name(identifier)
        if cids:
            if len(cids) == 1:
                return cids[0]
            raise AmbiguousIdentifierError(identifier, cids)

    if isinstance(identifier, str) and _looks_like_smiles(identifier):
        cids = api_helpers.get_cids_by_smiles(identifier)
        if cids:
            if len(cids) == 1:
                return cids[0]
            raise AmbiguousIdentifierError(identifier, cids)

    raise NotFoundError(identifier)


# --- Core API ---

PROPERTY_ALIASES: Dict[str, List[str]] = {
    "molecular_weight":   ["MolecularWeight"],
    "molecular_formula":  ["MolecularFormula"],
    "canonical_smiles":   ["CanonicalSMILES", "ConnectivitySMILES"],
    "isomeric_smiles":    ["IsomericSMILES", "SMILES"],
    "iupac_name":         ["IUPACName"],
    "xlogp":              ["XLogP"],
}
_SPECIAL_PROPS = {"cas", "synonyms"}

def get_properties(
    identifiers: Iterable[Union[str, int]],
    properties: Iterable[str],
) -> pd.DataFrame:
    """
    Retrieves multiple properties for a list of chemical identifiers.

    This is the main workhorse function for batch data retrieval. It accepts a
    list of mixed-type identifiers (names, CIDs, SMILES) and returns an
    "analysis-ready" Pandas DataFrame with a status column indicating the
    success or failure for each input.

    Args:
        identifiers: An iterable of chemical identifiers. Can be a mix of
            PubChem CIDs (int), names (str), or SMILES strings (str).
        properties: An iterable of property names to retrieve. Supported
            properties include 'molecular_weight', 'molecular_formula',
            'canonical_smiles', 'isomeric_smiles', 'iupac_name', 'xlogp',
            'cas', and 'synonyms'.

    Returns:
        A pandas DataFrame where each row corresponds to an input identifier.
        The DataFrame includes standard columns like `input_identifier`, `cid`,
        `status`, followed by a column for each requested property. The status
        can be 'OK', 'NotFoundError', or 'AmbiguousIdentifierError'.

    Raises:
        ValueError: If any of the requested properties are not supported.
    """
    identifiers = list(identifiers)
    properties  = list(properties)

    if not identifiers or not properties:
        return pd.DataFrame()

    regular     = [p for p in properties if p in PROPERTY_ALIASES]
    specials    = [p for p in properties if p in _SPECIAL_PROPS]
    unsupported = [p for p in properties if p not in regular + specials]
    if unsupported:
        raise ValueError(f"Unsupported properties: {unsupported}")

    meta: Dict[Any, Dict[str, Any]] = {}
    cids_needed: set[int] = set()
    for ident in identifiers:
        try:
            cid = _resolve_to_single_cid(ident)
            meta[ident] = {"status": "OK", "cid": cid}
            cids_needed.add(cid)
        except Exception as exc:
            meta[ident] = {"status": type(exc).__name__, "cid": None}

    fetched_regular: Dict[int, Dict[str, Any]] = {}
    if cids_needed and regular:
        tags: List[str] = []
        for p in regular:
            tags.extend(PROPERTY_ALIASES[p])
        tags = list(dict.fromkeys(tags))
        fetched_regular = api_helpers.get_batch_properties(list(cids_needed), tags)

    fetched_special = {sp: {cid: None for cid in cids_needed} for sp in specials}
    for cid in cids_needed:
        if "cas" in specials:
            fetched_special["cas"][cid] = api_helpers.get_cas_for_cid(cid)
        if "synonyms" in specials:
            fetched_special["synonyms"][cid] = api_helpers.get_synonyms_for_cid(cid)

    rows = []
    for ident in identifiers:
        entry: Dict[str, Any] = {"input_identifier": ident, **meta[ident]}
        if entry["status"] == "OK":
            cid = entry["cid"]
            api_row = fetched_regular.get(cid, {})
            for p in regular:
                val = next(
                    (api_row[tag] for tag in PROPERTY_ALIASES[p] if tag in api_row and api_row[tag]),
                    None,
                )
                entry[p] = val
            for p in specials:
                entry[p] = fetched_special[p][cid]
        else:
            for p in properties:
                entry[p] = None
        rows.append(entry)

    cols = ["input_identifier", "cid", "status"] + properties
    return pd.DataFrame(rows)[cols]

def _scalar(prop: str, identifier: Union[str, int]):
    """Internal helper to get a single value from get_properties."""
    df = get_properties([identifier], [prop])
    return df[prop].iat[0] if not df.empty and df["status"].iat[0] == "OK" else None

# --- Convenience Functions ---

def get_weight(id_: Union[str, int]) -> float | None:
    """Gets the molecular weight for a single identifier."""
    return _scalar("molecular_weight",   id_)

def get_formula(id_: Union[str, int]) -> str | None:
    """Gets the molecular formula for a single identifier."""
    return _scalar("molecular_formula",  id_)

def get_canonical_smiles(id_: Union[str, int]) -> str | None:
    """Gets the canonical SMILES string for a single identifier."""
    return _scalar("canonical_smiles",   id_)

def get_isomeric_smiles(id_: Union[str, int]) -> str | None:
    """Gets the isomeric SMILES string for a single identifier."""
    return _scalar("isomeric_smiles",    id_)

def get_iupac_name(id_: Union[str, int]) -> str | None:
    """Gets the IUPAC name for a single identifier."""
    return _scalar("iupac_name",         id_)

def get_xlogp(id_: Union[str, int]) -> float | None:
    """Gets the XLogP value for a single identifier."""
    return _scalar("xlogp",              id_)

def get_cas(id_: Union[str, int]) -> str | None:
    """Gets the primary CAS number for a single identifier."""
    return _scalar("cas",                id_)

def get_synonyms(id_: Union[str, int]) -> List[str]:
    """Gets a list of synonyms for a single identifier."""
    return _scalar("synonyms",           id_) or []

def get_compound(identifier: Union[str, int]) -> Compound:
    """
    Retrieves all available data for an identifier and returns it as a `Compound` object.

    Args:
        identifier: The chemical identifier (name, CID, or SMILES).

    Returns:
        A `Compound` object populated with data from PubChem.

    Raises:
        RuntimeError: If data fetching fails for the given identifier.
    """
    props = list(PROPERTY_ALIASES.keys()) + list(_SPECIAL_PROPS)
    df = get_properties([identifier], props)
    if df.empty or df["status"].iat[0] != "OK":
        raise RuntimeError(f"Failed to fetch compound for {identifier!r}")
    return Compound(**df.iloc[0].to_dict())

def get_compounds(identifiers: Iterable[Union[str, int]]) -> List[Compound]:
    """
    Retrieves all available data for a list of identifiers.

    Args:
        identifiers: An iterable of chemical identifiers.

    Returns:
        A list of `Compound` objects.
    """
    return [get_compound(x) for x in identifiers]

def draw_compound(identifier: Union[str, int]) -> None:
    """
    Displays the 2D structure of a compound using Matplotlib.

    Note:
        This function requires `requests`, `pillow`, and `matplotlib` to be
        installed. It will print a message if they are missing.
        This function will block and display a plot window.

    Args:
        identifier: The chemical identifier (name, CID, or SMILES).
    """
    try:
        import io, requests
        from PIL import Image
        import matplotlib.pyplot as plt
    except ImportError as exc:
        print(f"[ChemInformant] Cannot render structure: missing dependency {exc.name!r}. "
              "Please `pip install requests pillow matplotlib`.")
        return

    try:
        cid = _resolve_to_single_cid(identifier)
    except Exception as exc:
        print(f"[ChemInformant] Failed to resolve identifier: {exc}")
        return

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
    try:
        img_bytes = requests.get(url, timeout=15).content
        img = Image.open(io.BytesIO(img_bytes))
    except Exception as exc:
        print(f"[ChemInformant] Failed to download structure PNG: {exc}")
        return

    plt.imshow(img)
    plt.axis("off")
    plt.title(f"CID {cid}")
    plt.show()