# tests/test_api.py
"""
Comprehensive tests for ChemInformant API functions using pytest and pytest-mock.
These tests DO NOT hit the live PubChem API. Focus on cheminfo_api.py logic.
"""

import sys
import pytest
import requests # Import requests to test for potential RequestException propagation
import requests_cache # Import for testing setup_cache effect
from pydantic import HttpUrl # Keep import, but assertions might change
from unittest.mock import MagicMock, patch # Used with pytest-mock

# Import functions and classes to be tested
from ChemInformant import (
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
    setup_cache, # Import setup_cache
    CompoundData,
    NotFoundError,
    AmbiguousIdentifierError,
)
# Import specific exceptions potentially raised by helpers
from requests.exceptions import ConnectionError, Timeout, HTTPError

# --- Constants for Mocking ---
MOCK_CID_ASPIRIN = 2244
MOCK_CID_ETHANOL = 702
MOCK_CID_WATER = 962
MOCK_CID_AMBIGUOUS_1 = 1001
MOCK_CID_AMBIGUOUS_2 = 1002
MOCK_CID_NO_CAS = 1003
MOCK_CID_NO_WEIGHT = 1004
MOCK_CID_FETCH_ERROR_CAS_UNII = 1005
MOCK_CID_FETCH_ERROR_PROPS = 1006
MOCK_CID_FETCH_ERROR_DESC = 1007
MOCK_CID_FETCH_ERROR_SYN = 1008
MOCK_CID_INVALID_DATA = 1009

MOCK_NAME_ASPIRIN = "Aspirin"
MOCK_NAME_ETHANOL = "Ethanol"
MOCK_NAME_WATER = "Water"
MOCK_NAME_AMBIGUOUS = "AmbiguousDrug"
MOCK_NAME_NOTFOUND = "NotFoundCompound"
MOCK_NAME_NOCAS = "NoCasCompound"
MOCK_NAME_NOWEIGHT = "NoWeightCompound"
MOCK_NAME_FETCH_ERROR_CAS_UNII = "FetchErrorCasUniiCompound"
MOCK_NAME_FETCH_ERROR_PROPS = "FetchErrorPropsCompound"
MOCK_NAME_FETCH_ERROR_DESC = "FetchErrorDescCompound"
MOCK_NAME_FETCH_ERROR_SYN = "FetchErrorSynCompound"
MOCK_NAME_INVALID_DATA = "InvalidDataCompound"
EXPECTED_ASPIRIN_URL = f"https://pubchem.ncbi.nlm.nih.gov/compound/{MOCK_CID_ASPIRIN}"


