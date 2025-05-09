"""Tests for Pydantic models and custom exceptions."""

from ChemInformant.models import (
    CompoundData,
    NotFoundError,
    AmbiguousIdentifierError,
)


CID = 2244
NAME = "Aspirin"
CAS = "50-78-2"
UNII = "R16CO5Y76E"
FORMULA = "C9H8O4"
WEIGHT_STR = "180.157"
WEIGHT_FLOAT = 180.157
SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"
IUPAC = "2-Acetoxybenzoic acid"
DESC = "A common pain reliever."
SYNONYMS = ["Aspirin", "Acetylsalicylic acid"]
EXPECTED_URL = f"https://pubchem.ncbi.nlm.nih.gov/compound/{CID}"


def test_not_found_error():
    err_name = NotFoundError(NAME)
    assert err_name.identifier == NAME
    assert f"Identifier '{NAME}' not found" in str(err_name)

    err_cid = NotFoundError(CID)
    assert err_cid.identifier == CID
    assert f"Identifier '{CID}' not found" in str(err_cid)


def test_ambiguous_identifier_error():
    cids = [1001, 1002]
    err = AmbiguousIdentifierError(NAME, cids)
    assert err.identifier == NAME
    assert err.cids == cids
    assert f"Identifier '{NAME}' is ambiguous" in str(err)
    assert str(cids) in str(err)


def test_compound_data_creation_full():
    data = {
        "cid": CID,
        "input_identifier": NAME,
        "common_name": NAME,
        "cas": CAS,
        "unii": UNII,
        "MolecularFormula": FORMULA,
        "MolecularWeight": WEIGHT_STR,
        "CanonicalSMILES": SMILES,
        "IUPACName": IUPAC,
        "description": DESC,
        "synonyms": SYNONYMS,
    }
    compound = CompoundData(**data)

    assert compound.cid == CID
    assert compound.input_identifier == NAME
    assert compound.common_name == NAME
    assert compound.cas == CAS
    assert compound.unii == UNII
    assert compound.molecular_formula == FORMULA
    assert compound.molecular_weight == WEIGHT_FLOAT
    assert compound.canonical_smiles == SMILES
    assert compound.iupac_name == IUPAC
    assert compound.description == DESC
    assert compound.synonyms == SYNONYMS

    assert isinstance(compound.pubchem_url, str)
    assert compound.pubchem_url == EXPECTED_URL


def test_compound_data_creation_minimal():

    data = {"cid": CID, "input_identifier": CID}
    compound = CompoundData(**data)

    assert compound.cid == CID
    assert compound.input_identifier == CID
    assert compound.common_name is None
    assert compound.cas is None
    assert compound.unii is None
    assert compound.molecular_formula is None
    assert compound.molecular_weight is None
    assert compound.canonical_smiles is None
    assert compound.iupac_name is None
    assert compound.description is None
    assert compound.synonyms == []

    assert isinstance(compound.pubchem_url, str)
    assert compound.pubchem_url == EXPECTED_URL


def test_compound_data_weight_validator():

    c1 = CompoundData(cid=1, input_identifier=1, MolecularWeight="123.45")
    assert c1.molecular_weight == 123.45

    c2 = CompoundData(cid=1, input_identifier=1, MolecularWeight=123.45)
    assert c2.molecular_weight == 123.45

    c3 = CompoundData(cid=1, input_identifier=1, MolecularWeight=None)
    assert c3.molecular_weight is None

    c4 = CompoundData(cid=1, input_identifier=1, MolecularWeight="")
    assert c4.molecular_weight is None

    c5 = CompoundData(cid=1, input_identifier=1, MolecularWeight="N/A")
    assert c5.molecular_weight is None

    c6 = CompoundData(cid=1, input_identifier=1, MolecularWeight="invalid")
    assert c6.molecular_weight is None

    c7 = CompoundData(cid=1, input_identifier=1, MolecularWeight=["123"])
    assert c7.molecular_weight is None


def test_compound_data_pubchem_url_computed():

    compound = CompoundData(cid=CID, input_identifier=NAME)

    assert isinstance(compound.pubchem_url, str)
    assert compound.pubchem_url == EXPECTED_URL


def test_compound_data_model_copy():

    compound = CompoundData(
        cid=CID, input_identifier=NAME, cas=CAS, synonyms=SYNONYMS.copy()
    )

    copy1 = compound.model_copy()
    assert copy1 is not compound
    assert copy1.cid == compound.cid
    assert copy1.cas == compound.cas
    assert copy1.synonyms is compound.synonyms

    copy2 = compound.model_copy(deep=True)
    assert copy2 is not compound
    assert copy2.cid == compound.cid
    assert copy2.cas == compound.cas
    assert copy2.synonyms == compound.synonyms
    assert copy2.synonyms is not compound.synonyms

    copy3 = compound.model_copy(update={"cas": "NEW-CAS", "description": "New Desc"})
    assert copy3 is not compound
    assert copy3.cid == compound.cid
    assert copy3.cas == "NEW-CAS"
    assert copy3.unii is None
    assert copy3.description == "New Desc"
    assert compound.cas == CAS
    assert compound.description is None


def test_compound_data_extra_fields_ignored():

    data = {
        "cid": CID,
        "input_identifier": NAME,
        "extra_field": "should be ignored",
        "another": 123,
    }
    compound = CompoundData(**data)
    assert compound.cid == CID
    assert not hasattr(compound, "extra_field")
    assert not hasattr(compound, "another")


def test_compound_data_model_copy_with_none_update():
    # 测试当update参数为None时的情况，确保代码中的update=update or {}处理被覆盖
    compound = CompoundData(cid=CID, input_identifier=NAME, cas=CAS)

    # 显式传递None作为update参数
    copy1 = compound.model_copy(update=None)
    assert copy1 is not compound
    assert copy1.cid == compound.cid
    assert copy1.cas == compound.cas

    # 传递None并同时设置deep=True
    copy2 = compound.model_copy(update=None, deep=True)
    assert copy2 is not compound
    assert copy2.cid == compound.cid
    assert copy2.cas == compound.cas
