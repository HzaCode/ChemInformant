from __future__ import annotations

import json
import re
import sys
import types

import pandas as pd
import pytest

import ChemInformant as ci
from ChemInformant import api_helpers as ah
from ChemInformant import cheminfo_api as capi
from ChemInformant import models

# ==============================================================================
# MOCKING INFRASTRUCTURE
# ==============================================================================


@pytest.fixture(autouse=True)
def _mem_cache():
    """Ensure all tests use a fresh, in-memory cache for speed and isolation."""
    ci.setup_cache(backend="memory")


class _DummyCtx:
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...


class _Cache:
    def create_key(self, _):
        return "K"

    def delete(self, _): ...
    def disabled(self):
        return _DummyCtx()


class _Session:
    def __init__(self):
        self.cache = _Cache()

    def get(self, url, timeout=None):
        return _fake_execute_fetch(url)


class _Resp:
    def __init__(
        self,
        status=200,
        data: dict | None = None,
        from_cache=False,
        ctype="application/json",
        content: bytes | None = None,
    ):
        self.status_code, self.from_cache, self.headers, self.request, self._data = (
            status,
            from_cache,
            {"Content-Type": ctype},
            object(),
            data or {},
        )
        self.content = content if content is not None else b""

    def json(self):
        return self._data

    @property
    def text(self):
        return json.dumps(self._data)


