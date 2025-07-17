
from __future__ import annotations

import re
from typing import Iterable, List, Union, Dict, Any

import pandas as pd

from . import api_helpers
from .models import Compound, NotFoundError, AmbiguousIdentifierError

# SMILES pattern tokens
_SMILES_TOKENS = re.compile(r"[=#\[\]\(\)]|\d|Br|Cl|Si", re.I)

def _looks_like_smiles(s: str) -> bool:
    return bool(_SMILES_TOKENS.search(s))

def _resolve_to_single_cid(identifier: Union[str, int]) -> int:
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
    df = get_properties([identifier], [prop])
    return df[prop].iat[0] if not df.empty and df["status"].iat[0] == "OK" else None

def get_weight(id_):           return _scalar("molecular_weight",   id_)
def get_formula(id_):          return _scalar("molecular_formula",  id_)
def get_canonical_smiles(id_): return _scalar("canonical_smiles",   id_)
def get_isomeric_smiles(id_):  return _scalar("isomeric_smiles",    id_)
def get_iupac_name(id_):       return _scalar("iupac_name",         id_)
def get_xlogp(id_):            return _scalar("xlogp",              id_)
def get_cas(id_):              return _scalar("cas",                id_)
def get_synonyms(id_):         return _scalar("synonyms",           id_) or []

def get_compound(identifier: Union[str, int]) -> Compound:
    props = list(PROPERTY_ALIASES.keys()) + list(_SPECIAL_PROPS)
    df = get_properties([identifier], props)
    if df.empty or df["status"].iat[0] != "OK":
        raise RuntimeError(f"Failed to fetch compound for {identifier!r}")
    return Compound(**df.iloc[0].to_dict())

def get_compounds(identifiers: Iterable[Union[str, int]]) -> List[Compound]:
    return [get_compound(x) for x in identifiers]

def draw_compound(identifier):
    try:
        import io, requests
        from PIL import Image
        import matplotlib.pyplot as plt
    except ImportError as exc:
        print("[ChemInformant] Cannot render structure:"
              f" missing dependency {exc.name!r}. "
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