# --- Fixtures for Mocking API Helpers ---
# (Fixture definition remains the same as provided in the previous step)
@pytest.fixture
def mock_api_helpers(mocker):
    """Mocks all necessary functions in the api_helpers module."""
    mock_obj = MagicMock()
    # 1. Identifier Resolution Mock
    mock_obj.get_cids_by_name.side_effect = lambda name: {
        MOCK_NAME_ASPIRIN: [MOCK_CID_ASPIRIN], MOCK_NAME_ETHANOL: [MOCK_CID_ETHANOL],
        MOCK_NAME_WATER: [MOCK_CID_WATER], MOCK_NAME_AMBIGUOUS: [MOCK_CID_AMBIGUOUS_1, MOCK_CID_AMBIGUOUS_2],
        MOCK_NAME_NOCAS: [MOCK_CID_NO_CAS], MOCK_NAME_NOWEIGHT: [MOCK_CID_NO_WEIGHT],
        MOCK_NAME_FETCH_ERROR_CAS_UNII: [MOCK_CID_FETCH_ERROR_CAS_UNII], MOCK_NAME_FETCH_ERROR_PROPS: [MOCK_CID_FETCH_ERROR_PROPS],
        MOCK_NAME_FETCH_ERROR_DESC: [MOCK_CID_FETCH_ERROR_DESC], MOCK_NAME_FETCH_ERROR_SYN: [MOCK_CID_FETCH_ERROR_SYN],
        MOCK_NAME_INVALID_DATA: [MOCK_CID_INVALID_DATA],
    }.get(name, None)
    # 2. Individual Fetch Mocks
    mock_obj.cas_unii_data = {
        MOCK_CID_ASPIRIN: ("50-78-2", "ASPIRIN_UNII"), MOCK_CID_ETHANOL: ("64-17-5", "ETHANOL_UNII"),
        MOCK_CID_WATER: (None, "WATER_UNII"), MOCK_CID_NO_CAS: (None, "NOCAS_UNII"),
        MOCK_CID_NO_WEIGHT: ("NOWEIGHT_CAS", "NOWEIGHT_UNII"), MOCK_CID_AMBIGUOUS_1: ("CAS_AMBIG1", "UNII_AMBIG1"),
        MOCK_CID_AMBIGUOUS_2: ("CAS_AMBIG2", "UNII_AMBIG2"), MOCK_CID_FETCH_ERROR_PROPS: ("OK_CAS", "OK_UNII"),
        MOCK_CID_FETCH_ERROR_DESC: ("OK_CAS", "OK_UNII"), MOCK_CID_FETCH_ERROR_SYN: ("OK_CAS", "OK_UNII"),
        MOCK_CID_INVALID_DATA: ("OK_CAS", "OK_UNII"),
    }
    mock_obj.additional_properties_data = {
        MOCK_CID_ASPIRIN: {"MolecularFormula": "C9H8O4", "MolecularWeight": "180.16", "CanonicalSMILES": "SMILES_ASP", "IUPACName": "IUPAC_ASP"},
        MOCK_CID_ETHANOL: {"MolecularFormula": "C2H6O", "MolecularWeight": "46.07", "CanonicalSMILES": "SMILES_ETH", "IUPACName": "IUPAC_ETH"},
        MOCK_CID_WATER: {"MolecularFormula": "H2O", "MolecularWeight": "18.015", "CanonicalSMILES": "O", "IUPACName": "water"},
        MOCK_CID_NO_CAS: {"MolecularFormula": "F_NOCAS", "MolecularWeight": "100.0", "CanonicalSMILES": "S_NOCAS", "IUPACName": "I_NOCAS"},
        MOCK_CID_NO_WEIGHT: {"MolecularFormula": "F_NOWEIGHT", "MolecularWeight": None, "CanonicalSMILES": "S_NOWEIGHT", "IUPACName": "I_NOWEIGHT"},
        MOCK_CID_AMBIGUOUS_1: {"MolecularFormula": "F_AMBIG1", "MolecularWeight": "1.0", "CanonicalSMILES": "S_AMBIG1", "IUPACName": "I_AMBIG1"},
        MOCK_CID_AMBIGUOUS_2: {"MolecularFormula": "F_AMBIG2", "MolecularWeight": "2.0", "CanonicalSMILES": "S_AMBIG2", "IUPACName": "I_AMBIG2"},
        MOCK_CID_FETCH_ERROR_CAS_UNII: {"MolecularFormula": "OK_F", "MolecularWeight": "1.0", "CanonicalSMILES": "OK_S", "IUPACName": "OK_I"},
        MOCK_CID_FETCH_ERROR_DESC: {"MolecularFormula": "OK_F", "MolecularWeight": "1.0", "CanonicalSMILES": "OK_S", "IUPACName": "OK_I"},
        MOCK_CID_FETCH_ERROR_SYN: {"MolecularFormula": "OK_F", "MolecularWeight": "1.0", "CanonicalSMILES": "OK_S", "IUPACName": "OK_I"},
        MOCK_CID_INVALID_DATA: {"MolecularFormula": "OK_F", "MolecularWeight": "SHOULD_BE_FLOAT", "CanonicalSMILES": "OK_S", "IUPACName": "OK_I"},
    }
    mock_obj.description_data = {
        MOCK_CID_ASPIRIN: "Aspirin description.", MOCK_CID_ETHANOL: "Ethanol description.", MOCK_CID_WATER: None,
        MOCK_CID_NO_CAS: "No CAS description.", MOCK_CID_NO_WEIGHT: "No Weight description.", MOCK_CID_AMBIGUOUS_1: "Desc Ambiguous 1",
        MOCK_CID_AMBIGUOUS_2: "Desc Ambiguous 2", MOCK_CID_FETCH_ERROR_CAS_UNII: "OK_DESC", MOCK_CID_FETCH_ERROR_PROPS: "OK_DESC",
        MOCK_CID_FETCH_ERROR_SYN: "OK_DESC", MOCK_CID_INVALID_DATA: "OK_DESC",
    }
    mock_obj.synonyms_data = {
        MOCK_CID_ASPIRIN: ["Aspirin", "Synonym A"], MOCK_CID_ETHANOL: ["Ethanol", "Synonym B"], MOCK_CID_WATER: ["Water", "H2O"],
        MOCK_CID_NO_CAS: ["NoCasCompound"], MOCK_CID_NO_WEIGHT: ["NoWeightCompound"], MOCK_CID_AMBIGUOUS_1: ["AmbiguousDrug", "Syn C"],
        MOCK_CID_AMBIGUOUS_2: ["AmbiguousDrug", "Syn D"], MOCK_CID_FETCH_ERROR_CAS_UNII: ["OK_SYN"], MOCK_CID_FETCH_ERROR_PROPS: ["OK_SYN"],
        MOCK_CID_FETCH_ERROR_DESC: ["OK_SYN"], MOCK_CID_INVALID_DATA: ["OK_SYN"],
    }
    # 3. Default Side Effects
    mock_obj.get_cas_unii.side_effect = lambda cid_val: mock_obj.cas_unii_data.get(cid_val, (None, None))
    mock_obj.get_additional_properties.side_effect = lambda cid_val: mock_obj.additional_properties_data.get(cid_val, {"MolecularFormula": None, "MolecularWeight": None, "CanonicalSMILES": None, "IUPACName": None})
    mock_obj.get_compound_description.side_effect = lambda cid_val: mock_obj.description_data.get(cid_val, None)
    mock_obj.get_all_synonyms.side_effect = lambda cid_val: mock_obj.synonyms_data.get(cid_val, [])
    # 4. Batch Fetch Mocks
    mock_obj.get_batch_properties.side_effect = lambda cids, props: { cid: mock_obj.get_additional_properties(cid) for cid in cids }
    mock_obj.get_batch_synonyms.side_effect = lambda cids: { cid: mock_obj.get_all_synonyms(cid) for cid in cids }
    mock_obj.get_batch_descriptions.side_effect = lambda cids: { cid: mock_obj.get_compound_description(cid) for cid in cids }
    # --- Apply the patch ---
    mocker.patch("ChemInformant.cheminfo_api.api_helpers", new=mock_obj)
    return mock_obj

