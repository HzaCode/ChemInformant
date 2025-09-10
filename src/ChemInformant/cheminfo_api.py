"""
This module contains the high-level, user-facing API for ChemInformant.
It now operates exclusively on a snake_case standard for all property names.
"""
from __future__ import annotations

import logging
import re
import sys
from typing import Any, Iterable

import pandas as pd

from . import api_helpers
from .constants import (
    ALL_PROPS,
    CORE_PROPS,
    PROPERTY_ALIASES,
    SNAKE_TO_CAMEL,
    THREED_PROPS,
)
from .models import AmbiguousIdentifierError, Compound, NotFoundError

_SMILES_TOKENS = re.compile(r"[=#\[\]\(\)]|\d|Br|Cl|Si", re.I)
_SPECIAL_PROPS = {"cas", "synonyms"}

def _looks_like_smiles(s: str) -> bool:
    return bool(_SMILES_TOKENS.search(s))

def _resolve_to_single_cid(identifier: str | int) -> int:
    # This function remains robust as is.
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

def get_properties(
    identifiers: int | str | list[int] | list[str],
    properties: str | list[str] | None = None,
    *,
    namespace: str = "cid",
    include_3d: bool = False,
    all_properties: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """
    Retrieve chemical properties for one or more compounds from PubChem.

    This function is the core interface for fetching molecular properties. It accepts
    various types of chemical identifiers and returns data in a standardized snake_case
    format with consistent column ordering and error handling.

    Args:
        identifiers: Chemical identifier(s) to look up. Can be:
            - Single identifier: string name, CID number, or SMILES
            - List of identifiers: mixed types allowed
            Examples: "aspirin", 2244, "CC(=O)OC1=CC=CC=C1C(=O)O"

        properties: Specific properties to retrieve. Can be:
            - None: Returns core property set (default)
            - String: Single property name or comma-separated list
            - List: Multiple property names
            Supports both snake_case ("molecular_weight") and CamelCase ("MolecularWeight")

        namespace: Input identifier namespace (currently only "cid" supported)

        include_3d: If True and properties=None, includes 3D molecular descriptors
            in addition to core properties. Ignored when properties is specified.

        all_properties: If True, retrieves all ~40 available properties from PubChem.
            Mutually exclusive with properties and include_3d parameters.

        **kwargs: Additional keyword arguments (for future compatibility)

    Returns:
        pd.DataFrame: Results with columns:
            - input_identifier: Original input as provided
            - cid: PubChem Compound ID (string type)
            - status: "OK" for success, exception name for failures
            - [property columns]: Requested properties in snake_case format

        Column order preserves the original properties parameter order.
        Failed lookups return rows with status != "OK" and missing property values.

    Raises:
        ValueError: If unsupported properties are requested, or if all_properties=True
            is used with other property selection parameters

    Property Categories:
        Core properties (default): molecular_weight, molecular_formula, canonical_smiles,
            isomeric_smiles, iupac_name, cas, synonyms, xlogp, tpsa, complexity,
            h_bond_donor_count, h_bond_acceptor_count, rotatable_bond_count,
            heavy_atom_count, charge, atom_stereo_count, bond_stereo_count,
            covalent_unit_count, in_ch_i, in_ch_i_key

        3D properties: volume_3d, feature_count_3d, conformer_count_3d, etc.

        Special properties: cas (CAS Registry Number), synonyms (list of names)

    Examples:
        >>> # Get core properties for a single compound
        >>> df = get_properties("aspirin")
        >>> print(df.columns.tolist())
        ['input_identifier', 'cid', 'status', 'molecular_weight', ...]

        >>> # Get specific properties for multiple compounds
        >>> df = get_properties(["aspirin", "caffeine"], properties=["molecular_weight", "xlogp"])
        >>> print(df[["input_identifier", "molecular_weight", "xlogp"]])

        >>> # Get all available properties
        >>> df = get_properties("aspirin", all_properties=True)
        >>> print(f"Retrieved {len(df.columns)} columns")

        >>> # Include 3D descriptors with core set
        >>> df = get_properties("aspirin", include_3d=True)

        >>> # Handle mixed input types and failures
        >>> df = get_properties([2244, "invalid_name", "CC(=O)O"])
        >>> print(df[["input_identifier", "status"]])

    Notes:
        - Uses intelligent fallbacks for SMILES properties (canonical_smiles falls back
          to connectivity_smiles if canonical is unavailable)
        - Automatically handles API pagination for large batch requests
        - Results are cached to improve performance on repeated queries
        - All property names in output use snake_case format for consistency
        - CID column is returned as string type to handle large compound IDs
    """
    # --- Parameter validation ---
    if all_properties and (properties is not None or include_3d):
        raise ValueError("`all_properties=True` is mutually exclusive with `properties` and `include_3d`.")
    if properties is not None and include_3d:
        logging.warning("When `properties` is specified, `include_3d` is ignored.")

    # --- Step 1: Resolve all requested properties to a consistent snake_case list ---
    resolved_props: list[str]
    original_props_order = []
    if all_properties:
        resolved_props = ALL_PROPS[:]  # Get truly ALL properties including special ones
        original_props_order = resolved_props
    elif properties is not None:
        if isinstance(properties, str):
            properties = [p.strip() for p in properties.split(',')]
        original_props_order = list(properties)
        resolved_props = []
        unsupported_props = []
        for prop in properties:
            resolved = PROPERTY_ALIASES.get(prop, PROPERTY_ALIASES.get(prop.lower()))
            if resolved is None:
                unsupported_props.append(prop)
            elif resolved not in resolved_props:
                resolved_props.append(resolved)

        if unsupported_props:
            raise ValueError(f"Unsupported properties: {unsupported_props}")
    else: # Default behavior when properties is None
        resolved_props = CORE_PROPS[:]
        if include_3d:
            resolved_props.extend(THREED_PROPS)
        original_props_order = resolved_props

    # Handle empty properties list - should return empty DataFrame
    if properties is not None and len(resolved_props) == 0:
        return pd.DataFrame()

    if not isinstance(identifiers, list):
        identifiers = [identifiers]

    # --- Step 2: Create base DataFrame with resolved CIDs ---
    meta: dict[Any, dict[str, Any]] = {}
    for ident in identifiers:
        try:
            cid = _resolve_to_single_cid(ident)
            meta[ident] = {"status": "OK", "cid": str(cid)}
        except Exception as exc:
            meta[ident] = {"status": type(exc).__name__, "cid": pd.NA}
    df = pd.DataFrame([{"input_identifier": ident, **meta[ident]} for ident in identifiers])

    # --- Early return for empty inputs ---
    if df.empty:
        return df

    # --- Step 3: Fetch standard properties ---
    standard_props_snake = [p for p in resolved_props if p not in _SPECIAL_PROPS]
    if standard_props_snake:
        # Define internal fallback mappings (these are not exposed as separate properties)
        FALLBACK_MAP_SNAKE = {"canonical_smiles": "connectivity_smiles", "isomeric_smiles": "fallback_smiles"}
        INTERNAL_FALLBACK_TO_CAMEL = {"connectivity_smiles": "ConnectivitySMILES", "fallback_smiles": "SMILES"}

        api_tags_camel = {SNAKE_TO_CAMEL[p] for p in standard_props_snake}
        for prop_snake in standard_props_snake:
            if prop_snake in FALLBACK_MAP_SNAKE:
                fallback_prop = FALLBACK_MAP_SNAKE[prop_snake]
                api_tags_camel.add(INTERNAL_FALLBACK_TO_CAMEL[fallback_prop])

        cids_needed = [int(cid) for cid in df['cid'] if pd.notna(cid)]
        fetched_data = api_helpers.get_batch_properties(cids_needed, list(api_tags_camel)) if cids_needed else {}

        for prop_snake in standard_props_snake:
            prop_camel = SNAKE_TO_CAMEL[prop_snake]
            values = []
            for _, row in df.iterrows():
                cid = int(row["cid"]) if pd.notna(row["cid"]) else None
                val = None
                if row["status"] == "OK" and cid:
                    api_row = fetched_data.get(cid, {})
                    val = api_row.get(prop_camel)
                    if not val and prop_snake in FALLBACK_MAP_SNAKE:
                        fallback_prop = FALLBACK_MAP_SNAKE[prop_snake]
                        fallback_camel = INTERNAL_FALLBACK_TO_CAMEL[fallback_prop]
                        val = api_row.get(fallback_camel)
                values.append(val)
            df[prop_snake] = values

    # --- Step 4: Fetch special properties ---
    special_props_snake = [p for p in resolved_props if p in _SPECIAL_PROPS]
    if special_props_snake:
        for prop_snake in special_props_snake:
            fetch_func = api_helpers.get_cas_for_cid if prop_snake == 'cas' else api_helpers.get_synonyms_for_cid
            fail_value = None if prop_snake == 'cas' else []
            prop_data = [fetch_func(int(cid)) if pd.notna(cid) and status == 'OK' else fail_value for cid, status in zip(df['cid'], df['status'])]
            df[prop_snake] = prop_data

    # --- Step 5: Finalize and order DataFrame ---
    if "cid" in df.columns:
        df = df.astype({"cid": "string"})
    final_col_order = ["input_identifier", "cid", "status"]
    for prop in original_props_order:
        resolved_snake = PROPERTY_ALIASES.get(prop, prop.lower())
        if resolved_snake in df.columns and resolved_snake not in final_col_order:
            final_col_order.append(resolved_snake)

    # Add any remaining columns not yet included
    for col in df.columns:
        if col not in final_col_order:
            final_col_order.append(col)
    return df[final_col_order]

# --- Convenience Functions (now simple and consistent) ---

def _fetch_scalar(id_, prop_snake):
    """Internal helper for single-value convenience functions."""
    try:
        cid = _resolve_to_single_cid(id_)
        prop_camel = SNAKE_TO_CAMEL.get(prop_snake)

        if prop_camel is None:
            raise ValueError(f"Unknown property: {prop_snake}")

        # Define internal fallback mappings for convenience functions
        fallback_map = {"canonical_smiles": "connectivity_smiles", "isomeric_smiles": "fallback_smiles"}
        internal_fallback_to_camel = {"connectivity_smiles": "ConnectivitySMILES", "fallback_smiles": "SMILES"}

        fallback_snake = fallback_map.get(prop_snake)
        fallback_camel = internal_fallback_to_camel.get(fallback_snake) if fallback_snake else None

        props_to_fetch = [prop_camel]
        if fallback_camel:
            props_to_fetch.append(fallback_camel)

        props = api_helpers.get_batch_properties([cid], props_to_fetch)
        data = props.get(cid, {})

        return data.get(prop_camel) or (data.get(fallback_camel) if fallback_camel else None)
    except (NotFoundError, AmbiguousIdentifierError):
        return None

def get_weight(id_: str | int) -> float | None:
    """
    Get the molecular weight of a compound.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Molecular weight in g/mol, or None if compound not found

    Examples:
        >>> get_weight("aspirin")
        180.16
        >>> get_weight(2244)  # Same as above using CID
        180.16
    """
    return _fetch_scalar(id_, "molecular_weight")

def get_formula(id_: str | int) -> str | None:
    """
    Get the molecular formula of a compound.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Molecular formula string, or None if compound not found

    Examples:
        >>> get_formula("aspirin")
        'C9H8O4'
        >>> get_formula("water")
        'H2O'
    """
    return _fetch_scalar(id_, "molecular_formula")

def get_canonical_smiles(id_: str | int) -> str | None:
    """
    Get the canonical SMILES representation of a compound.

    Canonical SMILES provide a unique string representation of molecular structure
    with consistent atom ordering and standardized conventions.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Canonical SMILES string, or None if compound not found

    Examples:
        >>> get_canonical_smiles("aspirin")
        'CC(=O)OC1=CC=CC=C1C(=O)O'
        >>> get_canonical_smiles(2244)
        'CC(=O)OC1=CC=CC=C1C(=O)O'
    """
    return _fetch_scalar(id_, "canonical_smiles")

def get_isomeric_smiles(id_: str | int) -> str | None:
    """
    Get the isomeric SMILES representation of a compound.

    Isomeric SMILES include stereochemical information and isotope specifications,
    providing more detailed structural information than canonical SMILES.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Isomeric SMILES string, or None if compound not found

    Examples:
        >>> get_isomeric_smiles("glucose")
        'C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O'
    """
    return _fetch_scalar(id_, "isomeric_smiles")

def get_iupac_name(id_: str | int) -> str | None:
    """
    Get the IUPAC (systematic) name of a compound.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        IUPAC name string, or None if compound not found

    Examples:
        >>> get_iupac_name("aspirin")
        '2-acetyloxybenzoic acid'
        >>> get_iupac_name("water")
        'oxidane'
    """
    return _fetch_scalar(id_, "iupac_name")

def get_xlogp(id_: str | int) -> float | None:
    """
    Get the XLogP value (octanol-water partition coefficient) of a compound.

    XLogP is a key descriptor for drug discovery, indicating lipophilicity and
    membrane permeability. Values typically range from -3 to +10.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        XLogP value (log units), or None if compound not found

    Examples:
        >>> get_xlogp("aspirin")
        1.2
        >>> get_xlogp("water")
        -0.7
    """
    return _fetch_scalar(id_, "xlogp")

def get_cas(id_: str | int) -> str | None:
    """
    Get the CAS Registry Number of a compound.

    CAS (Chemical Abstracts Service) numbers are unique identifiers assigned
    to chemical substances by the American Chemical Society.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        CAS Registry Number as string, or None if not found

    Examples:
        >>> get_cas("aspirin")
        '50-78-2'
        >>> get_cas("water")
        '7732-18-5'
    """
    try:
        cid = _resolve_to_single_cid(id_)
        return api_helpers.get_cas_for_cid(cid)
    except (NotFoundError, AmbiguousIdentifierError):
        return None

def get_synonyms(id_: str | int) -> list[str]:
    """
    Get all known synonyms (alternative names) for a compound.

    Returns a comprehensive list of names including common names, brand names,
    systematic names, and other identifiers used for the compound.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        List of synonym strings, empty list if compound not found

    Examples:
        >>> synonyms = get_synonyms("aspirin")
        >>> print(synonyms[:3])  # First few names
        ['aspirin', 'acetylsalicylic acid', '2-acetyloxybenzoic acid']
    """
    try:
        cid = _resolve_to_single_cid(id_)
        return api_helpers.get_synonyms_for_cid(cid)
    except (NotFoundError, AmbiguousIdentifierError):
        return []

def get_exact_mass(id_: str | int) -> float | None:
    """
    Get the exact mass of a compound.

    Exact mass is the sum of atomic masses using the most abundant isotopes.
    Used in mass spectrometry for precise compound identification.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Exact mass in Da (atomic mass units), or None if compound not found

    Examples:
        >>> get_exact_mass("aspirin")
        180.04225873
    """
    return _fetch_scalar(id_, "exact_mass")

def get_monoisotopic_mass(id_: str | int) -> float | None:
    """
    Get the monoisotopic mass of a compound.

    Monoisotopic mass is calculated using the most abundant isotope of each element.
    Important for mass spectrometry and structural analysis.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Monoisotopic mass in Da, or None if compound not found

    Examples:
        >>> get_monoisotopic_mass("aspirin")
        180.04225873
    """
    return _fetch_scalar(id_, "monoisotopic_mass")

def get_tpsa(id_: str | int) -> float | None:
    """
    Get the Topological Polar Surface Area (TPSA) of a compound.

    TPSA is a key descriptor for drug discovery, predicting membrane
    permeability and blood-brain barrier penetration. Values < 90 Ų
    suggest good oral bioavailability.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        TPSA value in Ų (square Angstroms), or None if compound not found

    Examples:
        >>> get_tpsa("aspirin")
        63.6
    """
    return _fetch_scalar(id_, "tpsa")

def get_complexity(id_: str | int) -> float | None:
    """
    Get the molecular complexity score of a compound.

    Complexity is a measure of structural intricacy based on symmetry,
    branching, and ring systems. Higher values indicate more complex structures.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Complexity score (unitless), or None if compound not found

    Examples:
        >>> get_complexity("aspirin")
        212
    """
    return _fetch_scalar(id_, "complexity")

def get_h_bond_donor_count(id_: str | int) -> int | None:
    """
    Get the number of hydrogen bond donors in a compound.

    Counts atoms that can donate hydrogen bonds (typically N, O with H).
    Important for drug design and predicting molecular interactions.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of H-bond donors, or None if compound not found

    Examples:
        >>> get_h_bond_donor_count("aspirin")
        1
    """
    return _fetch_scalar(id_, "h_bond_donor_count")

def get_h_bond_acceptor_count(id_: str | int) -> int | None:
    """
    Get the number of hydrogen bond acceptors in a compound.

    Counts atoms that can accept hydrogen bonds (typically N, O).
    Key descriptor for drug-like properties and solubility prediction.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of H-bond acceptors, or None if compound not found

    Examples:
        >>> get_h_bond_acceptor_count("aspirin")
        4
    """
    return _fetch_scalar(id_, "h_bond_acceptor_count")

def get_rotatable_bond_count(id_: str | int) -> int | None:
    """
    Get the number of rotatable bonds in a compound.

    Rotatable bonds are acyclic single bonds between non-terminal heavy atoms.
    Indicates molecular flexibility, important for drug binding and bioavailability.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of rotatable bonds, or None if compound not found

    Examples:
        >>> get_rotatable_bond_count("aspirin")
        3
    """
    return _fetch_scalar(id_, "rotatable_bond_count")

def get_heavy_atom_count(id_: str | int) -> int | None:
    """
    Get the number of heavy atoms (non-hydrogen atoms) in a compound.

    Heavy atoms include all atoms except hydrogen. This is a basic
    measure of molecular size and complexity.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of heavy atoms, or None if compound not found

    Examples:
        >>> get_heavy_atom_count("aspirin")
        13
    """
    return _fetch_scalar(id_, "heavy_atom_count")

def get_charge(id_: str | int) -> int | None:
    """
    Get the formal charge of a compound.

    The total formal charge of the molecule, indicating whether it's
    neutral (0), positively charged (+), or negatively charged (-).

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Formal charge (integer), or None if compound not found

    Examples:
        >>> get_charge("aspirin")
        0
    """
    return _fetch_scalar(id_, "charge")

def get_atom_stereo_count(id_: str | int) -> int | None:
    """
    Get the number of stereocenters (chiral centers) in a compound.

    Counts atoms with defined stereochemistry, important for understanding
    the three-dimensional structure and potential biological activity.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of stereocenters, or None if compound not found

    Examples:
        >>> get_atom_stereo_count("glucose")
        4
    """
    return _fetch_scalar(id_, "atom_stereo_count")

def get_bond_stereo_count(id_: str | int) -> int | None:
    """
    Get the number of stereo bonds (E/Z double bonds) in a compound.

    Counts double bonds with defined stereochemistry (cis/trans or E/Z).
    Important for understanding molecular geometry and reactivity.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of stereo bonds, or None if compound not found

    Examples:
        >>> get_bond_stereo_count("retinol")
        4
    """
    return _fetch_scalar(id_, "bond_stereo_count")

def get_covalent_unit_count(id_: str | int) -> int | None:
    """
    Get the number of covalently bonded units in a compound.

    For most organic molecules this is 1. Higher values indicate
    multiple separate molecular components or fragments.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        Number of covalent units, or None if compound not found

    Examples:
        >>> get_covalent_unit_count("aspirin")
        1
    """
    return _fetch_scalar(id_, "covalent_unit_count")

def get_inchi(id_: str | int) -> str | None:
    """
    Get the InChI (International Chemical Identifier) of a compound.

    InChI is a standardized string representation developed by IUPAC
    for uniquely identifying chemical substances across databases.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        InChI string, or None if compound not found

    Examples:
        >>> get_inchi("aspirin")
        'InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)'
    """
    return _fetch_scalar(id_, "in_ch_i")

def get_inchi_key(id_: str | int) -> str | None:
    """
    Get the InChI Key (hashed version of InChI) of a compound.

    InChI Key is a fixed-length (27 character) hash of the InChI,
    designed for database searching and web queries.

    Args:
        id_: Chemical identifier (name, CID, or SMILES)

    Returns:
        InChI Key string, or None if compound not found

    Examples:
        >>> get_inchi_key("aspirin")
        'BSYNRYMUTXBXSQ-UHFFFAOYSA-N'
    """
    return _fetch_scalar(id_, "in_ch_i_key")

def get_compound(identifier: str | int) -> Compound:
    """
    Retrieve a complete Compound object with all available properties.

    This function fetches all properties for a single compound and returns
    a structured Compound object with type validation and convenient access
    to all molecular data.

    Args:
        identifier: Chemical identifier (name, CID, or SMILES)

    Returns:
        Compound object with all available properties as attributes

    Raises:
        RuntimeError: If the compound cannot be found or data retrieval fails
        NotFoundError: If the identifier cannot be resolved
        AmbiguousIdentifierError: If the identifier matches multiple compounds

    Examples:
        >>> compound = get_compound("aspirin")
        >>> print(compound.MolecularWeight)
        180.16
        >>> print(compound.CanonicalSMILES)
        'CC(=O)OC1=CC=CC=C1C(=O)O'

    Note:
        This function uses CamelCase property names to match the Compound model.
        For DataFrame output with snake_case names, use get_properties() instead.
    """
    df = get_properties([identifier], all_properties=True)
    if df.empty or df["status"].iat[0] != "OK":
        raise RuntimeError(f"Failed to fetch compound for {identifier!r}")

    # Rename snake_case columns to CamelCase for Pydantic model validation
    df_renamed = df.rename(columns=SNAKE_TO_CAMEL)
    return Compound(**df_renamed.iloc[0].to_dict())

def get_compounds(identifiers: Iterable[str | int]) -> list[Compound]:
    """
    Retrieve multiple Compound objects for a list of identifiers.

    This function processes multiple chemical identifiers and returns
    a list of Compound objects. Failed lookups will raise exceptions.

    Args:
        identifiers: Iterable of chemical identifiers (names, CIDs, or SMILES)

    Returns:
        List of Compound objects in the same order as input identifiers

    Raises:
        RuntimeError: If any compound cannot be found or data retrieval fails
        NotFoundError: If any identifier cannot be resolved
        AmbiguousIdentifierError: If any identifier matches multiple compounds

    Examples:
        >>> compounds = get_compounds(["aspirin", "caffeine"])
        >>> for comp in compounds:
        ...     print(f"{comp.InputIdentifier}: {comp.MolecularWeight}")
        aspirin: 180.16
        caffeine: 194.19

    Note:
        For batch processing with error handling, consider using get_properties()
        which returns a DataFrame with status information for failed lookups.
    """
    return [get_compound(x) for x in identifiers]

def draw_compound(identifier: str | int):
    """
    Draw the 2D chemical structure of a compound.

    This function fetches the chemical structure image from PubChem and displays it
    using matplotlib. Requires matplotlib and PIL to be installed.

    Args:
        identifier: A compound identifier (name, CID, or SMILES)

    Raises:
        NotFoundError: If the identifier cannot be resolved to a valid compound
        ImportError: If required dependencies (matplotlib, PIL) are not installed
    """
    try:
        from io import BytesIO

        import matplotlib.pyplot as plt
        import requests
        from PIL import Image
    except ImportError as e:
        missing_lib = str(e).split("'")[1] if "'" in str(e) else str(e)
        print(f"Cannot render structure: missing dependency '{missing_lib}'", file=sys.stderr)
        print("Please install with: pip install ChemInformant[plot]", file=sys.stderr)
        return

    try:
        # Resolve identifier to CID
        cid = _resolve_to_single_cid(identifier)

        # Get compound name for title
        try:
            synonyms = api_helpers.get_synonyms_for_cid(cid)
            title = synonyms[0] if synonyms else f"CID {cid}"
        except Exception:
            title = f"CID {cid}"

        # Fetch structure image from PubChem
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        response = requests.get(image_url, timeout=10)

        if response.status_code != 200:
            print(f"Failed to fetch structure image for CID {cid}", file=sys.stderr)
            return

        # Open and display the image
        image = Image.open(BytesIO(response.content))

        plt.figure(figsize=(8, 6))
        plt.imshow(image)
        plt.axis('off')
        plt.title(title, fontsize=14, pad=20)
        plt.tight_layout()
        plt.show()

    except (NotFoundError, AmbiguousIdentifierError) as e:
        raise e
    except Exception as e:
        print(f"Error drawing compound: {e}", file=sys.stderr)
