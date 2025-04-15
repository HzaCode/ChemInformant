# tests/test_api.py
"""
Comprehensive tests for ChemInformant API functions using pytest and pytest-mock.
These tests DO NOT hit the live PubChem API.
"""

import pytest
import requests  # Import requests to test for potential RequestException propagation
from unittest.mock import MagicMock  # Used with pytest-mock

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
    # setup_cache, # Can test this separately if needed
    CompoundData,
    NotFoundError,
    AmbiguousIdentifierError,
)

# --- Constants for Mocking ---
MOCK_CID_ASPIRIN = 2244
MOCK_CID_ETHANOL = 702
MOCK_CID_WATER = 962
MOCK_CID_AMBIGUOUS_1 = 1001
MOCK_CID_AMBIGUOUS_2 = 1002
MOCK_CID_NO_CAS = 1003
MOCK_CID_NO_WEIGHT = 1004
MOCK_CID_FETCH_ERROR = 1005  # For simulating fetch errors

MOCK_NAME_ASPIRIN = "Aspirin"
MOCK_NAME_ETHANOL = "Ethanol"
MOCK_NAME_WATER = "Water"
MOCK_NAME_AMBIGUOUS = "AmbiguousDrug"
MOCK_NAME_NOTFOUND = "NotFoundCompound"
MOCK_NAME_NOCAS = "NoCasCompound"
MOCK_NAME_NOWEIGHT = "NoWeightCompound"
MOCK_NAME_FETCH_ERROR = "FetchErrorCompound"  # Resolves OK, but helpers fail

# --- Fixtures for Mocking API Helpers ---


