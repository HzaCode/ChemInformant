from __future__ import annotations

import json
import re
import sys
import types

import pytest
import ChemInformant as ci
from ChemInformant import api_helpers as ah
from ChemInformant import cheminfo_api as capi
from ChemInformant import models


# ------------------------------------------------------------------#
# 0. Use in-memory HTTP cache for all tests
@pytest.fixture(autouse=True)
def _mem_cache():
    """Ensure all tests use a fresh, in-memory cache for speed and isolation."""
    ci.setup_cache(backend="memory")


# ------------------------------------------------------------------#
# 1. Fake CachedSession (to isolate tests from network)
class _DummyCtx:
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...


class _Cache:
    def create_key(self, _): return "K"
    def delete(self, _):     ...
    def disabled(self):      return _DummyCtx()


class _Session:
    def __init__(self):
        self.cache = _Cache()

    def get(self, url, timeout=None):
        return _fake_execute_fetch(url)


# ------------------------------------------------------------------#
# 2. Fake HTTP Response Object
class _Resp:
    def __init__(self, status=200, data: dict | None = None,
                 from_cache=False,
                 ctype="application/json"):
        self.status_code = status
        self.from_cache = from_cache
        self.headers = {"Content-Type": ctype}
        self.request = object()
        self._data = data or {}

    def json(self): return self._data
    @property
    def text(self): return json.dumps(self._data)


# ------------------------------------------------------------------#
# 3. Central Network Stub to Intercept API Calls
def _fake_execute_fetch(url: str) -> _Resp:                       # noqa: C901
    """Return canned PubChem-like JSON for the URLs used in tests."""
    # name/smiles → CID
    m = re.search(r"/compound/(name|smiles)/([^/]+)/cids", url)
    if m:
        token = re.sub(
            r"%..", lambda m: bytes.fromhex(m.group()[1:]).decode(), m.group(2)
        )
        mapping = {"aspirin": [2244], "ambiguous": [1, 2], "C1CC1": [999]}
        return _Resp(data={"IdentifierList": {"CID": mapping.get(token, [])}})
    # batch properties with pagination
    if "/property/" in url:
        if "/listkey/" in url:  # second page
            return _Resp(data={"PropertyTable": {"Properties": [
                {"CID": 222, "Foo": "b"}
            ]}})
        first_page = {"PropertyTable": {"Properties": [
            {"CID": 111, "Foo": "a"},
            {"CID": 2244, "MolecularWeight": 180.16,
             "MolecularFormula": "C9H8O4",
             "ConnectivitySMILES": "CC(=O)Oc1ccccc1C(=O)O"},
            {"CID": 999, "MolecularWeight": 46.07,
             "CanonicalSMILES": "C1CC1",
             "MolecularFormula": "C3H6"},
        ]}, "ListKey": "NEXT"}
        return _Resp(data=first_page)
    # CAS lookup
    if "/pug_view/data/compound/" in url:
        return _Resp(data={"Record": {"Section": [{
            "TOCHeading": "Names and Identifiers",
            "Section": [{
                "TOCHeading": "Other Identifiers",
                "Section": [{
                    "TOCHeading": "CAS",
                    "Information": [{
                        "Value": {"StringWithMarkup": [{"String": "50-78-2"}]}
                    }]
                }]
            }]
        }]}})
    # synonyms
    if "/synonyms/" in url:
        return _Resp(data={"InformationList": {"Information": [
            {"Synonym": ["alias1", "alias2"]}
        ]}})
    # default: 503 to exercise retry path
    return _Resp(status=503, from_cache=True)


# ------------------------------------------------------------------#
# 4. Wire stubs into the application using a pytest fixture
@pytest.fixture(autouse=True)
def _wire_net(monkeypatch):
    """Fixture to replace all network functions with fakes for all tests."""
    monkeypatch.setattr(ah, "get_session", lambda: _Session())
    monkeypatch.setattr(ah, "_execute_fetch", _fake_execute_fetch)