# --- Test Imports and Basic Setup ---
def test_imports():
    assert callable(info); assert callable(cid); assert callable(cas); assert callable(unii)
    assert callable(form); assert callable(wgt); assert callable(smi); assert callable(iup)
    assert callable(dsc); assert callable(syn); assert callable(get_multiple_compounds)
    assert callable(setup_cache); assert CompoundData is not None
    assert NotFoundError is not None; assert AmbiguousIdentifierError is not None

# --- Tests for setup_cache ---
# --- MODIFIED TEST ---
def test_setup_cache_callable(mocker):
    """Test that setup_cache calls requests_cache.CachedSession."""
    # Patch the actual CachedSession used internally by api_helpers.setup_cache
    mock_cached_session = mocker.patch("requests_cache.CachedSession")
    # Call the setup_cache function exposed at the package level
    setup_cache(cache_name="test_cache", backend="memory", expire_after=300, custom_arg="test")
    # Assert that CachedSession was initialized with the correct arguments
    mock_cached_session.assert_called_once_with(
        cache_name="test_cache", backend="memory", expire_after=300,
        allowable_codes=[200, 404], match_headers=False, custom_arg="test"
    )

# --- Tests for info() ---
# --- MODIFIED TEST ---
def test_info_success_by_name(mock_api_helpers):
    compound = info(MOCK_NAME_ASPIRIN)
    assert isinstance(compound, CompoundData)
    assert compound.cid == MOCK_CID_ASPIRIN
    assert compound.input_identifier == MOCK_NAME_ASPIRIN
    assert compound.cas == "50-78-2"
    assert compound.unii == "ASPIRIN_UNII"
    assert compound.molecular_formula == "C9H8O4"
    assert compound.molecular_weight == 180.16
    assert compound.canonical_smiles == "SMILES_ASP"
    assert compound.iupac_name == "IUPAC_ASP"
    assert compound.description == "Aspirin description."
    assert compound.synonyms == ["Aspirin", "Synonym A"] # Assumes raw synonyms
    assert compound.common_name == MOCK_NAME_ASPIRIN
    # Assert pubchem_url is a string based on test_models results
    assert isinstance(compound.pubchem_url, str)
    assert compound.pubchem_url == EXPECTED_ASPIRIN_URL