@pytest.fixture
def mock_api_helpers(mocker):
    """Mocks all necessary functions in the api_helpers module."""
    # IMPORTANT: We mock api_helpers as imported by cheminfo_api
    mock_obj = MagicMock()

    # --- Mock data fetching functions used by cheminfo_api ---

    # 1. Identifier Resolution Mock
    mock_obj.get_cids_by_name.side_effect = lambda name: {
        MOCK_NAME_ASPIRIN: [MOCK_CID_ASPIRIN],
        MOCK_NAME_ETHANOL: [MOCK_CID_ETHANOL],
        MOCK_NAME_WATER: [MOCK_CID_WATER],
        MOCK_NAME_AMBIGUOUS: [MOCK_CID_AMBIGUOUS_1, MOCK_CID_AMBIGUOUS_2],
        MOCK_NAME_NOCAS: [MOCK_CID_NO_CAS],
        MOCK_NAME_NOWEIGHT: [MOCK_CID_NO_WEIGHT],
        MOCK_NAME_FETCH_ERROR: [MOCK_CID_FETCH_ERROR],
    }.get(
        name, None
    )  # Return None for not found

    # 2. Individual Fetch Mocks (used by info() and batch fallback)
    # Use a dictionary to store the current side effect, allowing modification within tests
    mock_obj.cas_unii_data = {
        MOCK_CID_ASPIRIN: ("50-78-2", "ASPIRIN_UNII"),
        MOCK_CID_ETHANOL: ("64-17-5", "ETHANOL_UNII"),
        MOCK_CID_WATER: (
            None,
            "WATER_UNII",
        ),  # Water might not have CAS via this method
        MOCK_CID_NO_CAS: (None, "NOCAS_UNII"),  # Has UNII but no CAS
        MOCK_CID_NO_WEIGHT: ("NOWEIGHT_CAS", "NOWEIGHT_UNII"),
        MOCK_CID_AMBIGUOUS_1: ("CAS_AMBIG1", "UNII_AMBIG1"),
        MOCK_CID_AMBIGUOUS_2: ("CAS_AMBIG2", "UNII_AMBIG2"),
        MOCK_CID_FETCH_ERROR: (
            "FETCH_ERROR_CAS",
            "FETCH_ERROR_UNII",
        ),  # Provide data initially
    }
    mock_obj.get_cas_unii.side_effect = lambda cid_val: mock_obj.cas_unii_data.get(
        cid_val, (None, None)
    )

    mock_obj.additional_properties_data = {
        MOCK_CID_ASPIRIN: {
            "MolecularFormula": "C9H8O4",
            "MolecularWeight": "180.16",
            "CanonicalSMILES": "SMILES_ASP",
            "IUPACName": "IUPAC_ASP",
        },
        MOCK_CID_ETHANOL: {
            "MolecularFormula": "C2H6O",
            "MolecularWeight": "46.07",
            "CanonicalSMILES": "SMILES_ETH",
            "IUPACName": "IUPAC_ETH",
        },
        MOCK_CID_WATER: {
            "MolecularFormula": "H2O",
            "MolecularWeight": "18.015",
            "CanonicalSMILES": "O",
            "IUPACName": "water",
        },
        MOCK_CID_NO_CAS: {
            "MolecularFormula": "F_NOCAS",
            "MolecularWeight": "100.0",
            "CanonicalSMILES": "S_NOCAS",
            "IUPACName": "I_NOCAS",
        },
        MOCK_CID_NO_WEIGHT: {
            "MolecularFormula": "F_NOWEIGHT",
            "MolecularWeight": None,
            "CanonicalSMILES": "S_NOWEIGHT",
            "IUPACName": "I_NOWEIGHT",
        },  # Explicit None weight
        MOCK_CID_AMBIGUOUS_1: {
            "MolecularFormula": "F_AMBIG1",
            "MolecularWeight": "1.0",
            "CanonicalSMILES": "S_AMBIG1",
            "IUPACName": "I_AMBIG1",
        },
        MOCK_CID_AMBIGUOUS_2: {
            "MolecularFormula": "F_AMBIG2",
            "MolecularWeight": "2.0",
            "CanonicalSMILES": "S_AMBIG2",
            "IUPACName": "I_AMBIG2",
        },
        MOCK_CID_FETCH_ERROR: {
            "MolecularFormula": "F_FETCH_ERROR",
            "MolecularWeight": "99.9",
            "CanonicalSMILES": "S_FETCH_ERROR",
            "IUPACName": "I_FETCH_ERROR",
        },
    }
    mock_obj.get_additional_properties.side_effect = (
        lambda cid_val: mock_obj.additional_properties_data.get(cid_val, {})
    )

    mock_obj.description_data = {
        MOCK_CID_ASPIRIN: "Aspirin description.",
        MOCK_CID_ETHANOL: "Ethanol description.",
        MOCK_CID_WATER: None,
        MOCK_CID_NO_CAS: "No CAS description.",
        MOCK_CID_NO_WEIGHT: "No Weight description.",
        MOCK_CID_AMBIGUOUS_1: "Desc Ambiguous 1",
        MOCK_CID_AMBIGUOUS_2: "Desc Ambiguous 2",
        MOCK_CID_FETCH_ERROR: "Fetch error description.",
    }
    mock_obj.get_compound_description.side_effect = (
        lambda cid_val: mock_obj.description_data.get(cid_val, None)
    )

    mock_obj.synonyms_data = {
        MOCK_CID_ASPIRIN: ["Aspirin", "Synonym A"],
        MOCK_CID_ETHANOL: ["Ethanol", "Synonym B"],
        MOCK_CID_WATER: ["Water", "H2O"],
        MOCK_CID_NO_CAS: ["NoCasCompound"],
        MOCK_CID_NO_WEIGHT: ["NoWeightCompound"],
        MOCK_CID_AMBIGUOUS_1: ["AmbiguousDrug", "Syn C"],
        MOCK_CID_AMBIGUOUS_2: ["AmbiguousDrug", "Syn D"],
        MOCK_CID_FETCH_ERROR: ["FetchErrorCompound"],
    }
    mock_obj.get_all_synonyms.side_effect = lambda cid_val: mock_obj.synonyms_data.get(
        cid_val, []
    )

    # 3. Batch Fetch Mocks
    mock_obj.get_batch_properties.side_effect = lambda cids, props: {
        cid_val: mock_obj.get_additional_properties(cid_val)
        for cid_val in cids
        if cid_val in mock_obj.additional_properties_data
    }
    mock_obj.get_batch_synonyms.side_effect = lambda cids: {
        cid_val: mock_obj.get_all_synonyms(cid_val)
        for cid_val in cids
        if cid_val in mock_obj.synonyms_data
    }
    mock_obj.get_batch_descriptions.side_effect = lambda cids: {
        cid_val: mock_obj.get_compound_description(cid_val)
        for cid_val in cids  # Include None descriptions
    }

    # --- Apply the patch ---
    mocker.patch("ChemInformant.cheminfo_api.api_helpers", new=mock_obj)

    return mock_obj  # Return the mock object for easy modification within tests


# --- Test Imports and Basic Setup ---


def test_imports():
    """Ensure core components can be imported."""
    assert callable(info)
    assert callable(cid)
    assert callable(cas)
    assert callable(unii)
    assert callable(form)
    assert callable(wgt)
    assert callable(smi)
    assert callable(iup)
    assert callable(dsc)
    assert callable(syn)
    assert callable(get_multiple_compounds)
    assert CompoundData is not None
    assert NotFoundError is not None
    assert AmbiguousIdentifierError is not None


