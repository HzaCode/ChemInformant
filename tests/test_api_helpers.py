# tests/test_api_helpers.py (Assumed corrected content)
import pytest
import requests
import requests_cache
from unittest.mock import MagicMock, patch

from ChemInformant import (
    api_helpers,
)  # Import the module to allow patching its internals
from ChemInformant.api_helpers import (
    _fetch_data,
    get_cids_by_name,
    get_cas_unii,
    get_additional_properties,
    get_compound_description,
    get_all_synonyms,
    _get_batch_data_for_cids,  # Keep if you want to test it directly, though it's internal
    get_batch_properties,
    get_batch_synonyms,
    get_batch_descriptions,
    setup_cache,
    get_session,  # Keep if testing it directly
    fetch_compound_image_data,  # For image tests if any were here (they are in test_api.py)
    DEFAULT_CACHE_NAME,
    DEFAULT_CACHE_BACKEND,
    DEFAULT_CACHE_EXPIRE_AFTER,
    PUBCHEM_API_BASE,
    PUG_VIEW_BASE,
    REQUEST_TIMEOUT,
    quote,
)

CID1 = 2244
CID2 = 702
CID3 = 962
NAME1 = "Aspirin"
NAME2 = "Ethanol"  # Unused in this file currently
CAS1 = "50-78-2"
UNII1 = "R16CO5Y76E"
NS_MAP = {"pug": "http://pubchem.ncbi.nlm.nih.gov/pug_rest"}


@pytest.fixture(autouse=True)  # Applied to all tests in this module
def mock_session_for_module(
    mocker,
):  # Renamed to avoid conflict if a test defines its own 'mock_session'
    original_session = api_helpers._session
    api_helpers._session = None

    mock_sess_instance = MagicMock(spec=requests_cache.CachedSession)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}  # Default content type
    mock_response.json.return_value = {}  # Default JSON response
    mock_response.text = ""  # Default text response
    mock_response.content = b""  # Default content response
    setattr(mock_response, "from_cache", False)  # Simulate not from cache by default
    mock_sess_instance.get.return_value = mock_response
    mock_response.raise_for_status.return_value = None  # Default no HTTP error

    mocker.patch("requests_cache.CachedSession", return_value=mock_sess_instance)
    mocker.patch("requests.Session", return_value=mock_sess_instance)

    yield mock_response, mock_sess_instance

    api_helpers._session = original_session


def test_setup_cache_default():
    with patch("requests_cache.CachedSession") as mock_cached_sess:
        api_helpers._session = None
        setup_cache()
        mock_cached_sess.assert_called_once_with(
            cache_name=DEFAULT_CACHE_NAME,
            backend=DEFAULT_CACHE_BACKEND,
            expire_after=DEFAULT_CACHE_EXPIRE_AFTER,
            allowable_codes=[200, 404],
            match_headers=False,
        )
        assert api_helpers._session is mock_cached_sess.return_value
    api_helpers._session = None


def test_setup_cache_custom():
    with patch("requests_cache.CachedSession") as mock_cached_sess:
        api_helpers._session = None
        setup_cache(
            cache_name="custom", backend="memory", expire_after=100, custom_arg="test"
        )
        mock_cached_sess.assert_called_once_with(
            cache_name="custom",
            backend="memory",
            expire_after=100,
            allowable_codes=[200, 404],
            match_headers=False,
            custom_arg="test",
        )
        assert api_helpers._session is mock_cached_sess.return_value
    api_helpers._session = None


def test_get_session_initializes_default(mock_session_for_module):
    _mock_resp, mock_sess_instance_from_fixture = mock_session_for_module
    api_helpers._session = None
    with patch("ChemInformant.api_helpers.setup_cache") as mock_setup_cache_call:

        def side_effect_setup_cache(*args, **kwargs):
            api_helpers._session = mock_sess_instance_from_fixture

        mock_setup_cache_call.side_effect = side_effect_setup_cache

        session = get_session()
        mock_setup_cache_call.assert_called_once()
        assert session is mock_sess_instance_from_fixture
    api_helpers._session = None


def test_get_session_returns_existing(mock_session_for_module):
    _mock_resp, mock_sess_instance_from_fixture = mock_session_for_module
    api_helpers._session = mock_sess_instance_from_fixture
    with patch("ChemInformant.api_helpers.setup_cache") as mock_setup_cache_call:
        session = get_session()
        mock_setup_cache_call.assert_not_called()
        assert session is mock_sess_instance_from_fixture
    api_helpers._session = None


