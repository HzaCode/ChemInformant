from unittest import mock

import pandas as pd
import pytest

from ChemInformant import cheminfo_api
from ChemInformant.constants import ALL_PROPS, CORE_PROPS, THREED_PROPS
from ChemInformant.models import AmbiguousIdentifierError, Compound, NotFoundError


class TestResolveCid:
    def test_resolve_integer_cid(self):
        result = cheminfo_api._resolve_to_single_cid(2519)
        assert result == 2519

    def test_resolve_string_digit_cid(self):
        result = cheminfo_api._resolve_to_single_cid("2519")
        assert result == 2519

    def test_resolve_negative_cid_raises_error(self):
        with pytest.raises(ValueError):
            cheminfo_api._resolve_to_single_cid(-1)

    def test_resolve_zero_cid_raises_error(self):
        with pytest.raises(ValueError):
            cheminfo_api._resolve_to_single_cid(0)

    def test_resolve_name_single_result(self):
        with mock.patch(
            "ChemInformant.api_helpers.get_cids_by_name", return_value=[2519]
        ):
            result = cheminfo_api._resolve_to_single_cid("caffeine")
            assert result == 2519

    def test_resolve_name_multiple_results_raises_ambiguous(self):
        with mock.patch(
            "ChemInformant.api_helpers.get_cids_by_name", return_value=[2519, 2520]
        ):
            with pytest.raises(AmbiguousIdentifierError):
                cheminfo_api._resolve_to_single_cid("ambiguous_name")

    def test_resolve_name_no_results_try_smiles(self):
        with mock.patch(
            "ChemInformant.api_helpers.get_cids_by_name", return_value=None
        ):
            with mock.patch.object(
                cheminfo_api, "_looks_like_smiles", return_value=True
            ):
                with mock.patch(
                    "ChemInformant.api_helpers.get_cids_by_smiles", return_value=[2519]
                ):
                    result = cheminfo_api._resolve_to_single_cid(
                        "CC(=O)OC1=CC=CC=C1C(=O)O"
                    )
                    assert result == 2519

    def test_resolve_smiles_multiple_results_raises_ambiguous(self):
        with mock.patch(
            "ChemInformant.api_helpers.get_cids_by_name", return_value=None
        ):
            with mock.patch.object(
                cheminfo_api, "_looks_like_smiles", return_value=True
            ):
                with mock.patch(
                    "ChemInformant.api_helpers.get_cids_by_smiles",
                    return_value=[2519, 2520],
                ):
                    with pytest.raises(AmbiguousIdentifierError):
                        cheminfo_api._resolve_to_single_cid("CC(=O)OC1=CC=CC=C1C(=O)O")

    def test_resolve_not_found_raises_error(self):
        with mock.patch(
            "ChemInformant.api_helpers.get_cids_by_name", return_value=None
        ):
            with mock.patch.object(
                cheminfo_api, "_looks_like_smiles", return_value=False
            ):
                with pytest.raises(NotFoundError):
                    cheminfo_api._resolve_to_single_cid("unknown_compound")


class TestLooksLikeSmiles:
    def test_simple_smiles(self):
        assert cheminfo_api._looks_like_smiles("C1CCCCC1")
        assert cheminfo_api._looks_like_smiles("C(=O)O")
        assert cheminfo_api._looks_like_smiles("CCBr")

    def test_aromatic_smiles(self):
        assert cheminfo_api._looks_like_smiles("c1ccccc1")
        assert cheminfo_api._looks_like_smiles("c1ccc(O)cc1")

    def test_branched_smiles(self):
        assert cheminfo_api._looks_like_smiles("CC(C)C")
        assert cheminfo_api._looks_like_smiles("C(C)(C)C")

    def test_not_smiles(self):
        assert not cheminfo_api._looks_like_smiles("caffeine")
        assert not cheminfo_api._looks_like_smiles("aspirin")
        assert cheminfo_api._looks_like_smiles("2519")
        assert not cheminfo_api._looks_like_smiles("")

    def test_edge_cases(self):
        assert not cheminfo_api._looks_like_smiles("C")
        assert not cheminfo_api._looks_like_smiles("O")
        assert not cheminfo_api._looks_like_smiles("N")
        assert cheminfo_api._looks_like_smiles("C2")