# --- Tests for info() ---


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
    assert compound.synonyms == ["Aspirin", "Synonym A"]
    assert compound.common_name == MOCK_NAME_ASPIRIN
    # Check computed field
    assert (
        str(compound.pubchem_url)
        == f"https://pubchem.ncbi.nlm.nih.gov/compound/{MOCK_CID_ASPIRIN}"
    )


def test_info_success_by_cid(mock_api_helpers):
    compound = info(MOCK_CID_ETHANOL)
    assert isinstance(compound, CompoundData)
    assert compound.cid == MOCK_CID_ETHANOL
    assert compound.input_identifier == MOCK_CID_ETHANOL
    assert compound.cas == "64-17-5"
    assert compound.molecular_formula == "C2H6O"
    assert compound.common_name == "Ethanol"


def test_info_success_partial_data(mock_api_helpers):
    compound = info(MOCK_CID_WATER)
    assert isinstance(compound, CompoundData)
    assert compound.cid == MOCK_CID_WATER
    assert compound.cas is None
    assert compound.unii == "WATER_UNII"
    assert compound.molecular_formula == "H2O"
    assert compound.molecular_weight == 18.015
    assert compound.description is None
    assert compound.synonyms == ["Water", "H2O"]
    assert compound.common_name == "Water"


def test_info_success_explicit_none_weight(mock_api_helpers):
    compound = info(MOCK_CID_NO_WEIGHT)
    assert isinstance(compound, CompoundData)
    assert compound.molecular_weight is None


def test_info_not_found(mock_api_helpers):
    with pytest.raises(NotFoundError) as excinfo:
        info(MOCK_NAME_NOTFOUND)
    assert MOCK_NAME_NOTFOUND in str(excinfo.value)
    mock_api_helpers.get_cids_by_name.assert_called_once_with(MOCK_NAME_NOTFOUND)


def test_info_ambiguous_name(mock_api_helpers):
    with pytest.raises(AmbiguousIdentifierError) as excinfo:
        info(MOCK_NAME_AMBIGUOUS)
    assert MOCK_NAME_AMBIGUOUS in str(excinfo.value)
    assert excinfo.value.identifier == MOCK_NAME_AMBIGUOUS
    assert excinfo.value.cids == [MOCK_CID_AMBIGUOUS_1, MOCK_CID_AMBIGUOUS_2]
    mock_api_helpers.get_cids_by_name.assert_called_once_with(MOCK_NAME_AMBIGUOUS)


def test_info_invalid_cid_input(mock_api_helpers):
    with pytest.raises(ValueError):
        info(0)
    with pytest.raises(ValueError):
        info(-1)


def test_info_invalid_type_input(mock_api_helpers):
    with pytest.raises(TypeError):
        info(None)
    with pytest.raises(TypeError):
        info([MOCK_CID_ASPIRIN])


# --- MODIFIED TEST ---
def test_info_helper_fetch_error_returns_partial(mock_api_helpers, capsys):
    """Test info() returns partial data when a helper function fails but doesn't raise."""
    # Simulate get_cas_unii failing (e.g., network timeout caught internally)
    # by making the mock return None, None as if the fetch failed inside api_helpers
    mock_api_helpers.cas_unii_data[MOCK_CID_FETCH_ERROR] = (
        None,
        None,
    )  # Simulate fetch failure for this CID

    # info() should now succeed but return None for cas/unii
    compound = info(MOCK_NAME_FETCH_ERROR)

    # Optional: Check if a warning was printed to stderr
    # captured = capsys.readouterr()
    # assert f"Warning: Failed to get CAS/UNII for CID {MOCK_CID_FETCH_ERROR}" in captured.err

    assert isinstance(compound, CompoundData)
    assert compound.cid == MOCK_CID_FETCH_ERROR
    # Check that the fields fetched by the 'failing' helper are None
    assert compound.cas is None
    assert compound.unii is None
    # Check that other fields fetched by non-failing helpers are present
    assert compound.molecular_formula == "F_FETCH_ERROR"
    assert compound.description == "Fetch error description."
    assert compound.synonyms == ["FetchErrorCompound"]


# --- Tests for Convenience Functions ---


# cid() tests
def test_cid_success_name(mock_api_helpers):
    assert cid(MOCK_NAME_ASPIRIN) == MOCK_CID_ASPIRIN


def test_cid_success_cid_input(mock_api_helpers):
    assert cid(MOCK_CID_ETHANOL) == MOCK_CID_ETHANOL


def test_cid_not_found(mock_api_helpers):
    assert cid(MOCK_NAME_NOTFOUND) is None


