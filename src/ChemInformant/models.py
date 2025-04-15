# src/ChemInformant/models.py
"""
Pydantic models for representing chemical compound data retrieved from PubChem,
and custom exceptions.
"""

from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, HttpUrl, field_validator, computed_field

# ---------------------------------


# --- Custom Exceptions ---
class NotFoundError(Exception):
    """Custom exception for when a compound identifier cannot be found."""

    def __init__(self, identifier: Union[str, int]):
        self.identifier = identifier
        super().__init__(f"Identifier '{identifier}' not found in PubChem.")


class AmbiguousIdentifierError(Exception):
    """Custom exception for when a name maps to multiple CIDs."""

    def __init__(self, identifier: str, cids: List[int]):
        self.identifier = identifier
        self.cids = cids
        super().__init__(
            f"Identifier '{identifier}' is ambiguous and maps to multiple CIDs: {cids}. Please query using a specific CID."
        )


# --- Data Model ---
class CompoundData(BaseModel):
    """
    Represents structured information for a chemical compound.
    """

    cid: int = Field(..., description="PubChem Compound ID.")
    input_identifier: Union[str, int] = Field(
        ..., description="The name or CID used for the lookup."
    )
    common_name: Optional[str] = Field(
        None, description="A common name (often the first synonym or input name)."
    )
    cas: Optional[str] = Field(None, description="CAS Registry Number.")
    unii: Optional[str] = Field(
        None, description="FDA Unique Ingredient Identifier (UNII)."
    )
    molecular_formula: Optional[str] = Field(
        None, alias="MolecularFormula", description="Molecular formula."
    )
    molecular_weight: Optional[float] = Field(
        None, alias="MolecularWeight", description="Molecular weight (as float)."
    )
    canonical_smiles: Optional[str] = Field(
        None, alias="CanonicalSMILES", description="Canonical SMILES string."
    )
    iupac_name: Optional[str] = Field(
        None, alias="IUPACName", description="IUPAC systematic name."
    )
    description: Optional[str] = Field(None, description="Compound description text.")
    synonyms: List[str] = Field(default_factory=list, description="List of synonyms.")
    # pubchem_url is now a computed field, removed from direct definition

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
        "frozen": False,
        "computed_fields": [
            "pubchem_url"
        ],  # Declare computed field for older Pydantic v2 versions if needed
    }

    @field_validator("molecular_weight", mode="before")
    @classmethod
    def weight_to_float(cls, v: Any) -> Optional[float]:
        """Attempt to convert molecular weight string to float."""
        if v is None or v == "N/A" or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    # --- Use computed_field for pubchem_url ---
    @computed_field
    @property
    def pubchem_url(self) -> Optional[HttpUrl]:
        """Direct URL to the PubChem compound page, computed from CID."""
        if self.cid:
            try:
                # Pydantic will validate the URL format implicitly when returning HttpUrl
                return f"https://pubchem.ncbi.nlm.nih.gov/compound/{self.cid}"
            except Exception:  # Catch potential errors during URL creation/validation
                return None
        return None

    # ------------------------------------------

    # Pydantic v2 uses model_copy
    def model_copy(
        self: "CompoundData",
        *,
        update: Optional[Dict[str, Any]] = None,
        deep: bool = False,
    ) -> "CompoundData":
        return super().model_copy(update=update or {}, deep=deep)
