import pytest
import requests
import requests_cache
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch, ANY

from ChemInformant import api_helpers
from ChemInformant.api_helpers import (
    _fetch_data,
    get_cids_by_name,
    get_cas_unii,
    get_additional_properties,
    get_compound_description,
    get_all_synonyms,
    _get_batch_data_for_cids,
    get_batch_properties,
    get_batch_synonyms,
    get_batch_descriptions,
    setup_cache,
    get_session,
    DEFAULT_CACHE_NAME,
    DEFAULT_CACHE_BACKEND,
    DEFAULT_CACHE_EXPIRE_AFTER,
    PUBCHEM_API_BASE,
    PUG_VIEW_BASE,
    REQUEST_TIMEOUT,
    quote
)

CID1 = 2244
CID2 = 702
CID3 = 962
NAME1 = "Aspirin"
NAME2 = "Ethanol"
CAS1 = "50-78-2"
UNII1 = "R16CO5Y76E"
NS_MAP = {'pug': 'http://pubchem.ncbi.nlm.nih.gov/pug_rest'}

@pytest.fixture(autouse=True)
def mock_session(mocker):
    api_helpers._session = None
    mock_sess_instance = MagicMock(spec=requests_cache.CachedSession)
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.json.return_value = {}
    mock_response.text = ""
    mock_response.content = b""
    setattr(mock_response, 'from_cache', False)
    mock_sess_instance.get.return_value = mock_response
    mock_response.raise_for_status.return_value = None
    mocker.patch('requests_cache.CachedSession', return_value=mock_sess_instance)
    mocker.patch('requests.Session', return_value=mock_sess_instance)
    return mock_response, mock_sess_instance

def test_setup_cache_default():
    with patch('requests_cache.CachedSession') as mock_cached_sess:
        api_helpers._session = None
        setup_cache()
        mock_cached_sess.assert_called_once_with(
            cache_name=DEFAULT_CACHE_NAME, backend=DEFAULT_CACHE_BACKEND,
            expire_after=DEFAULT_CACHE_EXPIRE_AFTER, allowable_codes=[200, 404],
            match_headers=False,
        )
        assert api_helpers._session is mock_cached_sess.return_value
    api_helpers._session = None

def test_setup_cache_custom():
    with patch('requests_cache.CachedSession') as mock_cached_sess:
        api_helpers._session = None
        setup_cache(cache_name="custom", backend="memory", expire_after=100, custom_arg="test")
        mock_cached_sess.assert_called_once_with(
            cache_name="custom", backend="memory", expire_after=100,
            allowable_codes=[200, 404], match_headers=False, custom_arg="test"
        )
        assert api_helpers._session is mock_cached_sess.return_value
    api_helpers._session = None

def test_get_session_initializes_default(mock_session):
    mock_resp, mock_sess = mock_session
    api_helpers._session = None
    with patch('ChemInformant.api_helpers.setup_cache') as mock_setup:
        def side_effect_func(*args, **kwargs):
            api_helpers._session = mock_sess
        mock_setup.side_effect = side_effect_func
        session = get_session()
        mock_setup.assert_called_once()
        assert session is mock_sess
    api_helpers._session = None

def test_get_session_returns_existing(mock_session):
    mock_resp, mock_sess = mock_session
    api_helpers._session = mock_sess
    with patch('ChemInformant.api_helpers.setup_cache') as mock_setup:
        session = get_session()
        mock_setup.assert_not_called()
        assert session is mock_sess
    api_helpers._session = None