# (Other info tests remain the same as the previous corrected version)
def test_info_success_by_cid(mock_api_helpers):
    compound = info(MOCK_CID_ETHANOL); assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_ETHANOL
    assert compound.input_identifier == MOCK_CID_ETHANOL; assert compound.cas == "64-17-5"; assert compound.molecular_formula == "C2H6O"
    assert compound.common_name == "Ethanol" # First synonym
def test_info_success_partial_data_water(mock_api_helpers):
    compound = info(MOCK_CID_WATER); assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_WATER
    assert compound.cas is None; assert compound.unii == "WATER_UNII"; assert compound.molecular_formula == "H2O"
    assert compound.molecular_weight == 18.015; assert compound.description is None; assert compound.synonyms == ["Water", "H2O"]
    assert compound.common_name == "Water"
def test_info_success_explicit_none_weight(mock_api_helpers):
    compound = info(MOCK_CID_NO_WEIGHT); assert isinstance(compound, CompoundData); assert compound.molecular_weight is None
def test_info_not_found(mock_api_helpers):
    with pytest.raises(NotFoundError) as excinfo: info(MOCK_NAME_NOTFOUND)
    assert MOCK_NAME_NOTFOUND in str(excinfo.value); mock_api_helpers.get_cids_by_name.assert_called_with(MOCK_NAME_NOTFOUND)
def test_info_ambiguous_name(mock_api_helpers):
    with pytest.raises(AmbiguousIdentifierError) as excinfo: info(MOCK_NAME_AMBIGUOUS)
    assert MOCK_NAME_AMBIGUOUS in str(excinfo.value); assert excinfo.value.identifier == MOCK_NAME_AMBIGUOUS
    assert excinfo.value.cids == [MOCK_CID_AMBIGUOUS_1, MOCK_CID_AMBIGUOUS_2]; mock_api_helpers.get_cids_by_name.assert_called_with(MOCK_NAME_AMBIGUOUS)
def test_info_invalid_cid_input(mock_api_helpers):
    with pytest.raises(ValueError, match="Invalid CID value provided"): info(0)
    with pytest.raises(ValueError, match="Invalid CID value provided"): info(-1)
def test_info_invalid_type_input(mock_api_helpers):
    with pytest.raises(TypeError, match="Input must be a compound name"): info(None)
    with pytest.raises(TypeError, match="Input must be a compound name"): info([MOCK_CID_ASPIRIN])

