# src/ChemInformant/__init__.py
"""
ChemInformant: A Python client for easily retrieving cached, validated
chemical information from PubChem, with ambiguity handling and batch support.
"""

from typing import Union  # For setup_cache type hint
from datetime import timedelta  # For setup_cache type hint

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
    fig,
)

# Import specific exceptions and the data model from models module
from .models import CompoundData, NotFoundError, AmbiguousIdentifierError

# Import the api_helpers module to access its functions and constants
from . import api_helpers  # Changed to import the module itself

# Make setup_cache available at the package level (ChemInformant.setup_cache)
# and also DEFAULT constants for the wrapper.
from .api_helpers import (
    DEFAULT_CACHE_NAME,
    DEFAULT_CACHE_BACKEND,
    DEFAULT_CACHE_EXPIRE_AFTER
)

__version__ = "1.2.0"  # Keep consistent with pyproject.toml

# Define what gets imported with 'from ChemInformant import *'
# Include setup_cache here
__all__ = [
    # Single item functions
    "info",  # No trailing whitespace
    "cid",
    "cas",
    "unii",
    "form",
    "wgt",
    "smi",
    "iup",
    "dsc",
    "syn",
    "fig",
    # Batch function
    "get_multiple_compounds",
    # Models and Errors
    "CompoundData",
    "NotFoundError",
    "AmbiguousIdentifierError",
    # Cache utility
    "setup_cache",  # Expose the wrapper
    # Version is useful too
    "__version__",
]

# Note: get_session is now an internal implementation detail within api_helpers
# and is not (and should not be) exposed directly to the user here.

# --- Setup Cache (wrapper around api_helpers.setup_cache) ---
# This allows users to import setup_cache directly from ChemInformant


def setup_cache(
    cache_name: str = DEFAULT_CACHE_NAME,
    backend: str = DEFAULT_CACHE_BACKEND,
    expire_after: Union[int, float, None, timedelta] = DEFAULT_CACHE_EXPIRE_AFTER,
    **kwargs,
):
    """
    Configures the cache used for PubChem API requests.

    This is a wrapper around the an internal cache setup function.
    Call this function *before* making any ChemInformant API calls if you
    want to use non-default cache settings.

    Args:
        cache_name (str): Name of the cache file/db.
        backend (str): Cache backend ('sqlite', 'memory', etc.).
        expire_after (int | float | None | timedelta): Expiration time in seconds.
        **kwargs: Additional backend arguments for requests_cache.CachedSession.
    """
    # Call the original setup_cache from api_helpers
    api_helpers.setup_cache(  # Call the one in api_helpers directly
        cache_name=cache_name, backend=backend, expire_after=expire_after, **kwargs
    )


# Ensure a default session is created if setup_cache hasn't been called explicitly by the user
# This is primarily for convenience if a user forgets to call setup_cache().
# It will initialize with default settings.
# Accessing _session directly is okay here as it's part of initializing the library's default state.
if api_helpers._session is None:
    # print("ChemInformant __init__: No session found, initializing default cache...") # Optional: for debugging
    setup_cache()  # Call the wrapper defined in this file