def test_fetch_data_success_json(mock_session):
    mock_resp, mock_sess = mock_session
    mock_resp.json.return_value = {"key": "value"}
    result = _fetch_data("http://test.com/json", "TestID", 1)
    assert result == {"key": "value"}
    mock_sess.get.assert_called_once_with("http://test.com/json", timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_called_once()

def test_fetch_data_success_xml(mock_session):
    mock_resp, mock_sess = mock_session
    mock_resp.headers = {'Content-Type': 'application/xml'}
    xml_string = "<root><item>Test</item></root>"
    mock_resp.content = xml_string.encode('utf-8')
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/xml", "TestID", 2)
    assert result == xml_string
    mock_sess.get.assert_called_once_with("http://test.com/xml", timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_called_once()

def test_fetch_data_success_text_xml(mock_session):
    mock_resp, mock_sess = mock_session
    mock_resp.headers = {'Content-Type': 'text/xml'}
    xml_string = "<root><item>Test</item></root>"
    mock_resp.content = xml_string.encode('utf-8')
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/textxml", "TestID", 3)
    assert result == xml_string

def test_fetch_data_success_unexpected_content_type(mock_session):
    mock_resp, mock_sess = mock_session
    mock_resp.headers = {'Content-Type': 'text/plain'}
    plain_text = "Plain text response"
    mock_resp.text = plain_text
    mock_resp.content = plain_text.encode('utf-8')
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data("http://test.com/text", "TestID", 4)
    assert result == plain_text
    mock_sess.get.assert_called_once_with("http://test.com/text", timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_called_once()

def test_fetch_data_404_not_found(mock_session):
    mock_resp, mock_sess = mock_session
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Error", response=mock_resp)
    result = _fetch_data("http://test.com/notfound", "TestID", 5)
    assert result is None
    mock_sess.get.assert_called_once_with("http://test.com/notfound", timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_not_called()

def test_fetch_data_other_http_error(mock_session, capsys):
    mock_resp, mock_sess = mock_session
    mock_resp.status_code = 500
    url = "http://test.com/error"
    error_msg = "500 Server Error"
    http_error = requests.exceptions.HTTPError(error_msg, response=mock_resp)
    mock_resp.raise_for_status.side_effect = http_error
    result = _fetch_data(url, "TestID", 6)
    assert result is None
    mock_sess.get.assert_called_once_with(url, timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_called_once()
    captured = capsys.readouterr()
    expected_warning = f"Warning: API request failed for URL {url} (TestID: 6): {error_msg}"
    assert expected_warning in captured.err

def test_fetch_data_request_exception(mock_session, capsys):
    mock_resp, mock_sess = mock_session
    url = "http://test.com/timeout"
    error_msg = "Connection timed out"
    req_error = requests.exceptions.Timeout(error_msg)
    mock_sess.get.side_effect = req_error
    result = _fetch_data(url, "TestID", 7)
    assert result is None
    mock_sess.get.assert_called_once_with(url, timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_not_called()
    captured = capsys.readouterr()
    expected_warning = f"Warning: API request failed for URL {url} (TestID: 7): {error_msg}"
    assert expected_warning in captured.err

def test_fetch_data_unexpected_exception(mock_session, capsys):
    mock_resp, mock_sess = mock_session
    url = "http://test.com/value_error"
    error_msg = "Something unexpected"
    generic_error = ValueError(error_msg)
    mock_sess.get.side_effect = generic_error
    result = _fetch_data(url, "TestID", 8)
    assert result is None
    mock_sess.get.assert_called_once_with(url, timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_not_called()
    captured = capsys.readouterr()
    expected_warning = f"Warning: An unexpected error occurred processing URL {url}: {error_msg}"
    assert expected_warning in captured.err

def test_fetch_data_xml_decode_error(mock_session, capsys):
    mock_resp, mock_sess = mock_session
    url = "http://test.com/badxml"
    mock_resp.status_code = 200
    mock_resp.headers = {'Content-Type': 'application/xml'}
    bad_bytes = b'\x80abc'
    mock_resp.content = bad_bytes
    mock_resp.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    result = _fetch_data(url, "TestID", 9)
    assert result == bad_bytes
    captured = capsys.readouterr()
    expected_warning = f"Warning: Could not decode XML as UTF-8 from {url}. Returning raw bytes."
    assert expected_warning in captured.err
    mock_sess.get.assert_called_once_with(url, timeout=REQUEST_TIMEOUT)
    mock_resp.raise_for_status.assert_called_once()

@pytest.fixture
def mock_fetch(mocker):
    return mocker.patch('ChemInformant.api_helpers._fetch_data')

def test_get_cids_by_name_success_single(mock_fetch):
    mock_fetch.return_value = {"IdentifierList": {"CID": [CID1]}}
    result = get_cids_by_name(NAME1)
    assert result == [CID1]
    safe_name = quote(NAME1)
    expected_url = f"{PUBCHEM_API_BASE}/compound/name/{safe_name}/cids/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="Name", identifier=NAME1)

def test_get_cids_by_name_success_multiple(mock_fetch):
    mock_fetch.return_value = {"IdentifierList": {"CID": [CID1, CID2]}}
    result = get_cids_by_name("Ambiguous")
    assert result == [CID1, CID2]

def test_get_cids_by_name_not_found(mock_fetch):
    mock_fetch.return_value = None
    result = get_cids_by_name("NotFound")
    assert result is None
    safe_name = quote("NotFound")
    expected_url = f"{PUBCHEM_API_BASE}/compound/name/{safe_name}/cids/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="Name", identifier="NotFound")

def test_get_cids_by_name_malformed_response(mock_fetch):
    safe_name = quote(NAME1)
    expected_url = f"{PUBCHEM_API_BASE}/compound/name/{safe_name}/cids/JSON"
    mock_fetch.return_value = {"WrongKey": {}}
    assert get_cids_by_name(NAME1) is None
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"IdentifierList": {"WrongCIDKey": [CID1]}}
    assert get_cids_by_name(NAME1) is None
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"IdentifierList": {"CID": "not a list"}}
    assert get_cids_by_name(NAME1) is None
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"IdentifierList": {"CID": ["not an int"]}}
    assert get_cids_by_name(NAME1) is None

@pytest.fixture
def mock_pug_view_cas_unii_both():
    return {"Record": {"Reference": [{"SourceName": "CAS Common Chemistry", "SourceID": CAS1},{"SourceName": "FDA Global Substance Registration System (GSRS)", "SourceID": UNII1}]}}
@pytest.fixture
def mock_pug_view_cas_only():
     return { "Record": { "Reference": [{"SourceName": "CAS Common Chemistry", "SourceID": CAS1}] } }
@pytest.fixture
def mock_pug_view_unii_only():
     return { "Record": { "Reference": [{"SourceName": "FDA Global Substance Registration System (GSRS)", "SourceID": UNII1}]} }
@pytest.fixture
def mock_pug_view_neither():
     return { "Record": { "Reference": [{"SourceName": "Other Source", "SourceID": "OtherID"}]} }
@pytest.fixture
def mock_pug_view_empty_ref():
     return { "Record": { "Reference": []} }
@pytest.fixture
def mock_pug_view_malformed_ref():
     return { "Record": { "Reference": ["not a dict"]} }
@pytest.fixture
def mock_pug_view_missing_keys():
     return { "Record": { "Reference": [{"WrongKey": "CAS"}]} }
@pytest.fixture
def mock_pug_view_empty_sourceid():
     return { "Record": { "Reference": [{"SourceName": "CAS Common Chemistry", "SourceID": ""}]} }

def test_get_cas_unii_success_both(mock_fetch, mock_pug_view_cas_unii_both):
    mock_fetch.return_value = mock_pug_view_cas_unii_both
    cas, unii = get_cas_unii(CID1)
    assert cas == CAS1
    assert unii == UNII1
    expected_url = f"{PUG_VIEW_BASE}/compound/{CID1}/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="CID", identifier=CID1)

def test_get_cas_unii_success_only_cas(mock_fetch, mock_pug_view_cas_only):
    mock_fetch.return_value = mock_pug_view_cas_only
    cas, unii = get_cas_unii(CID1)
    assert cas == CAS1
    assert unii is None

def test_get_cas_unii_success_only_unii(mock_fetch, mock_pug_view_unii_only):
     mock_fetch.return_value = mock_pug_view_unii_only
     cas, unii = get_cas_unii(CID1)
     assert cas is None
     assert unii == UNII1

def test_get_cas_unii_success_neither(mock_fetch, mock_pug_view_neither):
    mock_fetch.return_value = mock_pug_view_neither
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_no_references_key(mock_fetch):
    mock_fetch.return_value = {"Record": {}}
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_empty_references_list(mock_fetch, mock_pug_view_empty_ref):
    mock_fetch.return_value = mock_pug_view_empty_ref
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_fetch_failed(mock_fetch):
    mock_fetch.return_value = None
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_malformed_reference_item(mock_fetch, mock_pug_view_malformed_ref):
    mock_fetch.return_value = mock_pug_view_malformed_ref
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_missing_keys_in_ref(mock_fetch, mock_pug_view_missing_keys):
    mock_fetch.return_value = mock_pug_view_missing_keys
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_cas_unii_empty_sourceid(mock_fetch, mock_pug_view_empty_sourceid):
    mock_fetch.return_value = mock_pug_view_empty_sourceid
    cas, unii = get_cas_unii(CID1)
    assert cas is None
    assert unii is None

def test_get_additional_properties_success(mock_fetch):
    props_data = {"MolecularFormula": "F1", "MolecularWeight": "W1", "CanonicalSMILES": "S1", "IUPACName": "I1", "CID": CID1}
    mock_fetch.return_value = {"PropertyTable": {"Properties": [props_data]}}
    result = get_additional_properties(CID1)
    assert result == {"MolecularFormula": "F1", "MolecularWeight": "W1", "CanonicalSMILES": "S1", "IUPACName": "I1"}
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="CID", identifier=CID1)

def test_get_additional_properties_partial(mock_fetch):
    props_data = {"MolecularFormula": "F1", "MolecularWeight": None, "CID": CID1}
    mock_fetch.return_value = {"PropertyTable": {"Properties": [props_data]}}
    result = get_additional_properties(CID1)
    assert result == {"MolecularFormula": "F1", "MolecularWeight": None, "CanonicalSMILES": None, "IUPACName": None}
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="CID", identifier=CID1)

def test_get_additional_properties_fetch_failed(mock_fetch):
    mock_fetch.return_value = None
    result = get_additional_properties(CID1)
    assert result == {"MolecularFormula": None, "MolecularWeight": None, "CanonicalSMILES": None, "IUPACName": None}

def test_get_additional_properties_malformed(mock_fetch):
    none_result = {"MolecularFormula": None, "MolecularWeight": None, "CanonicalSMILES": None, "IUPACName": None}
    mock_fetch.return_value = {"WrongKey": {}}
    assert get_additional_properties(CID1) == none_result
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"PropertyTable": {"WrongPropsKey": []}}
    assert get_additional_properties(CID1) == none_result
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"PropertyTable": {"Properties": []}}
    assert get_additional_properties(CID1) == none_result
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"PropertyTable": {"Properties": ["not a dict"]}}
    assert get_additional_properties(CID1) == none_result