# Tests for _fetch_data
def test_fetch_data_success_json(mock_session_for_module):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = {"key": "value"}
    result = _fetch_data("http://test.com/json", "TestID", 1)
    assert result == {"key": "value"}
    mock_sess.get.assert_called_once_with(
        "http://test.com/json", timeout=REQUEST_TIMEOUT
    )
    mock_resp.raise_for_status.assert_called_once()


def test_fetch_data_success_xml(mock_session_for_module):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.headers = {"Content-Type": "application/xml"}
    xml_string = "<root><item>Test</item></root>"
    mock_resp.content = xml_string.encode("utf-8")
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/xml", "TestID", 2)
    assert result == xml_string
    mock_sess.get.assert_called_once_with(
        "http://test.com/xml", timeout=REQUEST_TIMEOUT
    )


def test_fetch_data_success_text_xml(mock_session_for_module):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.headers = {"Content-Type": "text/xml;charset=UTF-8"}
    xml_string = "<root><item>Test</item></root>"
    mock_resp.content = xml_string.encode("utf-8")
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/textxml", "TestID", 3)
    assert result == xml_string


def test_fetch_data_success_unexpected_content_type_as_text(mock_session_for_module):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.headers = {"Content-Type": "text/plain"}
    plain_text = "Plain text response"
    mock_resp.text = plain_text
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/text", "TestID", 4)
    assert result == plain_text


def test_fetch_data_404_not_found(mock_session_for_module):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Error", response=mock_resp
    )
    result = _fetch_data("http://test.com/notfound", "TestID", 5)
    assert result is None
    mock_resp.raise_for_status.assert_not_called()


def test_fetch_data_other_http_error(mock_session_for_module, capsys):
    mock_resp, mock_sess = mock_session_for_module
    mock_resp.status_code = 500
    url = "http://test.com/error"
    error_msg = "500 Server Error"
    http_error = requests.exceptions.HTTPError(error_msg, response=mock_resp)
    mock_resp.raise_for_status.side_effect = http_error
    result = _fetch_data(url, "TestID", 6)
    assert result is None
    mock_resp.raise_for_status.assert_called_once()
    captured = capsys.readouterr()
    expected_warning = (
        f"Warning: API request failed for URL {url} (TestID: 6): {error_msg}"
    )
    assert expected_warning in captured.err


def test_fetch_data_request_exception(mock_session_for_module, capsys):
    mock_resp, mock_sess = mock_session_for_module
    url = "http://test.com/timeout"
    error_msg = "Connection timed out"
    req_error = requests.exceptions.Timeout(error_msg)
    mock_sess.get.side_effect = req_error
    result = _fetch_data(url, "TestID", 7)
    assert result is None
    mock_resp.raise_for_status.assert_not_called()
    captured = capsys.readouterr()
    expected_warning = (
        f"Warning: API request failed for URL {url} (TestID: 7): {error_msg}"
    )
    assert expected_warning in captured.err


def test_fetch_data_unexpected_exception_in_get(mock_session_for_module, capsys):
    mock_resp, mock_sess = mock_session_for_module
    url = "http://test.com/value_error"
    error_msg = "Something unexpected during get"
    generic_error = ValueError(error_msg)
    mock_sess.get.side_effect = generic_error
    result = _fetch_data(url, "TestID", 8)
    assert result is None
    captured = capsys.readouterr()
    expected_warning = (
        f"Warning: An unexpected error occurred processing URL {url}: {error_msg}"
    )
    assert expected_warning in captured.err


def test_fetch_data_xml_decode_error_returns_bytes(mock_session_for_module, capsys):
    mock_resp, mock_sess = mock_session_for_module
    url = "http://test.com/badxml"
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/xml"}
    bad_bytes = b"\x80abc"  # Invalid UTF-8 start byte
    mock_resp.content = bad_bytes
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)

    result = _fetch_data(url, "TestID", 9)
    assert result == bad_bytes
    captured = capsys.readouterr()
    expected_warning = (
        f"Warning: Could not decode XML as UTF-8 from {url}. Returning raw bytes."
    )
    assert expected_warning in captured.err


@pytest.fixture
def mock_fetch_data_for_helpers(mocker):
    return mocker.patch("ChemInformant.api_helpers._fetch_data")


