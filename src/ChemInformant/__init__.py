"""
ChemInformant: A modern, robust, and workflow-centric Python client
for high-throughput access to the PubChem database.

This package provides high-level functions to retrieve chemical data,
seamlessly handling identifier conversion, batch processing, and network
robustness through built-in caching and retry mechanisms.

Key Features:
    - **Standardized snake_case properties**: All data returned in consistent format
    - **Intelligent fallbacks**: Automatic fallback for SMILES and other properties
    - **Batch processing**: Efficient retrieval of multiple compounds
    - **Smart caching**: Persistent caching to reduce API calls
    - **Error handling**: Robust handling of failed lookups and network issues
    - **SQL integration**: Direct export to databases via df_to_sql()
    - **Type safety**: Full type hints and Pydantic models
    - **CLI tools**: Command-line interface for quick data retrieval

Main Functions:
    - get_properties(): Core function for batch property retrieval
    - get_compound()/get_compounds(): Structured Compound objects
    - 22 convenience functions: get_weight(), get_formula(), etc.
    - draw_compound(): Visualization of chemical structures
    - setup_cache(): Configure persistent caching
    - df_to_sql(): Export data to SQL databases

See documentation for detailed usage examples and API reference.
"""

from __future__ import annotations

from . import api_helpers

# Cache setup
from .api_helpers import setup_cache

# Re-export high-level API
from .cheminfo_api import (
    draw_compound,
    get_atom_stereo_count,
    get_bond_stereo_count,
    get_canonical_smiles,
    get_cas,
    get_charge,
    get_complexity,
    get_compound,
    get_compounds,
    get_covalent_unit_count,
    get_exact_mass,
    get_formula,
    get_h_bond_acceptor_count,
    get_h_bond_donor_count,
    get_heavy_atom_count,
    get_inchi,
    get_inchi_key,
    get_isomeric_smiles,
    get_iupac_name,
    get_monoisotopic_mass,
    get_properties,
    get_rotatable_bond_count,
    get_synonyms,
    get_tpsa,
    get_weight,
    get_xlogp,
)

# Models and exceptions
from .models import AmbiguousIdentifierError, Compound, NotFoundError

# --- NEW: Import the new SQL function ---
from .sql import df_to_sql

# --- NEW: Add df_to_sql to the public API list ---
__all__ = [
    # Core functions
    "get_properties",
    "get_compound",
    "get_compounds",
    # Scalar getters - Basic properties
    "get_weight",
    "get_formula",
    "get_cas",
    "get_iupac_name",
    "get_canonical_smiles",
    "get_isomeric_smiles",
    "get_xlogp",
    "get_synonyms",
    # Scalar getters - Mass properties
    "get_exact_mass",
    "get_monoisotopic_mass",
    # Scalar getters - Molecular descriptors
    "get_tpsa",
    "get_complexity",
    "get_charge",
    # Scalar getters - Bond and atom counts
    "get_h_bond_donor_count",
    "get_h_bond_acceptor_count",
    "get_rotatable_bond_count",
    "get_heavy_atom_count",
    # Scalar getters - Stereochemistry
    "get_atom_stereo_count",
    "get_bond_stereo_count",
    "get_covalent_unit_count",
    # Scalar getters - Identifiers
    "get_inchi",
    "get_inchi_key",
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