def test_get_compound_description_success_string(mock_fetch):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Test Description </pug:Description></pug:Information></pug:Info>'
    mock_fetch.return_value = xml_string.strip()
    result = get_compound_description(CID1)
    assert result == "Test Description"
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/description/XML"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="CID", identifier=CID1)

def test_get_compound_description_success_bytes(mock_fetch):
    xml_bytes = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Bytes Desc</pug:Description></pug:Information></pug:Info>'.encode('utf-8')
    mock_fetch.return_value = xml_bytes
    result = get_compound_description(CID1)
    assert result == "Bytes Desc"

def test_get_compound_description_no_description_tag(mock_fetch):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID></pug:Information></pug:Info>'
    mock_fetch.return_value = xml_string
    result = get_compound_description(CID1)
    assert result is None

def test_get_compound_description_empty_description_tag(mock_fetch):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description></pug:Description></pug:Information></pug:Info>'
    mock_fetch.return_value = xml_string
    result = get_compound_description(CID1)
    assert result is None

def test_get_compound_description_whitespace_description_tag(mock_fetch):
    xml_string = f'<pug:Info xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>   </pug:Description></pug:Information></pug:Info>'
    mock_fetch.return_value = xml_string
    result = get_compound_description(CID1)
    assert result == ""

def test_get_compound_description_fetch_failed(mock_fetch):
    mock_fetch.return_value = None
    result = get_compound_description(CID1)
    assert result is None

