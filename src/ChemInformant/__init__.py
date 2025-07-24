"""
ChemInformant: A modern, robust, and workflow-centric Python client
for high-throughput access to the PubChem database.

This package provides high-level functions to retrieve chemical data,
seamlessly handling identifier conversion, batch processing, and network
robustness through built-in caching and retry mechanisms.
"""
from __future__ import annotations

# Re-export high-level API
from .cheminfo_api import (
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

# --- NEW: Import the new SQL function ---
from .sql import df_to_sql

# Cache setup
from .api_helpers import setup_cache

# Models and exceptions
from .models import Compound, NotFoundError, AmbiguousIdentifierError

from . import api_helpers

# --- NEW: Add df_to_sql to the public API list ---
__all__ = [
# Core functions
"get_properties",
"get_compound",
"get_compounds",
# Scalar getters
"get_weight",
"get_formula",
"get_cas",
"get_iupac_name",
"get_canonical_smiles",
"get_isomeric_smiles",
"get_xlogp",
"get_synonyms",
# New persistence function
"df_to_sql",
# Utilities
"draw_compound",
"setup_cache",
# Objects and Exceptions
"api_helpers",
"Compound",
"NotFoundError",
"AmbiguousIdentifierError",
]