def test_cid_ambiguous(mock_api_helpers):
    assert cid(MOCK_NAME_AMBIGUOUS) is None


def test_cid_invalid_input(mock_api_helpers):
    assert cid(-5) is None
    assert cid(None) is None


# cas() tests
def test_cas_success(mock_api_helpers):
    assert cas(MOCK_NAME_ASPIRIN) == "50-78-2"
    assert cas(MOCK_CID_ETHANOL) == "64-17-5"


# --- MODIFIED TEST ---
def test_cas_returns_none_when_helper_returns_none(mock_api_helpers):
    """Test cas() returns None if api_helpers.get_cas_unii returns (None, unii)."""
    # Modify mock specifically for Aspirin's CID to return None for CAS
    mock_api_helpers.cas_unii_data[MOCK_CID_ASPIRIN] = (
        None,
        "ASPIRIN_UNII",
    )  # CAS is None

    # Now calling cas for Aspirin should return None
    assert cas(MOCK_NAME_ASPIRIN) is None


def test_cas_not_found(mock_api_helpers):
    assert cas(MOCK_NAME_NOTFOUND) is None


def test_cas_ambiguous(mock_api_helpers):
    assert cas(MOCK_NAME_AMBIGUOUS) is None


# --- MODIFIED TEST ---
def test_cas_succeeds_when_other_helper_fails(mock_api_helpers, capsys):
    """Test cas() still succeeds if unrelated helper (e.g., description) fails."""
    # Simulate description fetch failing (e.g., by raising error or returning None)
    mock_api_helpers.description_data[MOCK_CID_ASPIRIN] = (
        None  # Simulate no description found
    )
    # Or simulate an error being caught inside info():
    # mock_api_helpers.get_compound_description.side_effect = lambda cid_val: (_ for _ in ()).throw(ValueError("Desc fetch failed")) if cid_val == MOCK_CID_ASPIRIN else None

    # info() should still succeed and fetch CAS
    # Therefore, cas() should return the correct CAS number
    result = cas(MOCK_NAME_ASPIRIN)
    assert result == "50-78-2"  # Expect success now

    # Optional: Check stderr for the warning from info()
    # captured = capsys.readouterr()
    # assert f"Warning: Failed to get description for CID {MOCK_CID_ASPIRIN}" in captured.err


# form() tests
def test_form_success(mock_api_helpers):
    assert form(MOCK_NAME_ASPIRIN) == "C9H8O4"


def test_form_not_found(mock_api_helpers):
    assert form(MOCK_NAME_NOTFOUND) is None


# wgt() tests
def test_wgt_success(mock_api_helpers):
    assert wgt(MOCK_NAME_ETHANOL) == 46.07  # float


def test_wgt_explicit_none(mock_api_helpers):
    assert wgt(MOCK_NAME_NOWEIGHT) is None


def test_wgt_not_found(mock_api_helpers):
    assert wgt(MOCK_NAME_NOTFOUND) is None


# syn() tests
def test_syn_success(mock_api_helpers):
    assert syn(MOCK_NAME_ASPIRIN) == ["Aspirin", "Synonym A"]


def test_syn_empty(mock_api_helpers):
    # Use water which resolves but mock returns empty list for synonyms
    mock_api_helpers.synonyms_data[MOCK_CID_WATER] = []  # Explicitly set empty list
    assert syn(MOCK_CID_WATER) == []


def test_syn_not_found(mock_api_helpers):
    assert syn(MOCK_NAME_NOTFOUND) == []


def test_syn_ambiguous(mock_api_helpers):
    assert syn(MOCK_NAME_AMBIGUOUS) == []


# --- Tests for get_multiple_compounds() ---


@pytest.fixture
def batch_identifiers():
    """Provides a standard list for batch tests."""
    return [
        MOCK_NAME_ASPIRIN,  # Success (name) -> 2244
        MOCK_CID_ETHANOL,  # Success (CID) -> 702
        MOCK_NAME_NOTFOUND,  # Failure (NotFound)
        MOCK_NAME_AMBIGUOUS,  # Failure (Ambiguous) -> [1001, 1002]
        MOCK_CID_WATER,  # Success (CID) -> 962
        MOCK_NAME_NOCAS,  # Success (name) -> 1003
        -10,  # Failure (ValueError)
        None,  # Failure (TypeError)
        MOCK_NAME_FETCH_ERROR,  # Resolves OK (1005), but helpers will fail later
        MOCK_CID_ASPIRIN,  # Duplicate successful CID input -> 2244
    ]