def test_get_compound_description_xml_parse_error_string(mock_fetch, capsys):
    xml_string = "<Info><Malformed"
    mock_fetch.return_value = xml_string
    result = get_compound_description(CID1)
    assert result is None
    captured = capsys.readouterr()
    assert f"Warning: Failed to parse XML description string for CID {CID1}:" in captured.err

def test_get_compound_description_xml_parse_error_bytes(mock_fetch, capsys):
    xml_bytes = b"<Info><Malformed"
    mock_fetch.return_value = xml_bytes
    result = get_compound_description(CID1)
    assert result is None
    captured = capsys.readouterr()
    assert f"Warning: Failed processing description bytes for CID {CID1}:" in captured.err

def test_get_all_synonyms_success(mock_fetch):
    syns = ["Syn1", "Syn2 ", "  Syn3"]
    mock_fetch.return_value = {"InformationList": {"Information": [{"Synonym": syns, "CID": CID1}]}}
    result = get_all_synonyms(CID1)
    assert result == ["Syn1", "Syn2 ", "  Syn3"]
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/synonyms/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="CID", identifier=CID1)

def test_get_all_synonyms_empty(mock_fetch):
    mock_fetch.return_value = {"InformationList": {"Information": [{"Synonym": [], "CID": CID1}]}}
    result = get_all_synonyms(CID1)
    assert result == []