# ------------------------------------------------------------------#
# 5. Identifier Resolution Logic Tests
def test_resolve_variants():
    assert capi._resolve_to_single_cid(2244) == 2244
    assert capi._resolve_to_single_cid("2244") == 2244
    assert capi._resolve_to_single_cid("C1CC1") == 999
    with pytest.raises(models.AmbiguousIdentifierError):
        capi._resolve_to_single_cid("ambiguous")
    with pytest.raises(models.NotFoundError):
        capi._resolve_to_single_cid("nothing")


# ------------------------------------------------------------------#
# 6. API Helper Function Tests
def test_helpers_roundtrip():
    assert ah.get_cids_by_name("aspirin") == [2244]
    assert ah.get_cids_by_smiles("C1CC1") == [999]
    props = ah.get_batch_properties([2244, 999], ["MolecularWeight"])
    assert props[2244]["MolecularWeight"] == 180.16
    assert ah.get_cas_for_cid(2244) == "50-78-2"
    assert ah.get_synonyms_for_cid(2244) == ["alias1", "alias2"]


# ------------------------------------------------------------------#
# 7. High-Level Public API Tests
def test_get_properties_and_compound():
    df = ci.get_properties(["aspirin"],
                           ["canonical_smiles", "molecular_formula", "cas"])
    row = df.iloc[0]
    assert row["canonical_smiles"].startswith("CC(=O)O")
    assert row["cas"] == "50-78-2"
    cmpd = ci.get_compound("aspirin")
    assert cmpd.cid == 2244
    assert cmpd.molecular_weight == 180.16


# ------------------------------------------------------------------#
# 8. Network Retry Logic Test
def test_retry_path(monkeypatch):
    """Ensure a 503 error triggers a cache purge and a retry."""
    seq = [_Resp(status=503, from_cache=True),
           _Resp(status=200, data={"ok": True})]
    monkeypatch.setattr(ah, "_execute_fetch", lambda url: seq.pop(0))
    assert ah._fetch_with_ratelimit_and_retry("http://dummy") == {"ok": True}
    assert not seq, "The retry mechanism did not consume all mock responses"


# ------------------------------------------------------------------#
# 9. Plotting Function Smoke Test 
@pytest.fixture
def mock_plotting_libs(monkeypatch):
    """
    Mocks plotting libraries (requests, PIL, matplotlib) to prevent
    ImportError when they are not installed and to avoid actual I/O
    or GUI windows during tests. This is done by injecting fake
    modules into sys.modules before the code under test can import them.
    """
    # Mock `requests.get` to fake downloading an image
    fake_requests = types.SimpleNamespace(
        get=lambda *a, **k: types.SimpleNamespace(content=b"\x89PNG_FAKE_DATA")
    )
    monkeypatch.setitem(sys.modules, "requests", fake_requests)

    # Mock `PIL` (Pillow) to fake image handling, allowing `from PIL import Image`
    fake_image_module = types.SimpleNamespace(open=lambda *a, **k: "FAKE_IMAGE")
    fake_pil_module = types.ModuleType("PIL")
    fake_pil_module.Image = fake_image_module
    monkeypatch.setitem(sys.modules, "PIL", fake_pil_module)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_image_module)

    # Mock `matplotlib.pyplot` to fake plotting and avoid GUI popups
    fake_pyplot = types.SimpleNamespace(
        imshow=lambda *a, **k: None,
        axis=lambda *a, **k: None,
        title=lambda *a, **k: None,
        show=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "matplotlib", types.ModuleType("matplotlib"))
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    # Directly patch the `plt` object in the module under test for robustness
    monkeypatch.setattr(capi, "plt", fake_pyplot, raising=False)


def test_draw_compound_smoke(mock_plotting_libs):
    """
    Tests that draw_compound runs without crashing, using mocked libraries.
    The actual functionality is not tested, only the execution path.
    The `mock_plotting_libs` fixture handles all the complex setup.
    """
    capi.draw_compound("aspirin")