# --- Tests for info() error handling within helpers ---
# (These remain the same as the previous corrected version)
def test_info_helper_fetch_error_cas_unii(mock_api_helpers, capsys):
    original_side_effect = mock_api_helpers.get_cas_unii.side_effect
    expected_exception = KeyError("Simulated fetch error for CAS/UNII")
    def side_effect(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR_CAS_UNII: raise expected_exception
        return mock_api_helpers.cas_unii_data.get(cid_val, (None, None))
    mock_api_helpers.get_cas_unii.side_effect = side_effect
    compound = info(MOCK_NAME_FETCH_ERROR_CAS_UNII); captured = capsys.readouterr()
    assert f"Warning: Failed to get CAS/UNII for CID {MOCK_CID_FETCH_ERROR_CAS_UNII}: KeyError" in captured.err
    assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_FETCH_ERROR_CAS_UNII
    assert compound.cas is None; assert compound.unii is None; assert compound.molecular_formula == "OK_F"
    assert compound.molecular_weight == 1.0; assert compound.description == "OK_DESC"; assert compound.synonyms == ["OK_SYN"]
    mock_api_helpers.get_cas_unii.side_effect = original_side_effect
def test_info_helper_fetch_error_properties(mock_api_helpers, capsys):
    original_side_effect = mock_api_helpers.get_additional_properties.side_effect
    expected_exception = requests.exceptions.Timeout("Simulated timeout for properties")
    def side_effect(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR_PROPS: raise expected_exception
        return mock_api_helpers.additional_properties_data.get(cid_val, {"MolecularFormula": None, "MolecularWeight": None, "CanonicalSMILES": None, "IUPACName": None})
    mock_api_helpers.get_additional_properties.side_effect = side_effect
    compound = info(MOCK_NAME_FETCH_ERROR_PROPS); captured = capsys.readouterr()
    assert f"Warning: Failed to get additional properties for CID {MOCK_CID_FETCH_ERROR_PROPS}: Timeout" in captured.err
    assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_FETCH_ERROR_PROPS
    assert compound.molecular_formula is None; assert compound.molecular_weight is None; assert compound.canonical_smiles is None; assert compound.iupac_name is None
    assert compound.cas == "OK_CAS"; assert compound.unii == "OK_UNII"; assert compound.description == "OK_DESC"; assert compound.synonyms == ["OK_SYN"]
    mock_api_helpers.get_additional_properties.side_effect = original_side_effect
def test_info_helper_fetch_error_description(mock_api_helpers, capsys):
    original_side_effect = mock_api_helpers.get_compound_description.side_effect
    expected_exception = ValueError("Simulated parsing error for description")
    def side_effect(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR_DESC: raise expected_exception
        return mock_api_helpers.description_data.get(cid_val, None)
    mock_api_helpers.get_compound_description.side_effect = side_effect
    compound = info(MOCK_NAME_FETCH_ERROR_DESC); captured = capsys.readouterr()
    assert f"Warning: Failed to get description for CID {MOCK_CID_FETCH_ERROR_DESC}: ValueError" in captured.err
    assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_FETCH_ERROR_DESC
    assert compound.description is None; assert compound.cas == "OK_CAS"; assert compound.molecular_formula == "OK_F"; assert compound.synonyms == ["OK_SYN"]
    mock_api_helpers.get_compound_description.side_effect = original_side_effect
def test_info_helper_fetch_error_synonyms(mock_api_helpers, capsys):
    original_side_effect = mock_api_helpers.get_all_synonyms.side_effect
    expected_exception = ConnectionError("Simulated connection error for synonyms")
    def side_effect(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR_SYN: raise expected_exception
        return mock_api_helpers.synonyms_data.get(cid_val, [])
    mock_api_helpers.get_all_synonyms.side_effect = side_effect
    compound = info(MOCK_NAME_FETCH_ERROR_SYN); captured = capsys.readouterr()
    assert f"Warning: Failed to get synonyms for CID {MOCK_CID_FETCH_ERROR_SYN}: ConnectionError" in captured.err
    assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_FETCH_ERROR_SYN; assert compound.synonyms == []
    assert compound.cas == "OK_CAS"; assert compound.molecular_formula == "OK_F"; assert compound.description == "OK_DESC"
    assert compound.common_name == MOCK_NAME_FETCH_ERROR_SYN # Correct assertion based on info() logic
    mock_api_helpers.get_all_synonyms.side_effect = original_side_effect
def test_info_pydantic_validation_does_not_fail_on_invalid_weight_str(mock_api_helpers, capsys):
    # This test was correct in the previous version
    compound = info(MOCK_NAME_INVALID_DATA); captured = capsys.readouterr()
    assert isinstance(compound, CompoundData); assert compound.cid == MOCK_CID_INVALID_DATA; assert compound.molecular_weight is None
    assert compound.cas == "OK_CAS"; assert compound.molecular_formula == "OK_F"; assert compound.synonyms == ["OK_SYN"]
    assert "Error: Failed to create CompoundData model" not in captured.err; assert "Warning:" not in captured.err
def test_info_internal_resolve_error(mock_api_helpers):
    # This test was correct in the previous version
    mock_api_helpers.get_cids_by_name.return_value = [MOCK_CID_ASPIRIN]
    with patch('ChemInformant.cheminfo_api._resolve_identifier', return_value=[MOCK_CID_ASPIRIN]) as mock_resolve:
        with pytest.raises(TypeError, match="Internal error: Expected single CID but got"): info(MOCK_NAME_ASPIRIN)
        mock_resolve.assert_called_once_with(MOCK_NAME_ASPIRIN)

# --- Tests for Convenience Functions (Error Handling) ---
# (These tests were correct in the previous version)
def test_convenience_funcs_on_not_found(mock_api_helpers):
    assert cid(MOCK_NAME_NOTFOUND) is None; assert cas(MOCK_NAME_NOTFOUND) is None; assert unii(MOCK_NAME_NOTFOUND) is None
    assert form(MOCK_NAME_NOTFOUND) is None; assert wgt(MOCK_NAME_NOTFOUND) is None; assert smi(MOCK_NAME_NOTFOUND) is None
    assert iup(MOCK_NAME_NOTFOUND) is None; assert dsc(MOCK_NAME_NOTFOUND) is None; assert syn(MOCK_NAME_NOTFOUND) == []
def test_convenience_funcs_on_ambiguous(mock_api_helpers):
    assert cid(MOCK_NAME_AMBIGUOUS) is None; assert cas(MOCK_NAME_AMBIGUOUS) is None; assert unii(MOCK_NAME_AMBIGUOUS) is None
    assert form(MOCK_NAME_AMBIGUOUS) is None; assert wgt(MOCK_NAME_AMBIGUOUS) is None; assert smi(MOCK_NAME_AMBIGUOUS) is None
    assert iup(MOCK_NAME_AMBIGUOUS) is None; assert dsc(MOCK_NAME_AMBIGUOUS) is None; assert syn(MOCK_NAME_AMBIGUOUS) == []
def test_convenience_funcs_on_info_partial_failure(mock_api_helpers):
    # This test was correct in the previous version
    original_side_effect = mock_api_helpers.get_cas_unii.side_effect
    expected_exception = ValueError("Unexpected failure getting CAS/UNII")
    def side_effect(cid_val):
        if cid_val == MOCK_CID_ASPIRIN: raise expected_exception
        return mock_api_helpers.cas_unii_data.get(cid_val, (None, None))
    mock_api_helpers.get_cas_unii.side_effect = side_effect
    assert cas(MOCK_NAME_ASPIRIN) is None; assert unii(MOCK_NAME_ASPIRIN) is None
    assert form(MOCK_NAME_ASPIRIN) == "C9H8O4"; assert wgt(MOCK_NAME_ASPIRIN) == 180.16
    assert smi(MOCK_NAME_ASPIRIN) == "SMILES_ASP"; assert iup(MOCK_NAME_ASPIRIN) == "IUPAC_ASP"
    assert dsc(MOCK_NAME_ASPIRIN) == "Aspirin description."; assert syn(MOCK_NAME_ASPIRIN) == ["Aspirin", "Synonym A"]
    mock_api_helpers.get_cas_unii.side_effect = original_side_effect

# --- Tests for get_multiple_compounds() ---
# (Fixture definition remains the same)
@pytest.fixture
def batch_identifiers():
    return [
        MOCK_NAME_ASPIRIN, MOCK_CID_ETHANOL, MOCK_NAME_NOTFOUND, MOCK_NAME_AMBIGUOUS, MOCK_CID_WATER,
        MOCK_NAME_NOCAS, -10, None, MOCK_NAME_FETCH_ERROR_CAS_UNII, MOCK_CID_ASPIRIN, MOCK_NAME_INVALID_DATA,
    ]

# (This complex test was correct in the previous version)
def test_batch_success_and_failure_mix(mock_api_helpers, batch_identifiers):
    original_cas_unii_side_effect = mock_api_helpers.get_cas_unii.side_effect
    expected_cas_unii_exception = TimeoutError("Failed fetching CAS/UNII for 1005")
    def failing_cas_unii_for_batch(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR_CAS_UNII: raise expected_cas_unii_exception
        return mock_api_helpers.cas_unii_data.get(cid_val, (None, None))
    mock_api_helpers.get_cas_unii.side_effect = failing_cas_unii_for_batch
    results = get_multiple_compounds(batch_identifiers)
    assert len(results) == len(batch_identifiers)
    # Success Cases
    assert isinstance(results[MOCK_NAME_ASPIRIN], CompoundData) and results[MOCK_NAME_ASPIRIN].cid == MOCK_CID_ASPIRIN
    assert isinstance(results[MOCK_CID_ETHANOL], CompoundData) and results[MOCK_CID_ETHANOL].cid == MOCK_CID_ETHANOL
    assert isinstance(results[MOCK_CID_WATER], CompoundData) and results[MOCK_CID_WATER].cid == MOCK_CID_WATER and results[MOCK_CID_WATER].cas is None
    assert isinstance(results[MOCK_NAME_NOCAS], CompoundData) and results[MOCK_NAME_NOCAS].cid == MOCK_CID_NO_CAS and results[MOCK_NAME_NOCAS].cas is None
    assert isinstance(results[MOCK_CID_ASPIRIN], CompoundData) and results[MOCK_CID_ASPIRIN].input_identifier == MOCK_CID_ASPIRIN
    # Failure Cases
    assert isinstance(results[MOCK_NAME_NOTFOUND], NotFoundError) and results[MOCK_NAME_NOTFOUND].identifier == MOCK_NAME_NOTFOUND
    assert isinstance(results[MOCK_NAME_AMBIGUOUS], AmbiguousIdentifierError) and results[MOCK_NAME_AMBIGUOUS].identifier == MOCK_NAME_AMBIGUOUS
    assert isinstance(results[-10], ValueError)
    assert isinstance(results[None], TypeError)
    assert results[MOCK_NAME_FETCH_ERROR_CAS_UNII] is expected_cas_unii_exception
    # Invalid data case (should succeed with weight=None)
    assert isinstance(results[MOCK_NAME_INVALID_DATA], CompoundData) and results[MOCK_NAME_INVALID_DATA].molecular_weight is None
    mock_api_helpers.get_cas_unii.side_effect = original_cas_unii_side_effect

# (Other batch tests remain the same as the previous corrected version)
def test_batch_empty_input(mock_api_helpers):
    results = get_multiple_compounds([]); assert results == {}
    mock_api_helpers.get_batch_properties.assert_not_called()
def test_batch_all_resolve_fail(mock_api_helpers):
    identifiers = [MOCK_NAME_NOTFOUND, MOCK_NAME_AMBIGUOUS, -5]
    results = get_multiple_compounds(identifiers); assert len(results) == 3
    assert isinstance(results[MOCK_NAME_NOTFOUND], NotFoundError); assert isinstance(results[MOCK_NAME_AMBIGUOUS], AmbiguousIdentifierError); assert isinstance(results[-5], ValueError)
    mock_api_helpers.get_batch_properties.assert_not_called(); mock_api_helpers.get_batch_synonyms.assert_not_called()
    mock_api_helpers.get_batch_descriptions.assert_not_called(); mock_api_helpers.get_cas_unii.assert_not_called()
def test_batch_api_helper_fetch_error_props(mock_api_helpers, capsys):
    expected_batch_exception = requests.exceptions.ConnectionError("Batch Props API down")
    mock_api_helpers.get_batch_properties.side_effect = expected_batch_exception
    identifiers = [MOCK_NAME_ASPIRIN, MOCK_CID_ETHANOL]
    results = get_multiple_compounds(identifiers); captured = capsys.readouterr()
    assert f"Error: Batch data fetch failed: {expected_batch_exception}" in captured.err; assert len(results) == 2
    assert results[MOCK_NAME_ASPIRIN] is expected_batch_exception; assert results[MOCK_CID_ETHANOL] is expected_batch_exception
def test_batch_api_helper_fetch_error_synonyms(mock_api_helpers, capsys):
    original_props_side_effect = mock_api_helpers.get_batch_properties.side_effect
    mock_api_helpers.get_batch_properties.side_effect = lambda cids, props: { cid: mock_api_helpers.additional_properties_data.get(cid, {}) for cid in cids }
    expected_batch_exception = requests.exceptions.Timeout("Batch Synonyms API timeout")
    mock_api_helpers.get_batch_synonyms.side_effect = expected_batch_exception
    identifiers = [MOCK_NAME_ASPIRIN, MOCK_CID_ETHANOL]
    results = get_multiple_compounds(identifiers); captured = capsys.readouterr()
    assert f"Error: Batch data fetch failed: {expected_batch_exception}" in captured.err; assert len(results) == 2
    assert results[MOCK_NAME_ASPIRIN] is expected_batch_exception; assert results[MOCK_CID_ETHANOL] is expected_batch_exception
    mock_api_helpers.get_batch_properties.side_effect = original_props_side_effect
def test_batch_api_helper_fetch_error_descriptions(mock_api_helpers, capsys):
    original_props_side_effect = mock_api_helpers.get_batch_properties.side_effect
    original_syn_side_effect = mock_api_helpers.get_batch_synonyms.side_effect
    mock_api_helpers.get_batch_properties.side_effect = lambda cids, props: { cid: mock_api_helpers.additional_properties_data.get(cid, {}) for cid in cids }
    mock_api_helpers.get_batch_synonyms.side_effect = lambda cids: { cid: mock_api_helpers.synonyms_data.get(cid, []) for cid in cids }
    expected_batch_exception = requests.exceptions.HTTPError("Batch Descriptions API 500")
    mock_api_helpers.get_batch_descriptions.side_effect = expected_batch_exception
    identifiers = [MOCK_NAME_ASPIRIN, MOCK_CID_ETHANOL]
    results = get_multiple_compounds(identifiers); captured = capsys.readouterr()
    assert f"Error: Batch data fetch failed: {expected_batch_exception}" in captured.err; assert len(results) == 2
    assert results[MOCK_NAME_ASPIRIN] is expected_batch_exception; assert results[MOCK_CID_ETHANOL] is expected_batch_exception
    mock_api_helpers.get_batch_properties.side_effect = original_props_side_effect; mock_api_helpers.get_batch_synonyms.side_effect = original_syn_side_effect
def test_batch_resolve_internal_error(mock_api_helpers):
    # This test was correct in the previous version
    identifiers = [MOCK_NAME_ASPIRIN, MOCK_NAME_ETHANOL]
    def mock_resolve_side_effect(identifier):
        if identifier == MOCK_NAME_ETHANOL: raise TypeError(f"Input must be a compound name (str) or CID (int), got <class 'list'>")
        else: return MOCK_CID_ASPIRIN
    with patch('ChemInformant.cheminfo_api._resolve_identifier', side_effect=mock_resolve_side_effect): results = get_multiple_compounds(identifiers)
    assert len(results) == 2; assert isinstance(results[MOCK_NAME_ASPIRIN], CompoundData); assert isinstance(results[MOCK_NAME_ETHANOL], TypeError)
    assert "Input must be a compound name" in str(results[MOCK_NAME_ETHANOL])