def test_batch_success_and_failure_mix(mock_api_helpers, batch_identifiers):
    # --- Setup simulation for fetch error within batch ---
    original_cas_unii_side_effect = mock_api_helpers.get_cas_unii.side_effect
    expected_fetch_exception = TimeoutError("Failed fetching CAS/UNII")

    def failing_cas_unii_for_batch(cid_val):
        if cid_val == MOCK_CID_FETCH_ERROR:  # This CID comes from MOCK_NAME_FETCH_ERROR
            raise expected_fetch_exception
        # Call original side effect logic for other CIDs
        if callable(original_cas_unii_side_effect):
            return original_cas_unii_side_effect(cid_val)
        return ("OK", "OK")  # Fallback

    mock_api_helpers.get_cas_unii.side_effect = failing_cas_unii_for_batch
    # ----------------------------------------------------

    results = get_multiple_compounds(batch_identifiers)

    assert len(results) == len(batch_identifiers)  # Each input should have an entry

    # --- Check Success Cases ---
    assert (
        isinstance(results[MOCK_NAME_ASPIRIN], CompoundData)
        and results[MOCK_NAME_ASPIRIN].cid == MOCK_CID_ASPIRIN
    )
    assert (
        isinstance(results[MOCK_CID_ETHANOL], CompoundData)
        and results[MOCK_CID_ETHANOL].cid == MOCK_CID_ETHANOL
    )
    assert (
        isinstance(results[MOCK_CID_WATER], CompoundData)
        and results[MOCK_CID_WATER].cid == MOCK_CID_WATER
        and results[MOCK_CID_WATER].cas is None
    )
    assert (
        isinstance(results[MOCK_NAME_NOCAS], CompoundData)
        and results[MOCK_NAME_NOCAS].cid == MOCK_CID_NO_CAS
        and results[MOCK_NAME_NOCAS].cas is None
    )
    # Check duplicate CID input - result should be CompoundData
    assert (
        isinstance(results[MOCK_CID_ASPIRIN], CompoundData)
        and results[MOCK_CID_ASPIRIN].cid == MOCK_CID_ASPIRIN
        and results[MOCK_CID_ASPIRIN].input_identifier == MOCK_CID_ASPIRIN
    )

    # --- Check Failure Cases ---
    assert (
        isinstance(results[MOCK_NAME_NOTFOUND], NotFoundError)
        and results[MOCK_NAME_NOTFOUND].identifier == MOCK_NAME_NOTFOUND
    )
    assert (
        isinstance(results[MOCK_NAME_AMBIGUOUS], AmbiguousIdentifierError)
        and results[MOCK_NAME_AMBIGUOUS].identifier == MOCK_NAME_AMBIGUOUS
    )
    assert isinstance(results[-10], ValueError)
    assert isinstance(results[None], TypeError)
    # Check the specific fetch error for the designated identifier
    assert results[MOCK_NAME_FETCH_ERROR] is expected_fetch_exception

    # Restore the mock for subsequent tests if necessary (though fixture scope usually resets)
    mock_api_helpers.get_cas_unii.side_effect = original_cas_unii_side_effect


def test_batch_empty_input(mock_api_helpers):
    results = get_multiple_compounds([])
    assert results == {}
    mock_api_helpers.get_batch_properties.assert_not_called()


def test_batch_all_resolve_fail(mock_api_helpers):
    identifiers = [MOCK_NAME_NOTFOUND, MOCK_NAME_AMBIGUOUS, -5]
    results = get_multiple_compounds(identifiers)
    assert len(results) == 3
    assert isinstance(results[MOCK_NAME_NOTFOUND], NotFoundError)
    assert isinstance(results[MOCK_NAME_AMBIGUOUS], AmbiguousIdentifierError)
    assert isinstance(results[-5], ValueError)
    mock_api_helpers.get_batch_properties.assert_not_called()


def test_batch_api_helper_fetch_error(mock_api_helpers):
    """Test batch processing where a primary batch API call itself fails."""
    expected_batch_exception = requests.exceptions.ConnectionError("Batch API down")
    # Make get_batch_properties fail
    mock_api_helpers.get_batch_properties.side_effect = expected_batch_exception

    identifiers = [MOCK_NAME_ASPIRIN, MOCK_CID_ETHANOL]  # These resolve successfully
    results = get_multiple_compounds(identifiers)

    assert len(results) == 2
    # Both results should reflect the same batch fetch error
    assert results[MOCK_NAME_ASPIRIN] is expected_batch_exception
    assert results[MOCK_CID_ETHANOL] is expected_batch_exception

    # Reset side effect if necessary (fixture scope usually handles this)
    # mock_api_helpers.get_batch_properties.side_effect = lambda cids, props: { ... }