def test_get_all_synonyms_fetch_failed(mock_fetch):
    mock_fetch.return_value = None
    result = get_all_synonyms(CID1)
    assert result == []

def test_get_all_synonyms_malformed(mock_fetch):
    mock_fetch.return_value = {"WrongKey": {}}
    assert get_all_synonyms(CID1) == []
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"WrongInfoKey": []}}
    assert get_all_synonyms(CID1) == []
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"Information": []}}
    assert get_all_synonyms(CID1) == []
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"Information": [{"WrongSynKey": [], "CID": CID1}]}}
    assert get_all_synonyms(CID1) == []
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"Information": [{"Synonym": "not a list", "CID": CID1}]}}
    assert get_all_synonyms(CID1) == []
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"Information": [{"Synonym": [1, 2], "CID": CID1}]}}
    assert get_all_synonyms(CID1) == []

def test_get_batch_data_success_props(mock_fetch):
    cids = [CID1, CID2]
    props_data = [{"MolecularFormula": "F1", "CID": CID1}, {"MolecularFormula": "F2", "CID": CID2}]
    mock_fetch.return_value = {"PropertyTable": {"Properties": props_data}}
    result = _get_batch_data_for_cids(cids, "property/MolecularFormula", "PropertyTable")
    assert result == {CID1: props_data[0], CID2: props_data[1]}
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1},{CID2}/property/MolecularFormula/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="Batch CID", identifier=f"property/MolecularFormula for {len(cids)} CIDs")

def test_get_batch_data_success_syns(mock_fetch):
    cids = [CID1]
    syn_data = [{"Synonym": ["S1"], "CID": CID1}]
    mock_fetch.return_value = {"InformationList": {"Information": syn_data}}
    result = _get_batch_data_for_cids(cids, "synonyms", "InformationList")
    assert result == {CID1: syn_data[0]}
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1}/synonyms/JSON"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="Batch CID", identifier=f"synonyms for {len(cids)} CIDs")

def test_get_batch_data_partial(mock_fetch):
    cids = [CID1, CID2, CID3]
    props_data = [{"MolecularFormula": "F1", "CID": CID1}, {"MolecularFormula": "F3", "CID": CID3}]
    mock_fetch.return_value = {"PropertyTable": {"Properties": props_data}}
    result = _get_batch_data_for_cids(cids, "property/MolecularFormula", "PropertyTable")
    assert result == {CID1: props_data[0], CID3: props_data[1]}

def test_get_batch_data_empty_input(mock_fetch):
    result = _get_batch_data_for_cids([], "property/MolecularFormula", "PropertyTable")
    assert result == {}
    mock_fetch.assert_not_called()

def test_get_batch_data_fetch_failed(mock_fetch):
    cids = [CID1]
    mock_fetch.return_value = None
    result = _get_batch_data_for_cids(cids, "synonyms", "InformationList")
    assert result == {}

def test_get_batch_data_malformed_response(mock_fetch):
    cids = [CID1]
    mock_fetch.return_value = {"WrongKey": {}}
    result = _get_batch_data_for_cids(cids, "synonyms", "InformationList")
    assert result == {}
    mock_fetch.reset_mock()
    mock_fetch.return_value = {"InformationList": {"WrongItemsKey": []}}
    result = _get_batch_data_for_cids(cids, "synonyms", "InformationList")
    assert result == {}