def _fake_execute_fetch(url: str) -> _Resp:
    """Enhanced mock API to handle more test cases."""
    # Identifier resolution
    m = re.search(r"/compound/(name|smiles)/([^/]+)/cids", url)
    if m:
        token = re.sub(
            r"%..", lambda m: bytes.fromhex(m.group()[1:]).decode(), m.group(2)
        )
        mapping = {
            "aspirin": [2244],
            "caffeine": [2519],
            "ambiguous": [1, 2],
            "C1CC1": [999],
            "nonexistent": [],
        }
        return _Resp(data={"IdentifierList": {"CID": mapping.get(token, [])}})
    # Batch properties (with pagination logic)
    if "/property/" in url:
        props = url.split("/property/")[1].split("/")[0].split(",")
        if "listkey/PAGINATION_KEY" in url:  # Second page
            return _Resp(
                data={
                    "PropertyTable": {
                        "Properties": [
                            {"CID": 2519, "MolecularWeight": 194.19, "XLogP": -0.07}
                        ]
                    }
                }
            )
        # First page. The 0 / 0.0 entries are deliberate: they cover the
        # regression for issue #1 (truthiness fallback eating legitimate
        # zero values in _fetch_scalar).
        return _Resp(
            data={
                "PropertyTable": {
                    "Properties": [
                        {
                            "CID": 2244,
                            "MolecularWeight": 180.16,
                            "MolecularFormula": "C9H8O4",
                            "CanonicalSMILES": "CC(=O)Oc1ccccc1C(=O)O",
                            "IsomericSMILES": "CC(=O)Oc1ccccc1C(=O)O",
                            "IUPACName": "2-(acetyloxy)benzoic acid",
                            "XLogP": 1.2,
                            "Charge": 0,
                            "AtomStereoCount": 0,
                            "BondStereoCount": 0,
                            "CovalentUnitCount": 1,
                        },
                        {
                            "CID": 999,
                            "MolecularWeight": 46.07,
                            "MolecularFormula": "C3H6",
                            "CanonicalSMILES": "C1CC1",
                            "Charge": 0,
                            "AtomStereoCount": 0,
                            "BondStereoCount": 0,
                        },
                    ]
                },
                "ListKey": "PAGINATION_KEY" if "XLogP" in props else None,
            }
        )
    # CAS lookup
    if "/pug_view/data/compound/" in url:
        cid = int(url.split("/")[-2])
        if cid == 2244:
            return _Resp(
                data={
                    "Record": {
                        "Section": [
                            {
                                "TOCHeading": "Names and Identifiers",
                                "Section": [
                                    {
                                        "TOCHeading": "Other Identifiers",
                                        "Section": [
                                            {
                                                "TOCHeading": "CAS",
                                                "Information": [
                                                    {
                                                        "Value": {
                                                            "StringWithMarkup": [
                                                                {"String": "50-78-2"}
                                                            ]
                                                        }
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ]
                    }
                }
            )
        return _Resp(status=404)
    # Synonyms lookup
    if "/synonyms/" in url:
        return _Resp(
            data={
                "InformationList": {"Information": [{"Synonym": ["alias1", "alias2"]}]}
            }
        )
    # Structure PNG endpoint used by draw_compound
    if url.endswith("/PNG"):
        return _Resp(
            status=200, ctype="image/png", content=b"\x89PNG_FAKE_DATA"
        )
    # Default: 503 to exercise retry path
    return _Resp(status=503, from_cache=True)


@pytest.fixture(autouse=True)
def _wire_net(monkeypatch):
    """Fixture to replace all network functions with fakes for all tests."""
    monkeypatch.setattr(ah, "get_session", lambda: _Session())
    monkeypatch.setattr(ah, "_execute_fetch", _fake_execute_fetch)


@pytest.fixture
def mock_plotting_libs(monkeypatch):
    """Mocks plotting libraries to avoid actual I/O or GUI windows.

    draw_compound() now goes through ``api_helpers.get_session().get(...)`` for
    the PNG endpoint, so the existing session-level patch in ``_wire_net``
    already covers the HTTP call. Only the plotting-layer modules need to be
    faked here.
    """
    fake_image_module = types.SimpleNamespace(open=lambda *a, **k: "FAKE_IMAGE")
    fake_pil_module = types.ModuleType("PIL")
    fake_pil_module.Image = fake_image_module
    monkeypatch.setitem(sys.modules, "PIL", fake_pil_module)
    monkeypatch.setitem(sys.modules, "PIL.Image", fake_image_module)
    fake_pyplot = types.SimpleNamespace(
        figure=lambda *a, **k: None,
        imshow=lambda *a, **k: None,
        axis=lambda *a, **k: None,
        title=lambda *a, **k: None,
        tight_layout=lambda *a, **k: None,
        show=lambda *a, **k: None,
    )
    monkeypatch.setitem(sys.modules, "matplotlib", types.ModuleType("matplotlib"))
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)
    monkeypatch.setattr(capi, "plt", fake_pyplot, raising=False)


# ==============================================================================
# TESTS
# ==============================================================================


def test_resolve_variants():
    """Tests the internal CID resolution logic."""
    assert capi._resolve_to_single_cid(2244) == 2244
    assert capi._resolve_to_single_cid("2244") == 2244
    assert capi._resolve_to_single_cid("C1CC1") == 999
    with pytest.raises(models.AmbiguousIdentifierError):
        capi._resolve_to_single_cid("ambiguous")
    with pytest.raises(models.NotFoundError):
        capi._resolve_to_single_cid("nonexistent")
    with pytest.raises(ValueError):
        capi._resolve_to_single_cid(-10)


def test_cid_column_is_always_string():
    """Ensures the 'cid' column has the correct string dtype."""
    df = ci.get_properties(["aspirin", "nonexistent"], ["molecular_weight"])
    assert pd.api.types.is_string_dtype(df["cid"])
    assert df.loc[df["input_identifier"] == "aspirin", "cid"].iloc[0] == "2244"
    assert pd.isna(df.loc[df["input_identifier"] == "nonexistent", "cid"].iloc[0])


def test_get_properties_rigorous_with_mixed_inputs_and_pagination():
    """A more rigorous test for get_properties, now also testing pagination."""
    identifiers = ["aspirin", "caffeine", "nonexistent"]
    properties = ["molecular_weight", "xlogp"]
    df_actual = ci.get_properties(identifiers, properties)

    expected_data = [
        {
            "input_identifier": "aspirin",
            "cid": "2244",
            "status": "OK",
            "molecular_weight": 180.16,
            "xlogp": 1.2,
        },
        {
            "input_identifier": "caffeine",
            "cid": "2519",
            "status": "OK",
            "molecular_weight": 194.19,
            "xlogp": -0.07,
        },
        {
            "input_identifier": "nonexistent",
            "cid": pd.NA,
            "status": "NotFoundError",
            "molecular_weight": None,
            "xlogp": None,
        },
    ]
    df_expected = pd.DataFrame(expected_data).astype(
        {"cid": "string", "xlogp": "float64"}
    )
    pd.testing.assert_frame_equal(df_actual, df_expected, check_like=True)


def test_get_properties_edge_cases():
    """Tests edge cases for get_properties."""
    assert ci.get_properties([], ["molecular_weight"]).empty
    assert ci.get_properties(["aspirin"], []).empty
    with pytest.raises(ValueError, match="Unsupported properties: .*'invalid_prop'"):
        ci.get_properties(["aspirin"], ["molecular_weight", "invalid_prop"])


def test_convenience_functions():
    """Tests all the scalar convenience functions."""
    assert ci.get_weight("aspirin") == 180.16
    assert ci.get_formula("aspirin") == "C9H8O4"
    assert ci.get_canonical_smiles("aspirin").startswith("CC(=O)O")
    assert ci.get_isomeric_smiles("aspirin").startswith("CC(=O)O")
    assert ci.get_iupac_name("aspirin") == "2-(acetyloxy)benzoic acid"
    assert ci.get_xlogp("aspirin") == 1.2
    assert ci.get_cas("aspirin") == "50-78-2"
    assert ci.get_synonyms("aspirin") == ["alias1", "alias2"]
    assert ci.get_cas("caffeine") is None


def test_convenience_functions_preserve_zero_values():
    """Regression (#1): _fetch_scalar previously used ``or`` as a fallback,
    which silently turned legitimate ``0`` / ``0.0`` values into ``None``.
    For neutral molecules, achiral compounds, single-component compounds
    this would misreport real data as missing."""
    # Neutral molecule -> formal charge must be 0, not None.
    assert ci.get_charge("aspirin") == 0
    assert isinstance(ci.get_charge("aspirin"), int)

    # Achiral -> stereo counts must be 0, not None.
    assert ci.get_atom_stereo_count("aspirin") == 0
    assert ci.get_bond_stereo_count("aspirin") == 0

    # Sanity: non-zero ints still work.
    assert ci.get_covalent_unit_count("aspirin") == 1


def test_convenience_functions_return_none_on_not_found():
    """Tests that convenience functions return None when compound is not found."""
    assert ci.get_weight("nonexistent") is None
    assert ci.get_formula("nonexistent") is None
    assert ci.get_canonical_smiles("nonexistent") is None
    assert ci.get_isomeric_smiles("nonexistent") is None
    assert ci.get_iupac_name("nonexistent") is None
    assert ci.get_xlogp("nonexistent") is None
    assert ci.get_cas("nonexistent") is None
    assert ci.get_exact_mass("nonexistent") is None
    assert ci.get_monoisotopic_mass("nonexistent") is None
    assert ci.get_tpsa("nonexistent") is None
    assert ci.get_complexity("nonexistent") is None
    assert ci.get_h_bond_donor_count("nonexistent") is None
    assert ci.get_h_bond_acceptor_count("nonexistent") is None
    assert ci.get_rotatable_bond_count("nonexistent") is None
    assert ci.get_heavy_atom_count("nonexistent") is None
    assert ci.get_charge("nonexistent") is None
    assert ci.get_atom_stereo_count("nonexistent") is None
    assert ci.get_bond_stereo_count("nonexistent") is None
    assert ci.get_covalent_unit_count("nonexistent") is None
    assert ci.get_inchi("nonexistent") is None
    assert ci.get_inchi_key("nonexistent") is None


def test_convenience_functions_return_none_on_ambiguous():
    """Tests that convenience functions return None when identifier is ambiguous."""
    assert ci.get_weight("ambiguous") is None
    assert ci.get_formula("ambiguous") is None
    assert ci.get_canonical_smiles("ambiguous") is None
    assert ci.get_isomeric_smiles("ambiguous") is None
    assert ci.get_iupac_name("ambiguous") is None
    assert ci.get_xlogp("ambiguous") is None


def test_get_compound_and_compounds():
    """Tests the Compound object retrieval functions."""
    cmpd = ci.get_compound("aspirin")
    assert isinstance(cmpd, models.Compound)
    assert cmpd.cid == 2244
    assert cmpd.molecular_weight == 180.16
    assert cmpd.pubchem_url.endswith("2244")
    # get_compound() must preserve the original user-facing identifier rather
    # than silently replacing it with the resolved CID string.
    assert cmpd.input_identifier == "aspirin"

    compounds = ci.get_compounds(["aspirin", "caffeine"])
    assert len(compounds) == 2
    assert compounds[0].cid == 2244
    assert compounds[1].cid == 2519


def test_get_compound_typed_exceptions_bubble_up():
    """Regression (#3): typed resolution errors must propagate, not be flattened
    into a RuntimeError. The convenience-layer contract and the docstring both
    advertise NotFoundError / AmbiguousIdentifierError."""
    with pytest.raises(models.NotFoundError):
        ci.get_compound("nonexistent")
    with pytest.raises(models.AmbiguousIdentifierError):
        ci.get_compound("ambiguous")

    # get_compounds() delegates per-identifier and must propagate the same way.
    with pytest.raises(models.NotFoundError):
        ci.get_compounds(["aspirin", "nonexistent"])


def test_draw_compound_paths(mock_plotting_libs, monkeypatch):
    """Tests the different execution paths of the draw_compound function."""
    # Success path: no exception, no error messages.
    ci.draw_compound("aspirin")

    # Identifier not found path still raises NotFoundError.
    with pytest.raises(models.NotFoundError):
        ci.draw_compound("nonexistent")


def test_draw_compound_missing_dependency_raises(monkeypatch):
    """Regression (#4): a missing plotting dependency must raise ImportError
    (so the chemdraw CLI can exit non-zero), not silently print and return."""
    # Force the matplotlib import inside draw_compound to fail.
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", None)
    with pytest.raises(ImportError, match="missing dependency"):
        ci.draw_compound("aspirin")
