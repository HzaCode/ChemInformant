
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, computed_field

class NotFoundError(Exception):
    def __init__(self, identifier: Union[str, int]):
        super().__init__(f"Identifier '{identifier}' was not found in PubChem.")

class AmbiguousIdentifierError(Exception):
    def __init__(self, identifier: str, cids: List[int]):
        msg = f"Identifier '{identifier}' maps to multiple CIDs: {cids}."
        super().__init__(msg)

class Compound(BaseModel):
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
        return f"https://pubchem.ncbi.nlm.nih.gov/compound/{self.cid}"

    @field_validator("molecular_weight", "xlogp", mode="before")
    @classmethod
    def to_float(cls, v: Any):
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    model_config = {"populate_by_name": True, "extra": "ignore"}