def test_get_batch_data_invalid_cid_in_response(mock_fetch, capsys):
    cids = [CID1, CID2]
    props_data = [
        {"MolecularFormula": "F1", "CID": CID1},
        {"MolecularFormula": "F2", "CID": "InvalidCID"},
        {"MolecularFormula": "F3", "CID": 123.45},
        {"MolecularFormula": "F4"},
        {"MolecularFormula": "F5", "CID": None}
    ]
    mock_fetch.return_value = {"PropertyTable": {"Properties": props_data}}
    result = _get_batch_data_for_cids(cids, "property/MolecularFormula", "PropertyTable")
    expected_result = {
        CID1: {"MolecularFormula": "F1", "CID": CID1},
        123: {"MolecularFormula": "F3", "CID": 123.45}
    }
    assert result == expected_result
    captured = capsys.readouterr()
    assert "Warning: Invalid CID 'InvalidCID' found in batch response for property/MolecularFormula." in captured.err

def test_get_batch_properties_success(mocker):
    cids = [CID1, CID2]
    props_list = ["MolecularWeight", "IUPACName"]
    mock_batch_data_returned = { CID1: {"MolecularWeight": "W1", "IUPACName": "I1", "CID": CID1}, CID2: {"MolecularWeight": "W2", "IUPACName": "I2", "CID": CID2}}
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value=mock_batch_data_returned)
    result = get_batch_properties(cids, props_list)
    assert result == { CID1: {"MolecularWeight": "W1", "IUPACName": "I1", "CID": CID1}, CID2: {"MolecularWeight": "W2", "IUPACName": "I2", "CID": CID2}}
    expected_props_str = ",".join(props_list)
    mock_get_batch.assert_called_once_with(cids, f"property/{expected_props_str}", "PropertyTable", "CID")

def test_get_batch_properties_partial_response(mocker):
    cids = [CID1, CID2, CID3]
    props_list = ["MolecularWeight"]
    mock_batch_data_returned = { CID1: {"MolecularWeight": "W1", "CID": CID1}, CID3: {"MolecularWeight": "W3", "CID": CID3}}
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value=mock_batch_data_returned)
    result = get_batch_properties(cids, props_list)
    assert result == { CID1: {"MolecularWeight": "W1", "CID": CID1}, CID2: {}, CID3: {"MolecularWeight": "W3", "CID": CID3}}

def test_get_batch_properties_empty_cids(mocker):
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value={})
    props_list = ["Prop1"]
    result = get_batch_properties([], props_list)
    assert result == {}
    expected_props_str = ",".join(props_list)
    mock_get_batch.assert_called_once_with([], f"property/{expected_props_str}", "PropertyTable", "CID")

def test_get_batch_properties_empty_props(mocker):
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids')
    result = get_batch_properties([CID1], [])
    assert result == {CID1: {}}
    mock_get_batch.assert_not_called()

def test_get_batch_synonyms_success(mocker):
    cids = [CID1, CID2]
    mock_batch_data_returned = { CID1: {"Synonym": [" S1a", "S1b "], "CID": CID1}, CID2: {"Synonym": ["S2a"], "CID": CID2}}
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value=mock_batch_data_returned)
    result = get_batch_synonyms(cids)
    assert result == {CID1: [" S1a", "S1b "], CID2: ["S2a"]}
    mock_get_batch.assert_called_once_with(cids, "synonyms", "InformationList", "CID")

def test_get_batch_synonyms_partial_response(mocker):
    cids = [CID1, CID2, CID3]
    mock_batch_data_returned = { CID1: {"Synonym": ["S1a"], "CID": CID1}, CID3: {"Synonym": [], "CID": CID3}}
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value=mock_batch_data_returned)
    result = get_batch_synonyms(cids)
    assert result == {CID1: ["S1a"], CID2: [], CID3: []}

