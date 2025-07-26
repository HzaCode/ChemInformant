"""
This module defines the Pydantic data models and custom exceptions used
by ChemInformant to structure data and handle specific error states.
"""

from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, computed_field

# --- Custom Exceptions ---


class NotFoundError(Exception):
    """Raised when an identifier cannot be found in PubChem."""

    def __init__(self, identifier: Union[str, int]):
        super().__init__(f"Identifier '{identifier}' was not found in PubChem.")


class AmbiguousIdentifierError(Exception):
    """Raised when a name or SMILES string maps to multiple PubChem CIDs."""

    def __init__(self, identifier: str, cids: List[int]):
        msg = f"Identifier '{identifier}' maps to multiple CIDs: {cids}."
        super().__init__(msg)


# --- Data Models ---


class Compound(BaseModel):
    """
    A Pydantic model representing a chemical compound from PubChem.

    This class serves as a structured data container for the information
    retrieved from the API, providing type hints and validation.

    Attributes:
        cid: The unique PubChem Compound ID.
        input_identifier: The original identifier used for the query.
        molecular_formula: The molecular formula (e.g., "C8H10N4O2").
        molecular_weight: The molecular weight (g/mol).
        canonical_smiles: The canonical SMILES string.
        isomeric_smiles: The isomeric SMILES string.
        iupac_name: The IUPAC name.
        xlogp: The calculated XLogP value.
        cas: The primary CAS registry number.
        synonyms: A list of common names and synonyms.
        pubchem_url: A computed property with the direct link to the compound's
                     PubChem page.
    """

    cid: int
    input_identifier: Union[str, int]

    molecular_formula: Optional[str] = Field(None, alias="MolecularFormula")
    molecular_weight: Optional[float] = Field(None, alias="MolecularWeight")
    canonical_smiles: Optional[str] = Field(None, alias="CanonicalSMILES")
    isomeric_smiles: Optional[str] = Field(None, alias="IsomericSMILES")
    iupac_name: Optional[str] = Field(None, alias="IUPACName")
    xlogp: Optional[float] = Field(None, alias="XLogP")

    cas: Optional[str] = None
    description: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)

    @computed_field
    def pubchem_url(self) -> str:
        """Direct URL to the compound's page on the PubChem website."""
        return f"https://pubchem.ncbi.nlm.nih.gov/compound/{self.cid}"

    @field_validator("molecular_weight", "xlogp", mode="before")
    @classmethod
    def to_float(cls, v: Any):
        """Validator to safely convert string values to float."""
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    model_config = {"populate_by_name": True, "extra": "ignore"}
