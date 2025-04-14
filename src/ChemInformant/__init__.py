# src/ChemInformant/__init__.py
"""
ChemInformant: A Python client for easily retrieving cached, validated
chemical information from PubChem, with ambiguity handling and batch support.
"""

# Import core functions from cheminfo_api module
from .cheminfo_api import (
    info,
    cid,
    cas,
    unii,
    form,
    wgt,
    smi,
    iup,
    dsc,
    syn,
    get_multiple_compounds,
)
# Import specific exceptions and the data model from models module
from .models import CompoundData, NotFoundError, AmbiguousIdentifierError

# Import the cache configuration function *from* api_helpers module
# This makes setup_cache available at the package level (ChemInformant.setup_cache)
from .api_helpers import setup_cache

__version__ = "1.1.4" # Keep consistent with pyproject.toml

# Define what gets imported with 'from ChemInformant import *'
# Include setup_cache here
__all__ = [
    # Single item functions
    'info', 'cid', 'cas', 'unii', 'form', 'wgt', 'smi', 'iup', 'dsc', 'syn',
    # Batch function
    'get_multiple_compounds',
    # Models and Errors
    'CompoundData', 'NotFoundError', 'AmbiguousIdentifierError',
    # Cache utility (now imported from api_helpers)
    'setup_cache',
    # Version is useful too
    '__version__',
]

# Note: get_session is now an internal implementation detail within api_helpers
# and is not (and should not be) exposed directly to the user here.