def test_get_batch_synonyms_malformed_synonym_data(mocker):
    cids = [CID1, CID2, CID3]
    mock_batch_data_returned = { CID1: {"Synonym": "not a list", "CID": CID1}, CID2: {"Synonym": [1, 2], "CID": CID2}, CID3: {"WrongSynKey": ["S3"], "CID": CID3}}
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value=mock_batch_data_returned)
    result = get_batch_synonyms(cids)
    assert result == {CID1: [], CID2: [], CID3: []}

def test_get_batch_synonyms_empty_cids(mocker):
    mock_get_batch = mocker.patch('ChemInformant.api_helpers._get_batch_data_for_cids', return_value={})
    result = get_batch_synonyms([])
    assert result == {}
    mock_get_batch.assert_called_once_with([], "synonyms", "InformationList", "CID")

def test_get_batch_descriptions_success_string(mock_fetch):
    cids = [CID1, CID2]
    xml_string = f"""<?xml version="1.0"?><pug:InfoList xmlns:pug="{NS_MAP['pug']}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Desc 1 </pug:Description></pug:Information><pug:Information><pug:CID>{CID2}</pug:CID><pug:Description> Desc 2 </pug:Description></pug:Information></pug:InfoList>"""
    mock_fetch.return_value = xml_string.strip()
    result = get_batch_descriptions(cids)
    assert result == {CID1: "Desc 1", CID2: "Desc 2"}
    expected_url = f"{PUBCHEM_API_BASE}/compound/cid/{CID1},{CID2}/description/XML"
    mock_fetch.assert_called_once_with(expected_url, identifier_type="Batch CID", identifier=f"description for {len(cids)} CIDs")

def test_get_batch_descriptions_success_bytes(mock_fetch):
    cids = [CID1]
    xml_bytes = f'<pug:InfoList xmlns:pug="{NS_MAP["pug"]}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description> Bytes Desc </pug:Description></pug:Information></pug:InfoList>'.encode('utf-8')
    mock_fetch.return_value = xml_bytes
    result = get_batch_descriptions(cids)
    assert result == {CID1: "Bytes Desc"}

def test_get_batch_descriptions_partial_response(mock_fetch):
    cids = [CID1, CID2, CID3]
    xml_string = f"""<?xml version="1.0"?><pug:InfoList xmlns:pug="{NS_MAP['pug']}"><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Desc 1</pug:Description></pug:Information><pug:Information><pug:CID>{CID3}</pug:CID><pug:Description></pug:Description></pug:Information><pug:Information><pug:CID>{CID1}</pug:CID><pug:Description>Duplicate CID 1</pug:Description></pug:Information></pug:InfoList>"""
    mock_fetch.return_value = xml_string.strip()
    result = get_batch_descriptions(cids)
    assert result == {CID1: "Duplicate CID 1", CID2: None, CID3: None}

def test_get_batch_descriptions_invalid_cid_in_xml(mock_fetch):
    cids = [CID1, CID2]
    xml_string = f"""<?xml version="1.0"?>
    <pug:InfoList xmlns:pug="{NS_MAP['pug']}">
      <pug:Information><pug:CID>InvalidCID</pug:CID><pug:Description>Desc Invalid</pug:Description></pug:Information>
      <pug:Information><pug:CID>{CID2}</pug:CID><pug:Description>Desc 2</pug:Description></pug:Information>
      <pug:Information><pug:Description>No CID here</pug:Description></pug:Information>
    </pug:InfoList>"""
    mock_fetch.return_value = xml_string.strip()
    result = get_batch_descriptions(cids)
    assert result == {CID1: None, CID2: "Desc 2"}

def test_get_batch_descriptions_empty_cids(mock_fetch):
    result = get_batch_descriptions([])
    assert result == {}
    mock_fetch.assert_not_called()

def test_get_batch_descriptions_fetch_failed(mock_fetch):
    cids = [CID1]
    mock_fetch.return_value = None
    result = get_batch_descriptions(cids)
    assert result == {CID1: None}

def test_get_batch_descriptions_xml_parse_error(mock_fetch, capsys):
    cids = [CID1]
    xml_string = "<InfoList><Malformed"
    mock_fetch.return_value = xml_string
    result = get_batch_descriptions(cids)
    assert result == {CID1: None}
    captured = capsys.readouterr()
    assert "Warning: Failed to parse batch XML description:" in captured.err