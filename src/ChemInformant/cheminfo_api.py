# src/ChemInformant/cheminfo_api.py
"""
Provides simple, cached, validated functions for retrieving chemical information
from PubChem, including ambiguity handling and batch retrieval.
"""
import sys
from typing import Optional, List, Union, Dict, Any, Tuple
import time  # For potential sleeps in batch
import requests  # Import requests to catch RequestException

# Use relative imports within the package
from . import api_helpers
from .models import CompoundData, NotFoundError, AmbiguousIdentifierError


# --- Internal Helper ---
def _resolve_identifier(identifier: Union[str, int]) -> Union[int, List[int]]:
    """
    Resolves an identifier (name or CID) to a PubChem CID or list of CIDs.

    Raises:
        NotFoundError: If the identifier cannot be found.
        AmbiguousIdentifierError: If a name maps to multiple CIDs (contains the list).
        ValueError: If an invalid integer CID (<1) is provided.
        TypeError: If the input type is incorrect.
    """
    if isinstance(identifier, int):
        if identifier > 0:
            return identifier
        else:
            raise ValueError(f"Invalid CID value provided: {identifier}")
    elif isinstance(identifier, str):
        cids = api_helpers.get_cids_by_name(identifier)
        if cids is None or len(cids) == 0:
            raise NotFoundError(identifier=identifier)
        elif len(cids) == 1:
            return cids[0]  # Unambiguous name
        else:
            raise AmbiguousIdentifierError(identifier=identifier, cids=cids)
    else:
        raise TypeError(
            f"Input must be a compound name (str) or CID (int), got {type(identifier)}"
        )


# --- Primary Single Compound Function ---
def info(name_or_cid: Union[str, int]) -> CompoundData:
    """
    Retrieves comprehensive, validated details for a single compound.
    Attempts to return partial data even if some underlying fetches fail.

    Args:
        name_or_cid: The compound name (str) or PubChem CID (int).

    Returns:
        CompoundData: A Pydantic model instance with the compound information.

    Raises:
        NotFoundError: If the compound identifier cannot be resolved initially.
        AmbiguousIdentifierError: If the name maps to multiple CIDs initially.
        ValueError: If an invalid CID (<1) is provided initially.
        TypeError: If the input type is incorrect initially.
        Exception: Potentially Pydantic validation errors if data is severely malformed.
    """
    resolved_id = _resolve_identifier(name_or_cid)  # Raises initial errors if needed

    if not isinstance(resolved_id, int):
        raise TypeError(f"Internal error: Expected single CID but got {resolved_id}")

    cid_val = resolved_id

    # --- Fetch components individually, handling potential errors for each ---
    cas_val, unii_val = None, None
    props = None
    description_val = None
    synonyms_val = None

    try:
        cas_val, unii_val = api_helpers.get_cas_unii(cid_val)
    except Exception as e:
        print(
            f"Warning: Failed to get CAS/UNII for CID {cid_val}: {type(e).__name__}",
            file=sys.stderr,
        )

    try:
        props = api_helpers.get_additional_properties(cid_val)
    except Exception as e:
        print(
            f"Warning: Failed to get additional properties for CID {cid_val}: {type(e).__name__}",
            file=sys.stderr,
        )

    try:
        description_val = api_helpers.get_compound_description(cid_val)
    except Exception as e:
        print(
            f"Warning: Failed to get description for CID {cid_val}: {type(e).__name__}",
            file=sys.stderr,
        )

    try:
        synonyms_val = api_helpers.get_all_synonyms(cid_val)
    except Exception as e:
        print(
            f"Warning: Failed to get synonyms for CID {cid_val}: {type(e).__name__}",
            file=sys.stderr,
        )
    # --- End of individual fetches ---

    # Determine common name using available data
    common_name = None
    if isinstance(name_or_cid, str):
        common_name = name_or_cid
    # Check if synonyms_val is a list and not None before accessing
    elif isinstance(synonyms_val, list) and synonyms_val:
        common_name = synonyms_val[0]
    # Check if props is a dict and not None before accessing
    elif isinstance(props, dict) and props.get("IUPACName"):
        common_name = props.get("IUPACName")

    # Prepare data dictionary, using fetched values or defaults (None/empty list)
    compound_dict = {
        "cid": cid_val,
        "input_identifier": name_or_cid,
        "common_name": common_name,
        "cas": cas_val,
        "unii": unii_val,
        "description": description_val,
        "synonyms": (
            synonyms_val if isinstance(synonyms_val, list) else []
        ),  # Ensure list
        **(props if isinstance(props, dict) else {}),  # Unpack properties dict if valid
    }

    # Validate and create Pydantic model
    try:
        # Pydantic will use the defaults (None) for fields if fetch failed
        model_instance = CompoundData(**compound_dict)
        return model_instance
    except Exception as e:  # Catch Pydantic validation errors
        print(
            f"Error: Failed to create CompoundData model for CID {cid_val} from dict {compound_dict}: {e}",
            file=sys.stderr,
        )
        raise  # Re-raise Pydantic validation errors as they indicate critical data issues


# --- Convenience Functions for Specific Properties ---
# (These remain unchanged as they rely on info() which now handles internal errors)


def cid(name_or_cid: Union[str, int]) -> Optional[int]:
    """Gets the PubChem CID. Returns single CID if unambiguous, None otherwise or if not found."""
    try:
        resolved_id = _resolve_identifier(name_or_cid)
        return resolved_id if isinstance(resolved_id, int) else None
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except (ValueError, TypeError):
        return None


