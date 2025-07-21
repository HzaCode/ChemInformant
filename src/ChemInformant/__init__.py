"""
ChemInformant: A modern, robust, and workflow-centric Python client
for high-throughput access to the PubChem database.

This package provides high-level functions to retrieve chemical data,
seamlessly handling identifier conversion, batch processing, and network
robustness through built-in caching and retry mechanisms.
"""

from __future__ import annotations

# Re-export high-level API
from .cheminfo_api import (  # noqa: F401
    get_properties,
    get_compound,
    get_compounds,
    get_weight,
    get_formula,
    get_cas,
    get_iupac_name,
    get_canonical_smiles,
    get_isomeric_smiles,
    get_xlogp,
    get_synonyms,
    draw_compound,
)

# Cache setup
from .api_helpers import setup_cache  # noqa: F401

# Models and exceptions
from .models import Compound, NotFoundError, AmbiguousIdentifierError  # noqa: F401

from . import api_helpers  # noqa: F401

__all__ = [
    "get_properties",
    "get_compound",
    "get_compounds",
    "get_weight",
    "get_formula",
    "get_cas",
    "get_iupac_name",
    "get_canonical_smiles",
    "get_isomeric_smiles",
    "get_xlogp",
    "get_synonyms",
    "draw_compound",
    "setup_cache",
    "api_helpers",
    "Compound",
    "NotFoundError",
    "AmbiguousIdentifierError",
]