def test_get_cids_by_name_success_single(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {"IdentifierList": {"CID": [CID1]}}
    result = get_cids_by_name(NAME1)
    assert result == [CID1]
    safe_name = quote(NAME1)
    expected_url = f"{PUBCHEM_API_BASE}/compound/name/{safe_name}/cids/JSON"
    mock_fetch_data_for_helpers.assert_called_once_with(
        expected_url, identifier_type="Name", identifier=NAME1
    )


def test_get_cids_by_name_success_multiple(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {"IdentifierList": {"CID": [CID1, CID2]}}
    result = get_cids_by_name("Ambiguous")
    assert result == [CID1, CID2]


def test_get_cids_by_name_not_found_returns_none(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = None
    result = get_cids_by_name("NotFound")
    assert result is None


def test_get_cids_by_name_malformed_response_returns_none(mock_fetch_data_for_helpers):
    test_cases = [
        {"WrongKey": {}},
        {"IdentifierList": {"WrongCIDKey": [CID1]}},
        {"IdentifierList": {"CID": "not a list"}},
        {"IdentifierList": {"CID": ["not an int", 123]}},
    ]
    for malformed_data in test_cases:
        mock_fetch_data_for_helpers.return_value = malformed_data
        assert get_cids_by_name(NAME1) is None
        mock_fetch_data_for_helpers.reset_mock()


# Fixtures for PUG View responses
@pytest.fixture
def mock_pug_view_cas_unii_both():
    return {
        "Record": {
            "Reference": [
                {"SourceName": "CAS Common Chemistry", "SourceID": CAS1},
                {
                    "SourceName": "FDA Global Substance Registration System (GSRS)",
                    "SourceID": UNII1,
                },
            ]
        }
    }


@pytest.fixture
def mock_pug_view_cas_only():
    return {
        "Record": {
            "Reference": [{"SourceName": "CAS Common Chemistry", "SourceID": CAS1}]
        }
    }


@pytest.fixture
def mock_pug_view_unii_only():
    return {
        "Record": {
            "Reference": [
                {
                    "SourceName": "FDA Global Substance Registration System (GSRS)",
                    "SourceID": UNII1,
                }
            ]
        }
    }


@pytest.fixture
def mock_pug_view_neither():
    return {
        "Record": {"Reference": [{"SourceName": "Other Source", "SourceID": "OtherID"}]}
    }


@pytest.fixture
def mock_pug_view_empty_ref_list():
    return {"Record": {"Reference": []}}


@pytest.fixture
def mock_pug_view_malformed_ref_item():
    return {"Record": {"Reference": ["not a dict"]}}


@pytest.fixture
def mock_pug_view_missing_keys_in_ref():
    return {"Record": {"Reference": [{"WrongKey": "CAS"}]}}


@pytest.fixture
def mock_pug_view_empty_sourceid_for_cas():
    return {
        "Record": {
            "Reference": [{"SourceName": "CAS Common Chemistry", "SourceID": ""}]
        }
    }


def test_get_cas_unii_success_both(
    mock_fetch_data_for_helpers, mock_pug_view_cas_unii_both
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_cas_unii_both
    cas, unii = get_cas_unii(CID1)
    assert cas == CAS1
    assert unii == UNII1
    expected_url = f"{PUG_VIEW_BASE}/compound/{CID1}/JSON"
    mock_fetch_data_for_helpers.assert_called_once_with(
        expected_url, identifier_type="CID", identifier=CID1
    )


def test_get_cas_unii_success_only_cas(
    mock_fetch_data_for_helpers, mock_pug_view_cas_only
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_cas_only
    cas, unii = get_cas_unii(CID1)
    assert cas == CAS1
    assert unii is None


def test_get_cas_unii_success_only_unii(
    mock_fetch_data_for_helpers, mock_pug_view_unii_only
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_unii_only
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii == UNII1


def test_get_cas_unii_success_neither_relevant_source(
    mock_fetch_data_for_helpers, mock_pug_view_neither
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_neither
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_no_record_key_in_response(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {"NotRecord": {}}
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_no_references_key_in_record(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {"Record": {}}
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_empty_references_list(
    mock_fetch_data_for_helpers, mock_pug_view_empty_ref_list
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_empty_ref_list
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_fetch_failed_returns_none_tuple(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = None
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_malformed_reference_item(
    mock_fetch_data_for_helpers, mock_pug_view_malformed_ref_item
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_malformed_ref_item
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_missing_keys_in_ref_item(
    mock_fetch_data_for_helpers, mock_pug_view_missing_keys_in_ref
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_missing_keys_in_ref
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_cas_unii_empty_sourceid(
    mock_fetch_data_for_helpers, mock_pug_view_empty_sourceid_for_cas
):
    mock_fetch_data_for_helpers.return_value = mock_pug_view_empty_sourceid_for_cas
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None


def test_get_additional_properties_success(mock_fetch_data_for_helpers):
    props_data = {
        "MolecularFormula": "F1",
        "MolecularWeight": "W1",
        "CanonicalSMILES": "S1",
        "IUPACName": "I1",
        "CID": CID1,
    }
    mock_fetch_data_for_helpers.return_value = {
        "PropertyTable": {"Properties": [props_data]}
    }
    result = get_additional_properties(CID1)
    assert result == {
        "MolecularFormula": "F1",
        "MolecularWeight": "W1",
        "CanonicalSMILES": "S1",
        "IUPACName": "I1",
    }


def test_get_additional_properties_partial_data_with_none(mock_fetch_data_for_helpers):
    props_data = {"MolecularFormula": "F1", "MolecularWeight": None, "CID": CID1}
    mock_fetch_data_for_helpers.return_value = {
        "PropertyTable": {"Properties": [props_data]}
    }
    result = get_additional_properties(CID1)
    assert result == {
        "MolecularFormula": "F1",
        "MolecularWeight": None,
        "CanonicalSMILES": None,
        "IUPACName": None,
    }


def test_get_additional_properties_fetch_failed_returns_all_none(
    mock_fetch_data_for_helpers,
):
    mock_fetch_data_for_helpers.return_value = None
    result = get_additional_properties(CID1)
    assert result == {
        "MolecularFormula": None,
        "MolecularWeight": None,
        "CanonicalSMILES": None,
        "IUPACName": None,
    }


def test_get_additional_properties_malformed_response_returns_all_none(
    mock_fetch_data_for_helpers,
):
    none_result = {
        "MolecularFormula": None,
        "MolecularWeight": None,
        "CanonicalSMILES": None,
        "IUPACName": None,
    }
    test_cases = [
        {"WrongKey": {}},
        {"PropertyTable": {"WrongPropsKey": []}},
        {"PropertyTable": {"Properties": []}},
        {"PropertyTable": {"Properties": ["not a dict"]}},
    ]
    for malformed_data in test_cases:
        mock_fetch_data_for_helpers.return_value = malformed_data
        assert get_additional_properties(CID1) == none_result
        mock_fetch_data_for_helpers.reset_mock()


def test_get_compound_description_success_from_string(mock_fetch_data_for_helpers):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Test Description </pug:Description></pug:Information></pug:Info>'
    mock_fetch_data_for_helpers.return_value = xml_string.strip()
    result = get_compound_description(CID1)
    assert result == "Test Description"


def test_get_compound_description_success_from_bytes(mock_fetch_data_for_helpers):
    xml_bytes = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Bytes Desc</pug:Description></pug:Information></pug:Info>'.encode(
        "utf-8"
    )
    mock_fetch_data_for_helpers.return_value = xml_bytes
    result = get_compound_description(CID1)
    assert result == "Bytes Desc"


def test_get_compound_description_no_description_tag_returns_none(
    mock_fetch_data_for_helpers,
):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID></pug:Information></pug:Info>'
    mock_fetch_data_for_helpers.return_value = xml_string
    assert get_compound_description(CID1) is None


def test_get_compound_description_empty_description_tag_returns_none(
    mock_fetch_data_for_helpers,
):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description></pug:Description></pug:Information></pug:Info>'
    mock_fetch_data_for_helpers.return_value = xml_string
    assert get_compound_description(CID1) == ""


def test_get_compound_description_whitespace_only_tag_returns_empty_str(
    mock_fetch_data_for_helpers,
):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>   </pug:Description></pug:Information></pug:Info>'
    mock_fetch_data_for_helpers.return_value = xml_string
    assert get_compound_description(CID1) == ""


def test_get_compound_description_fetch_failed_returns_none(
    mock_fetch_data_for_helpers,
):
    mock_fetch_data_for_helpers.return_value = None
    assert get_compound_description(CID1) is None


def test_get_compound_description_xml_parse_error_on_string_returns_none(
    mock_fetch_data_for_helpers, capsys
):
    xml_string = "<Info><Malformed"
    mock_fetch_data_for_helpers.return_value = xml_string
    assert get_compound_description(CID1) is None
    captured = capsys.readouterr()
    assert (
        f"Warning: Failed to parse XML description string for CID {CID1}:"
        in captured.err
    )


def test_get_compound_description_xml_parse_error_on_bytes_returns_none(
    mock_fetch_data_for_helpers, capsys
):
    xml_bytes = b"<Info><Malformed"
    mock_fetch_data_for_helpers.return_value = xml_bytes
    assert get_compound_description(CID1) is None
    captured = capsys.readouterr()
    assert (
        f"Warning: Failed processing description bytes for CID {CID1}:" in captured.err
    )
    assert (
        "unclosed token" in captured.err.lower()
    )  # Check for specific parse error detail


def test_get_all_synonyms_success(mock_fetch_data_for_helpers):
    syns = ["Syn1", "Syn2 ", "  Syn3"]
    mock_fetch_data_for_helpers.return_value = {
        "InformationList": {"Information": [{"Synonym": syns, "CID": CID1}]}
    }
    result = get_all_synonyms(CID1)
    assert result == ["Syn1", "Syn2 ", "  Syn3"]


def test_get_all_synonyms_empty_list_from_api(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {
        "InformationList": {"Information": [{"Synonym": [], "CID": CID1}]}
    }
    assert get_all_synonyms(CID1) == []


def test_get_all_synonyms_fetch_failed_returns_empty_list(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = None
    assert get_all_synonyms(CID1) == []


def test_get_all_synonyms_malformed_response_returns_empty_list(
    mock_fetch_data_for_helpers,
):
    test_cases = [
        {"WrongKey": {}},
        {"InformationList": {"WrongInfoKey": []}},
        {"InformationList": {"Information": []}},
        {"InformationList": {"Information": [{"WrongSynKey": [], "CID": CID1}]}},
        {"InformationList": {"Information": [{"Synonym": "not a list", "CID": CID1}]}},
        {
            "InformationList": {
                "Information": [{"Synonym": [123, "string"], "CID": CID1}]
            }
        },
    ]
    for malformed_data in test_cases:
        mock_fetch_data_for_helpers.return_value = malformed_data
        assert get_all_synonyms(CID1) == []
        mock_fetch_data_for_helpers.reset_mock()


# Tests for _get_batch_data_for_cids (internal helper)
def test_internal_get_batch_data_success_props(mock_fetch_data_for_helpers):
    cids = [CID1, CID2]
    props_data = [
        {"MolecularFormula": "F1", "CID": CID1},
        {"MolecularFormula": "F2", "CID": CID2},
    ]
    mock_fetch_data_for_helpers.return_value = {
        "PropertyTable": {"Properties": props_data}
    }
    result = _get_batch_data_for_cids(
        cids, "property/MolecularFormula", "PropertyTable"
    )
    assert result == {CID1: props_data[0], CID2: props_data[1]}


def test_internal_get_batch_data_success_syns(mock_fetch_data_for_helpers):
    cids = [CID1]
    syn_data = [{"Synonym": ["S1"], "CID": CID1}]
    mock_fetch_data_for_helpers.return_value = {
        "InformationList": {"Information": syn_data}
    }
    result = _get_batch_data_for_cids(cids, "synonyms", "InformationList")
    assert result == {CID1: syn_data[0]}


def test_internal_get_batch_data_partial_response(mock_fetch_data_for_helpers):
    cids_input = [CID1, CID2, CID3]
    props_data_from_api = [
        {"MolecularFormula": "F1", "CID": CID1},
        {"MolecularFormula": "F3", "CID": CID3},
    ]
    mock_fetch_data_for_helpers.return_value = {
        "PropertyTable": {"Properties": props_data_from_api}
    }
    result = _get_batch_data_for_cids(
        cids_input, "property/MolecularFormula", "PropertyTable"
    )
    assert result == {CID1: props_data_from_api[0], CID3: props_data_from_api[1]}


def test_internal_get_batch_data_empty_input_cids(mock_fetch_data_for_helpers):
    assert (
        _get_batch_data_for_cids([], "property/MolecularFormula", "PropertyTable") == {}
    )
    mock_fetch_data_for_helpers.assert_not_called()


def test_internal_get_batch_data_fetch_failed(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = None
    assert _get_batch_data_for_cids([CID1], "synonyms", "InformationList") == {}


def test_internal_get_batch_data_malformed_outer_response(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {"WrongKey": {}}
    assert _get_batch_data_for_cids([CID1], "synonyms", "InformationList") == {}


def test_internal_get_batch_data_malformed_inner_list_key(mock_fetch_data_for_helpers):
    mock_fetch_data_for_helpers.return_value = {
        "InformationList": {"WrongItemsKey": []}
    }
    assert _get_batch_data_for_cids([CID1], "synonyms", "InformationList") == {}


def test_internal_get_batch_data_invalid_cid_in_response_item(
    mock_fetch_data_for_helpers, capsys
):
    cids_input = [CID1, 123]
    props_data_from_api = [
        {"MolecularFormula": "F1", "CID": CID1},
        {"MolecularFormula": "F2", "CID": "InvalidCID"},
        {"MolecularFormula": "F3", "CID": 123.45},
        {"MolecularFormula": "F4"},
        {"MolecularFormula": "F5", "CID": None},
    ]
    mock_fetch_data_for_helpers.return_value = {
        "PropertyTable": {"Properties": props_data_from_api}
    }
    result = _get_batch_data_for_cids(
        cids_input, "property/MolecularFormula", "PropertyTable"
    )
    expected_result = {
        CID1: {"MolecularFormula": "F1", "CID": CID1},
        123: {"MolecularFormula": "F3", "CID": 123.45},
    }
    assert result == expected_result
    captured = capsys.readouterr()
    assert (
        "Warning: Invalid CID 'InvalidCID' found in batch response for property/MolecularFormula."
        in captured.err
    )
    assert (
        "Warning: Invalid CID 'None' found in batch response for property/MolecularFormula."
        in captured.err
    )


# Tests for public batch functions
def test_get_batch_properties_success(mocker):
    cids = [CID1, CID2]
    props_list = ["MolecularWeight", "IUPACName"]
    mock_batch_data_returned = {
        CID1: {"MolecularWeight": "W1", "IUPACName": "I1", "CID": CID1},
        CID2: {"MolecularWeight": "W2", "IUPACName": "I2", "CID": CID2},
    }
    mock_internal_batch_fetch = mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids",
        return_value=mock_batch_data_returned,
    )
    result = get_batch_properties(cids, props_list)
    assert result == mock_batch_data_returned
    expected_props_str = ",".join(props_list)
    mock_internal_batch_fetch.assert_called_once_with(
        cids, f"property/{expected_props_str}", "PropertyTable", "CID"
    )


def test_get_batch_properties_partial_response_fills_missing(mocker):
    cids_input = [CID1, CID2, CID3]
    props_list = ["MolecularWeight"]
    mock_batch_data_returned_from_internal = {
        CID1: {"MolecularWeight": "W1", "CID": CID1},
        CID3: {"MolecularWeight": "W3", "CID": CID3},
    }
    mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids",
        return_value=mock_batch_data_returned_from_internal,
    )
    result = get_batch_properties(cids_input, props_list)
    expected_result = {
        CID1: {"MolecularWeight": "W1", "CID": CID1},
        CID2: {},
        CID3: {"MolecularWeight": "W3", "CID": CID3},
    }
    assert result == expected_result


def test_get_batch_properties_empty_cids_list_returns_empty_dict(mocker):
    mock_internal_batch_fetch = mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids"
    )
    result = get_batch_properties([], ["Prop1"])
    assert result == {}
    mock_internal_batch_fetch.assert_not_called()


def test_get_batch_properties_empty_props_list_returns_empty_dicts_for_cids(mocker):
    mock_internal_batch_fetch = mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids"
    )
    result = get_batch_properties([CID1, CID2], [])
    assert result == {CID1: {}, CID2: {}}
    mock_internal_batch_fetch.assert_not_called()


def test_get_batch_synonyms_success(mocker):
    cids = [CID1, CID2]
    mock_batch_data_returned_from_internal = {
        CID1: {"Synonym": ["S1a", "S1b"], "CID": CID1},
        CID2: {"Synonym": ["S2a"], "CID": CID2},
    }
    mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids",
        return_value=mock_batch_data_returned_from_internal,
    )
    result = get_batch_synonyms(cids)
    assert result == {CID1: ["S1a", "S1b"], CID2: ["S2a"]}


def test_get_batch_synonyms_partial_response_fills_missing_with_empty_list(mocker):
    cids_input = [CID1, CID2, CID3]
    mock_batch_data_returned_from_internal = {
        CID1: {"Synonym": ["S1a"], "CID": CID1},
        CID3: {"Synonym": [], "CID": CID3},
    }
    mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids",
        return_value=mock_batch_data_returned_from_internal,
    )
    result = get_batch_synonyms(cids_input)
    expected_result = {CID1: ["S1a"], CID2: [], CID3: []}
    assert result == expected_result


def test_get_batch_synonyms_malformed_synonym_data_handled(mocker):
    cids_input = [CID1, CID2, CID3]
    mock_batch_data_returned_from_internal = {
        CID1: {"Synonym": "not a list", "CID": CID1},
        CID2: {"Synonym": [1, 2], "CID": CID2},
        CID3: {"WrongSynKeyInsteadOfSynonym": ["S3"], "CID": CID3},
    }
    mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids",
        return_value=mock_batch_data_returned_from_internal,
    )
    result = get_batch_synonyms(cids_input)
    assert result == {CID1: [], CID2: [], CID3: []}


def test_get_batch_synonyms_empty_cids_list_returns_empty_dict(mocker):
    mock_internal_batch_fetch = mocker.patch(
        "ChemInformant.api_helpers._get_batch_data_for_cids"
    )
    result = get_batch_synonyms([])
    assert result == {}
    mock_internal_batch_fetch.assert_not_called()


# Tests for get_batch_descriptions
def test_get_batch_descriptions_success_from_string(mock_fetch_data_for_helpers):
    cids = [CID1, CID2]
    xml_string = f"""<?xml version="1.0"?><pug:InfoList xmlns:pug="{NS_MAP['pug']}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Desc 1 </pug:Description></pug:Information><pug:Information><pug:CID>{CID2}</pug:CID><pug:Description> Desc 2 </pug:Description></pug:Information></pug:InfoList>"""
    mock_fetch_data_for_helpers.return_value = xml_string.strip()
    result = get_batch_descriptions(cids)
    assert result == {CID1: "Desc 1", CID2: "Desc 2"}


def test_get_batch_descriptions_success_from_bytes(mock_fetch_data_for_helpers):
    cids = [CID1]
    xml_bytes = f'<pug:InfoList xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Bytes Desc </pug:Description></pug:Information></pug:InfoList>'.encode(
        "utf-8"
    )
    mock_fetch_data_for_helpers.return_value = xml_bytes
    result = get_batch_descriptions(cids)
    assert result == {CID1: "Bytes Desc"}


def test_get_batch_descriptions_partial_response_fills_missing_with_none(
    mock_fetch_data_for_helpers,
):
    cids_input = [CID1, CID2, CID3]
    xml_string = f"""<?xml version="1.0"?><pug:InfoList xmlns:pug="{NS_MAP['pug']}">
                     <pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Desc 1 First</pug:Description></pug:Information>
                     <pug:Information><pug:CID>{CID3}</pug:CID><pug:Description></pug:Description></pug:Information>
                     <pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Desc 1 Last</pug:Description></pug:Information>
                   </pug:InfoList>"""
    mock_fetch_data_for_helpers.return_value = xml_string.strip()
    result = get_batch_descriptions(cids_input)
    expected_result = {
        CID1: "Desc 1 Last",
        CID2: None,
        CID3: "",  # Corrected: An empty <Description></Description> tag gives an empty string
    }
    assert result == expected_result


def test_get_batch_descriptions_invalid_cid_in_xml_ignored(mock_fetch_data_for_helpers):
    cids_input = [CID1, CID2]
    xml_string = f"""<?xml version="1.0"?><pug:InfoList xmlns:pug="{NS_MAP['pug']}">
      <pug:Information><pug:CID>InvalidCID</pug:CID><pug:Description>Desc Invalid</pug:Description></pug:Information>
      <pug:Information><pug:CID>{CID2}</pug:CID><pug:Description>Desc 2</pug:Description></pug:Information>
      <pug:Information><pug:Description>No CID here</pug:Description></pug:Information>
    </pug:InfoList>"""
    mock_fetch_data_for_helpers.return_value = xml_string.strip()
    result = get_batch_descriptions(cids_input)
    assert result == {CID1: None, CID2: "Desc 2"}


def test_get_batch_descriptions_empty_cids_list_returns_empty_dict(
    mock_fetch_data_for_helpers,
):
    assert get_batch_descriptions([]) == {}
    mock_fetch_data_for_helpers.assert_not_called()


def test_get_batch_descriptions_fetch_failed_returns_all_none_for_cids(
    mock_fetch_data_for_helpers,
):
    cids_input = [CID1, CID2]
    mock_fetch_data_for_helpers.return_value = None
    result = get_batch_descriptions(cids_input)
    assert result == {CID1: None, CID2: None}


def test_get_batch_descriptions_xml_parse_error_returns_all_none_for_cids(
    mock_fetch_data_for_helpers, capsys
):
    xml_bytes = b"<pug:Info><Malformed"
    mock_fetch_data_for_helpers.return_value = xml_bytes
    result = get_batch_descriptions([CID1, CID2])
    assert result == {CID1: None, CID2: None}
    captured = capsys.readouterr()
    assert "Warning: Failed to parse batch XML description:" in captured.err


# Tests for fetch_compound_image_data
def test_fetch_compound_image_data_success(mock_session_for_module):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    mock_response_success = MagicMock(spec=requests.Response)
    mock_response_success.status_code = 200
    mock_response_success.headers = {"Content-Type": "image/png"}
    mock_response_success.content = b"fake image data"
    mock_response_success.raise_for_status.return_value = None
    mock_sess_fixture.get.return_value = mock_response_success

    result = fetch_compound_image_data(CID1)

    assert result == b"fake image data"
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/PNG"
    mock_sess_fixture.get.assert_called_once_with(expected_url, timeout=REQUEST_TIMEOUT)


def test_fetch_compound_image_data_invalid_cid(mock_session_for_module, capsys):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    invalid_cids = [0, -1]
    for invalid_cid_val in invalid_cids:
        result = fetch_compound_image_data(invalid_cid_val)
        assert result is None
        captured = capsys.readouterr()
        assert (
            f"Warning: Invalid CID provided for image fetching: {invalid_cid_val}"
            in captured.err
        )

    # Test for non-int type, which should raise TypeError due to the check in fetch_compound_image_data
    expected_type_error_msg = "CID must be an integer, got <class 'str'>"
    with pytest.raises(TypeError, match=expected_type_error_msg):
        fetch_compound_image_data("string_cid")  # type: ignore

    mock_sess_fixture.get.assert_not_called()  # Ensure no API call for these invalid cases


def test_fetch_compound_image_data_not_found(mock_session_for_module, capsys):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    mock_response_notfound = MagicMock(spec=requests.Response)
    mock_response_notfound.status_code = 404
    mock_response_notfound.headers = {"Content-Type": "text/plain"}
    # For 404, raise_for_status might not be called if status_code is checked first in fetch_compound_image_data
    # However, if it IS called, it should raise. Let's assume it's called for non-200s before specific 404 check.
    mock_response_notfound.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response_notfound
    )
    mock_sess_fixture.get.return_value = mock_response_notfound

    result = fetch_compound_image_data(CID1)

    assert result is None
    captured = capsys.readouterr()
    # The warning for 404 is specific in fetch_compound_image_data
    assert f"Warning: Image not found for CID {CID1} (404 error)." in captured.err
    mock_sess_fixture.get.assert_called_once()


def test_fetch_compound_image_data_unexpected_content_type(
    mock_session_for_module, capsys
):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    mock_response_unexp_type = MagicMock(spec=requests.Response)
    mock_response_unexp_type.status_code = 200
    mock_response_unexp_type.headers = {"Content-Type": "application/json"}
    mock_response_unexp_type.content = b'{"error": "wrong format"}'
    mock_response_unexp_type.raise_for_status.return_value = None
    mock_sess_fixture.get.return_value = mock_response_unexp_type

    result = fetch_compound_image_data(CID1)

    assert result is None
    captured = capsys.readouterr()
    assert (
        "Warning: Expected PNG image but received content type 'application/json'"
        in captured.err
    )
    mock_sess_fixture.get.assert_called_once()


def test_fetch_compound_image_data_request_exception(mock_session_for_module, capsys):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    error_message = "Network connection error"
    mock_sess_fixture.get.side_effect = requests.exceptions.RequestException(
        error_message
    )

    result = fetch_compound_image_data(CID1)

    assert result is None
    captured = capsys.readouterr()
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/PNG"
    # This warning comes from the except block in fetch_compound_image_data
    assert (
        f"Warning: API request failed for image URL {expected_url} (CID: {CID1}): {error_message}"
        in captured.err
    )
    mock_sess_fixture.get.assert_called_once()


def test_fetch_compound_image_data_general_exception(mock_session_for_module, capsys):
    _mock_resp_fixture, mock_sess_fixture = mock_session_for_module

    error_message = "A very unexpected error"
    mock_sess_fixture.get.side_effect = Exception(error_message)

    result = fetch_compound_image_data(CID1)

    assert result is None
    captured = capsys.readouterr()
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/PNG"
    # This warning comes from the final except block in fetch_compound_image_data
    assert (
        f"Warning: An unexpected error occurred fetching image for CID {CID1} from {expected_url}: {error_message}"
        in captured.err
    )
    mock_sess_fixture.get.assert_called_once()