class TestGetProperties:
    def test_get_properties_empty_inputs(self):
        result = cheminfo_api.get_properties([], [])
        assert result.empty

        result = cheminfo_api.get_properties(["caffeine"], [])
        assert result.empty

    def test_get_properties_unsupported_property_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported properties"):
            cheminfo_api.get_properties(["caffeine"], ["invalid_property"])

    def test_get_properties_success(self):
        mock_batch_data = {2519: {"MolecularWeight": "194.19", "IUPACName": "caffeine"}}

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2519
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                with mock.patch(
                    "ChemInformant.api_helpers.get_cas_for_cid", return_value="58-08-2"
                ):
                    result = cheminfo_api.get_properties(
                        ["caffeine"], ["molecular_weight", "iupac_name", "cas"]
                    )

                    assert len(result) == 1
                    assert result.iloc[0]["input_identifier"] == "caffeine"
                    assert result.iloc[0]["cid"] == "2519"
                    assert result.iloc[0]["status"] == "OK"
                    assert result.iloc[0]["molecular_weight"] == "194.19"
                    assert result.iloc[0]["cas"] == "58-08-2"

    def test_get_properties_with_failure(self):
        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", side_effect=NotFoundError("test")
        ):
            result = cheminfo_api.get_properties(["unknown"], ["molecular_weight"])

            assert len(result) == 1
            assert result.iloc[0]["input_identifier"] == "unknown"
            assert pd.isna(result.iloc[0]["cid"])
            assert result.iloc[0]["status"] == "NotFoundError"
            assert pd.isna(result.iloc[0]["molecular_weight"])

    def test_get_properties_mixed_success_failure(self):
        def mock_resolve(identifier):
            if identifier == "caffeine":
                return 2519
            else:
                raise NotFoundError(identifier)

        mock_batch_data = {2519: {"MolecularWeight": "194.19"}}

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", side_effect=mock_resolve
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                result = cheminfo_api.get_properties(
                    ["caffeine", "unknown"], ["molecular_weight"]
                )

                assert len(result) == 2
                assert result.iloc[0]["status"] == "OK"
                assert result.iloc[1]["status"] == "NotFoundError"

    def test_get_properties_default_core_set(self):
        """Verify: When called without any property parameters, returns core property set."""
        mock_batch_data = {2244: {prop: f"value_{prop}" for prop in CORE_PROPS}}

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2244
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                result = cheminfo_api.get_properties([2244])

                # Check that core properties are included but 3D properties are not
                for prop in CORE_PROPS:
                    assert prop in result.columns
                for prop in THREED_PROPS:
                    assert prop not in result.columns
                assert (
                    len(result.columns) == len(CORE_PROPS) + 3
                )  # +3 for 'input_identifier', 'cid', 'status'

    def test_get_properties_include_3d(self):
        """Verify: `include_3d=True` adds 3D properties."""
        all_props_data = {prop: f"value_{prop}" for prop in CORE_PROPS + THREED_PROPS}
        mock_batch_data = {2244: all_props_data}

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2244
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                result = cheminfo_api.get_properties([2244], include_3d=True)

                for prop in CORE_PROPS:
                    assert prop in result.columns
                for prop in THREED_PROPS:
                    assert prop in result.columns
                assert len(result.columns) == len(CORE_PROPS) + len(THREED_PROPS) + 3

    def test_get_properties_all_properties(self):
        """Verify: `all_properties=True` gets complete property list."""
        all_props_data = {prop: f"value_{prop}" for prop in ALL_PROPS}
        mock_batch_data = {2244: all_props_data}

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2244
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                result = cheminfo_api.get_properties([2244], all_properties=True)

                for prop in ALL_PROPS:
                    assert prop in result.columns
                assert len(result.columns) == len(ALL_PROPS) + 3

    def test_get_properties_custom_list(self):
        """Verify: Using aliases to get custom property list."""
        props = ["tpsa", "charge", "isomeric_smiles"]
        expected_props_camel = ["TPSA", "Charge", "IsomericSMILES"]  # API return format
        expected_props_snake = [
            "tpsa",
            "charge",
            "isomeric_smiles",
        ]  # DataFrame column format
        mock_batch_data = {
            2244: {prop: f"value_{prop}" for prop in expected_props_camel}
        }

        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2244
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value=mock_batch_data,
            ):
                result = cheminfo_api.get_properties([2244], properties=props)

                for prop in expected_props_snake:
                    assert prop in result.columns
                assert (
                    list(result.columns)
                    == ["input_identifier", "cid", "status"] + expected_props_snake
                )

    def test_get_properties_raises_on_unknown_prop(self):
        """Verify: When requesting an invalid property name, raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported properties"):
            cheminfo_api.get_properties([2244], properties=["not_a_real_property"])

    def test_get_properties_raises_on_exclusive_args(self):
        """Verify: When using mutually exclusive parameters, raises ValueError."""
        with pytest.raises(ValueError, match="mutually exclusive"):
            cheminfo_api.get_properties([2244], all_properties=True, include_3d=True)
        with pytest.raises(ValueError, match="mutually exclusive"):
            cheminfo_api.get_properties(
                [2244], all_properties=True, properties=["TPSA"]
            )


class TestGetCompound:
    def test_get_compound_success(self):
        mock_df = pd.DataFrame(
            {
                "input_identifier": ["caffeine"],
                "cid": ["2519"],
                "status": ["OK"],
                "molecular_weight": ["194.19"],
                "cas": ["58-08-2"],
            }
        )

        with mock.patch.object(cheminfo_api, "get_properties", return_value=mock_df):
            result = cheminfo_api.get_compound("caffeine")

            assert isinstance(result, Compound)
            assert result.input_identifier == "caffeine"
            assert result.cid == 2519

    def test_get_compound_failure_raises_error(self):
        mock_df = pd.DataFrame(
            {
                "input_identifier": ["unknown"],
                "cid": [pd.NA],
                "status": ["NotFoundError"],
            }
        )

        with mock.patch.object(cheminfo_api, "get_properties", return_value=mock_df):
            with pytest.raises(RuntimeError, match="Failed to fetch compound"):
                cheminfo_api.get_compound("unknown")

    def test_get_compound_empty_dataframe_raises_error(self):
        mock_df = pd.DataFrame()

        with mock.patch.object(cheminfo_api, "get_properties", return_value=mock_df):
            with pytest.raises(RuntimeError, match="Failed to fetch compound"):
                cheminfo_api.get_compound("unknown")


class TestGetCompounds:
    def test_get_compounds_success(self):
        with mock.patch.object(cheminfo_api, "get_compound") as mock_get_compound:
            mock_compound = Compound(
                input_identifier="caffeine", cid="2519", status="OK"
            )
            mock_get_compound.return_value = mock_compound

            result = cheminfo_api.get_compounds(["caffeine"])

            assert len(result) == 1
            assert result[0] == mock_compound
            mock_get_compound.assert_called_once_with("caffeine")


class TestDrawCompound:
    def test_draw_compound_success(self):
        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2519
        ):
            with mock.patch.object(
                cheminfo_api.api_helpers,
                "get_synonyms_for_cid",
                return_value=["Caffeine"],
            ):
                with mock.patch("requests.get") as mock_get:
                    mock_response = mock.Mock()
                    mock_response.status_code = 200
                    mock_response.content = b"fake_png_data"
                    mock_get.return_value = mock_response

                    with mock.patch("io.BytesIO") as mock_bytesio:
                        mock_bytesio.return_value = mock.Mock()

                        with mock.patch("PIL.Image.open") as mock_image_open:
                            mock_img = mock.Mock()
                            mock_image_open.return_value = mock_img

                            with mock.patch("matplotlib.pyplot.show") as mock_show:
                                with mock.patch("matplotlib.pyplot.imshow"):
                                    with mock.patch("matplotlib.pyplot.axis"):
                                        with mock.patch("matplotlib.pyplot.title"):
                                            with mock.patch("matplotlib.pyplot.figure"):
                                                with mock.patch(
                                                    "matplotlib.pyplot.tight_layout"
                                                ):
                                                    cheminfo_api.draw_compound(
                                                        "caffeine"
                                                    )
                                                    mock_show.assert_called_once()

    def test_draw_compound_image_request_fails(self):
        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2519
        ):
            with mock.patch.object(
                cheminfo_api.api_helpers,
                "get_synonyms_for_cid",
                return_value=["Caffeine"],
            ):
                with mock.patch("requests.get") as mock_get:
                    mock_response = mock.Mock()
                    mock_response.status_code = 404
                    mock_response.content = b"not found"
                    mock_get.return_value = mock_response

                    with mock.patch("builtins.print") as mock_print:
                        result = cheminfo_api.draw_compound("caffeine")
                        assert result is None
                        mock_print.assert_called()


class TestFetchScalar:
    def test_property_with_invalid_type_returns_none(self):
        """Test that properties with invalid types return None."""
        with mock.patch.object(
            cheminfo_api, "_resolve_to_single_cid", return_value=2519
        ):
            with mock.patch(
                "ChemInformant.api_helpers.get_batch_properties",
                return_value={2519: {"MolecularWeight": ["invalid", "list"]}},
            ):
                result = cheminfo_api._fetch_scalar(2519, "molecular_weight")
                assert result is None


class TestGetSynonyms:
    def test_get_synonyms_returns_empty_list_on_not_found(self):
        """Test that get_synonyms returns empty list when compound not found."""
        result = cheminfo_api.get_synonyms("nonexistent")
        assert result == []

    def test_get_synonyms_returns_empty_list_on_ambiguous(self):
        """Test that get_synonyms returns empty list when identifier is ambiguous."""
        result = cheminfo_api.get_synonyms("ambiguous")
        assert result == []


class TestCompoundModel:
    def test_safe_float_handles_invalid_types(self):
        """Test that _safe_float returns None for invalid values."""
        # Test with valid values
        compound = Compound(
            input_identifier="test",
            cid="123",
            status="OK",
            molecular_weight=100.5,
        )
        assert compound.molecular_weight == 100.5

        # Test with None
        compound = Compound(
            input_identifier="test", cid="123", status="OK", molecular_weight=None
        )
        assert compound.molecular_weight is None

        # Test with empty string
        compound = Compound(
            input_identifier="test", cid="123", status="OK", molecular_weight=""
        )
        assert compound.molecular_weight is None

        # Test with invalid string (ValueError)
        compound = Compound(
            input_identifier="test",
            cid="123",
            status="OK",
            molecular_weight="not_a_number",
        )
        assert compound.molecular_weight is None

        # Test with invalid type (TypeError) - using a complex object
        compound = Compound(
            input_identifier="test", cid="123", status="OK", molecular_weight={"key": "value"}
        )
        assert compound.molecular_weight is None