def cas(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the CAS number. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).cas
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def unii(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the UNII code. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).unii
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def form(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the Molecular Formula. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).molecular_formula
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def wgt(name_or_cid: Union[str, int]) -> Optional[float]:
    """Gets the Molecular Weight as float. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).molecular_weight
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def smi(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the Canonical SMILES. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).canonical_smiles
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def iup(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the IUPAC Name. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).iupac_name
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def dsc(name_or_cid: Union[str, int]) -> Optional[str]:
    """Gets the description. Returns None if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).description
    except (NotFoundError, AmbiguousIdentifierError):
        return None
    except Exception:
        return None


def syn(name_or_cid: Union[str, int]) -> List[str]:
    """Gets the list of synonyms. Returns empty list ([]) if not found, ambiguous, or fetch failed."""
    try:
        return info(name_or_cid).synonyms
    except (NotFoundError, AmbiguousIdentifierError):
        return []
    except Exception:
        return []


# --- Batch Processing Function ---
# (Remains unchanged from the previous version, as its error handling relies on
# storing the exception in the results dict, which is appropriate for batch)
def get_multiple_compounds(
    identifiers: List[Union[str, int]],
) -> Dict[Union[str, int], Union[CompoundData, Exception]]:
    """
    Retrieves data for multiple compounds efficiently using batch requests where possible.

    Args:
        identifiers: A list of compound names (str) or PubChem CIDs (int).

    Returns:
        A dictionary where keys are the original identifiers from the input list,
        and values are either a CompoundData object upon success, or an Exception
        (NotFoundError, AmbiguousIdentifierError, ValueError, TypeError, etc.)
        indicating failure for that specific identifier.
    """
    if not identifiers:
        return {}
    results: Dict[Union[str, int], Union[CompoundData, Exception]] = {}
    resolution_results: List[Tuple[Union[str, int], Union[int, Exception]]] = []
    cids_to_fetch_details: set[int] = set()

    # Step 1: Resolve identifiers
    for identifier in identifiers:
        try:
            resolved_id = _resolve_identifier(identifier)
            if isinstance(resolved_id, int):
                resolution_results.append((identifier, resolved_id))
                cids_to_fetch_details.add(resolved_id)
            else:
                resolution_results.append(
                    (
                        identifier,
                        TypeError(f"Unexpected resolution result: {resolved_id}"),
                    )
                )
        except Exception as e:  # Catch NotFound, Ambiguous, ValueError, TypeError etc.
            resolution_results.append((identifier, e))

    unique_cids_to_fetch = list(cids_to_fetch_details)
    if not unique_cids_to_fetch:
        for original_id, error in resolution_results:
            if isinstance(error, Exception):
                results[original_id] = error
        return results

    # Step 2: Batch fetch data
    batch_props: Dict[int, Dict[str, Any]] = {}
    batch_synonyms: Dict[int, List[str]] = {}
    batch_descriptions: Dict[int, Optional[str]] = {}
    batch_fetch_error: Optional[Exception] = None
    try:
        batch_props_needed = [
            "MolecularFormula",
            "MolecularWeight",
            "CanonicalSMILES",
            "IUPACName",
        ]
        batch_props = api_helpers.get_batch_properties(
            unique_cids_to_fetch, batch_props_needed
        )
        batch_synonyms = api_helpers.get_batch_synonyms(unique_cids_to_fetch)
        batch_descriptions = api_helpers.get_batch_descriptions(unique_cids_to_fetch)
    except Exception as e:
        print(
            f"Error: Batch data fetch failed: {e}. Storing error for related identifiers.",
            file=sys.stderr,
        )
        batch_fetch_error = e

    # Step 3: Fetch individual data (CAS/UNII)
    individual_cas_unii: Dict[int, Tuple[Optional[str], Optional[str]]] = {}
    individual_fetch_errors: Dict[int, Exception] = {}
    if batch_fetch_error is None:
        for cid_val in unique_cids_to_fetch:
            try:
                time.sleep(0.05)
                individual_cas_unii[cid_val] = api_helpers.get_cas_unii(cid_val)
            except Exception as e:
                # print(f"Warning: Failed to get CAS/UNII for CID {cid_val}: {e}", file=sys.stderr)
                individual_fetch_errors[cid_val] = e

    # Step 4: Assemble results
    for original_id, resolved_result in resolution_results:
        if isinstance(resolved_result, int):  # Successfully resolved
            cid_val = resolved_result
            current_error: Optional[Exception] = None
            if batch_fetch_error:
                current_error = batch_fetch_error
            elif cid_val in individual_fetch_errors:
                current_error = individual_fetch_errors[cid_val]

            if current_error:
                results[original_id] = current_error
            else:
                props = batch_props.get(cid_val, {})
                synonyms = batch_synonyms.get(cid_val, [])
                description = batch_descriptions.get(cid_val)
                cas_val, unii_val = individual_cas_unii.get(cid_val, (None, None))

                common_name_batch = None
                if isinstance(original_id, str):
                    common_name_batch = original_id
                elif synonyms:
                    common_name_batch = synonyms[0]
                elif props and props.get("IUPACName"):
                    common_name_batch = props.get("IUPACName")

                compound_dict = {
                    "cid": cid_val,
                    "input_identifier": original_id,
                    "common_name": common_name_batch,
                    "cas": cas_val,
                    "unii": unii_val,
                    "description": description,
                    "synonyms": synonyms if synonyms is not None else [],
                    **(props if props else {}),
                }
                try:
                    results[original_id] = CompoundData(**compound_dict)
                except Exception as e:
                    # print(f"Error: Failed creating CompoundData for CID {cid_val} (from input {original_id}): {e}", file=sys.stderr)
                    results[original_id] = e  # Store Pydantic validation error
        elif isinstance(resolved_result, Exception):  # Resolution failed
            results[original_id] = resolved_result
        else:  # Should not happen
            results[original_id] = TypeError(
                f"Unknown resolution result type for {original_id}"
            )

    return results
