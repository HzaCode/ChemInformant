# src/cheminfo_api.py
import sys
import os

# Try to import api_helpers
try:
    # First try relative import
    from . import api_helpers
except ImportError:
    # If that fails, try absolute import based on file location
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import api_helpers

# Import required functions
from api_helpers import (
    get_cid_by_name,
    get_cas_unii,
    get_compound_description,
    get_all_synonyms,
    get_additional_details
)

class ChemInfo:
    """Simplified API for retrieving chemical compound information from PubChem."""
    
    @staticmethod
    def cid(name_or_cid):
        """Get the PubChem Compound ID (CID) for a chemical compound."""
        if isinstance(name_or_cid, int):
            return name_or_cid
        result = get_cid_by_name(name_or_cid)
        # Explicitly return "Not found" instead of None for consistency
        if result is None:
            return "Not found"
        return result

    @staticmethod
    def cas(name_or_cid):
        """Get the CAS Registry Number for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            cas, _ = get_cas_unii(cid)
            return cas
        return "Not found"

    @staticmethod
    def uni(name_or_cid):
        """Get the UNII code for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            _, unii = get_cas_unii(cid)
            return unii
        return "Not found"

    @staticmethod
    def form(name_or_cid):
        """Get the molecular formula for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            props = get_additional_details(cid)
            return props.get('MolecularFormula', 'N/A')
        return "N/A"

    @staticmethod
    def wgt(name_or_cid):
        """Get the molecular weight for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            props = get_additional_details(cid)
            return props.get('MolecularWeight', 'N/A')
        return "N/A"

    @staticmethod
    def smi(name_or_cid):
        """Get the SMILES notation for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            props = get_additional_details(cid)
            return props.get('CanonicalSMILES', 'N/A')
        return "N/A"

    @staticmethod
    def iup(name_or_cid):
        """Get the IUPAC name for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            props = get_additional_details(cid)
            return props.get('IUPACName', 'N/A')
        return "N/A"

    @staticmethod
    def dsc(name_or_cid):
        """Get the description for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            return get_compound_description(cid)
        return "No description available"

    @staticmethod
    def syn(name_or_cid):
        """Get the synonyms for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if cid:
            return get_all_synonyms(cid)
        return []

    @staticmethod
    def all(name_or_cid):
        """Get all available information for a chemical compound."""
        cid = ChemInfo.cid(name_or_cid)
        if not cid:
            return {"Error": "Compound not found"}
        
        cas, unii = get_cas_unii(cid)
        props = get_additional_details(cid)
        
        return {
            "Common Name": str(name_or_cid) if isinstance(name_or_cid, str) else "N/A",
            "CID": cid,
            "CAS": cas,
            "UNII": unii,
            "MolecularFormula": props.get('MolecularFormula', 'N/A'),
            "MolecularWeight": props.get('MolecularWeight', 'N/A'),
            "CanonicalSMILES": props.get('CanonicalSMILES', 'N/A'),
            "IUPACName": props.get('IUPACName', 'N/A'),
            "Description": get_compound_description(cid),
            "Synonyms": get_all_synonyms(cid)
        }
    
    # Legacy method names as aliases for backward compatibility
    CID = cid
    CAS = cas
    UNII = uni
    formula = form
    weight = wgt
    smiles = smi
    iupac_name = iup
    description = dsc
    synonyms = syn