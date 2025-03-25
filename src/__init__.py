# src/__init__.py
"""
ChemInformant - A simplified API for retrieving chemical compound information from PubChem.
"""

from .cheminfo_api import ChemInfo

__all__ = ['ChemInfo']
__version__ = '1.0.0'